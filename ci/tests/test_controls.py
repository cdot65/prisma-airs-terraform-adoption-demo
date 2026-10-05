import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conjur import environment
from plans import digest, input_digest, require_trusted_event, summarize, validate_artifact, redact_review, require_no_new_drift, execution_digest, observed_credentials


class Controls(unittest.TestCase):
    def setUp(self):
        self.settings = {'repository': 'owner/project', 'plan_max_age_seconds': 3600}
        self.plan = b'saved-plan-with-private-values'
        self.auth = {key: key + '-credential' for key in ('PANW_MGMT_CLIENT_ID', 'PANW_MGMT_CLIENT_SECRET',
                     'PANW_MGMT_TSG_ID', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY')}
        self.inputs = {'product': {'credential': 'private', 'missing': None, 'empty': ''}}
        self.manifest = {'repository': 'owner/project', 'ref': 'refs/heads/main',
                         'event': 'push', 'commit': 'a' * 40, 'created_at': 1000,
                         'plan_sha256': digest(self.plan), 'execution_sha256': execution_digest(self.inputs, self.auth),
                         'summary': {'noop': True}}

    def validate(self, **kwargs):
        return validate_artifact(kwargs.get('manifest', self.manifest), kwargs.get('plan', self.plan),
                                 kwargs.get('sha', digest(self.plan)), self.settings,
                                 kwargs.get('commit', 'a' * 40), kwargs.get('inputs', self.inputs), kwargs.get('authentication', self.auth),
                                 now=kwargs.get('now', 1100))

    def test_fork_live_plan_refused(self):
        event = {'pull_request': {'head': {'repo': {'full_name': 'attacker/fork'}}, 'base': {'ref': 'main'}}}
        with self.assertRaises(ValueError):
            require_trusted_event(self.settings, 'pull_request', 'refs/pull/1/head', 'owner/project', event)

    def test_apply_requires_manual_main_dispatch(self):
        for event, ref in [('push', 'refs/heads/main'), ('workflow_dispatch', 'refs/heads/feature')]:
            with self.assertRaises(ValueError):
                require_trusted_event(self.settings, event, ref, 'owner/project', {}, applying=True)
        require_trusted_event(self.settings, 'workflow_dispatch', 'refs/heads/main', 'owner/project', {}, applying=True)

    def test_review_redacts_raw_and_json_escaped_credentials(self):
        secret = 'secret-with-quote\"and\nnewline'
        text = secret + ' ' + json.dumps(secret) + ' ordinary-settings'
        redacted = redact_review(text, [secret])
        self.assertNotIn(secret, redacted)
        self.assertNotIn(json.dumps(secret)[1:-1], redacted)
        self.assertIn('ordinary-settings', redacted)

    def test_valid_reviewed_artifact(self):
        self.assertTrue(self.validate()['noop'])

    def test_tampered_plan_refused(self):
        with self.assertRaises(ValueError):
            self.validate(plan=b'tampered')

    def test_stale_commit_refused(self):
        with self.assertRaises(ValueError):
            self.validate(commit='b' * 40)

    def test_changed_conjur_input_refused(self):
        with self.assertRaises(ValueError):
            self.validate(inputs={'product': {'credential': 'rotated'}})

    def test_standard_credential_rotation_is_refused(self):
        for key in self.auth:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate(authentication={**self.auth, key: 'rotated'})

    def test_old_dynamic_header_is_redacted_during_rotation(self):
        plan = {'resource_changes': [{'change': {
            'before': {'custom': {'request_headers': {'x-pan-token': 'old-private-token'}}},
            'after': {'custom': {'request_headers': {'x-pan-token': 'new-private-token'}}}}}]}
        values = observed_credentials(plan, [])
        redacted = redact_review('old-private-token -> new-private-token', values)
        self.assertNotIn('private-token', redacted)

    def test_expired_or_future_plan_refused(self):
        for now in [500, 5000]:
            with self.assertRaises(ValueError):
                self.validate(now=now)

    def test_pr_plan_cannot_be_applied(self):
        manifest = {**self.manifest, 'event': 'pull_request'}
        with self.assertRaises(ValueError):
            self.validate(manifest=manifest)

    def test_protected_replacement_refused(self):
        with self.assertRaises(ValueError):
            summarize({'resource_changes': [{'address': 'test.a', 'change': {'actions': ['delete', 'create']}}]})

    def test_already_reviewed_refresh_drift_is_accepted(self):
        resource = {'mode': 'managed', 'address': 'test.existing', 'values': {'last_updated_at': 'reviewed-time'}}
        reviewed = {'prior_state': {'values': {'root_module': {'resources': [resource]}}},
                    'resource_drift': [{'address': 'test.existing', 'change': {'actions': ['update']}}]}
        refreshed = {'prior_state': {'values': {'root_module': {'resources': [resource]}}},
                     'planned_values': {'root_module': {}},
                     'resource_drift': reviewed['resource_drift']}
        require_no_new_drift(reviewed, refreshed)

    def test_change_after_review_is_refused(self):
        resource = {'mode': 'managed', 'address': 'test.existing', 'values': {'setting': 'reviewed'}}
        reviewed = {'prior_state': {'values': {'root_module': {'resources': [resource]}}}}
        refreshed = {'prior_state': {'values': {'root_module': {'resources': [
            {**resource, 'values': {'setting': 'changed'}}]}}}, 'planned_values': {'root_module': {}}}
        with self.assertRaises(ValueError):
            require_no_new_drift(reviewed, refreshed)

    def test_child_module_disappearance_is_refused(self):
        resource = {'mode': 'managed', 'address': 'module.child.test.existing', 'values': {'id': 'private-id'}}
        reviewed = {'prior_state': {'values': {'root_module': {'child_modules': [{'resources': [resource]}]}}}}
        with self.assertRaises(ValueError):
            require_no_new_drift(reviewed, {'prior_state': {'values': {'root_module': {}}},
                                          'planned_values': {'root_module': {}}})

    def test_sensitive_values_never_enter_summary(self):
        result = summarize({'resource_changes': [{'address': 'test.a', 'change': {'actions': ['update'],
                             'before': {'credential': 'private-before'}, 'after': {'credential': 'private-after'}}}]})
        self.assertNotIn('private', json.dumps(result))
        self.assertEqual(result['actions']['update'], 1)

    def test_credentials_are_native_environment_only(self):
        from unittest.mock import patch
        settings = {'conjur_prefix': 'scope', 'expected_tsg_id': 'tenant',
                    's3_endpoint': 'http://minio', 'region': 'us-east-1'}
        values = {'scope/management/tsg-id': 'tenant'}
        with patch.dict('os.environ', {'TF_VAR_gateway_config': 'ambient', 'PANW_MGMT_ENDPOINT': 'wrong',
                                      'AWS_PROFILE': 'wrong'}, clear=True):
            env = environment(settings, lambda key: values.get(key, 'secret'), '/temporary')
        self.assertFalse(any(key.startswith('TF_VAR_') for key in env))
        self.assertNotIn('AWS_PROFILE', env)
        self.assertNotIn('PANW_MGMT_ENDPOINT', env)
        self.assertEqual(env['PANW_MGMT_TSG_ID'], 'tenant')

    def test_wrong_tenant_credentials_are_refused(self):
        with self.assertRaises(ValueError):
            environment({'conjur_prefix': 'p', 'expected_tsg_id': 'tenant'}, lambda _: 'wrong', '/temporary')

    def cleanup_plan(self, identity='fixture-id', actions=None, address='test.fixture'):
        return {'resource_changes': [{'address': address, 'mode': 'managed', 'change': {
            'actions': actions or ['delete'], 'before': {'id': identity}, 'after': None}}]}

    def test_cleanup_requires_explicit_mode_and_exact_identity(self):
        ownership = {'test.fixture': 'fixture-id'}
        self.assertEqual(summarize(self.cleanup_plan(), ownership, cleanup=True)['actions']['delete'], 1)
        for plan, cleanup in [(self.cleanup_plan(), False), (self.cleanup_plan('different'), True),
                              (self.cleanup_plan(address='test.other'), True),
                              (self.cleanup_plan(actions=['delete', 'create']), True),
                              (self.cleanup_plan(actions=['update']), True)]:
            with self.subTest(plan=plan, cleanup=cleanup), self.assertRaises(ValueError):
                summarize(plan, ownership, cleanup=cleanup)

    def test_cleanup_must_include_all_adopted_objects(self):
        with self.assertRaises(ValueError):
            summarize(self.cleanup_plan(), {'test.fixture': 'fixture-id', 'test.second': 'second-id'}, cleanup=True)

    def test_normal_plan_rejects_unowned_or_recreated_objects(self):
        for plan in [self.cleanup_plan(address='test.other', actions=['update']),
                     self.cleanup_plan(identity=None, actions=['create'])]:
            with self.assertRaises(ValueError):
                summarize(plan, {'test.fixture': 'fixture-id'})

    def test_cleanup_artifact_cannot_be_used_as_normal_apply(self):
        with self.assertRaises(ValueError):
            self.validate(manifest={**self.manifest, 'cleanup': True})



if __name__ == '__main__':
    unittest.main()
