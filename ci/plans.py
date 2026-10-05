"""Bind an apply to the reviewed plan, source commit, input set, and private artifact."""
import hashlib
import json
import re
import time


def digest(data):
    return hashlib.sha256(data).hexdigest()


def input_digest(inputs):
    return digest(json.dumps(inputs, sort_keys=True, separators=(',', ':')).encode())


def artifact_digest(manifest):
    """Bind binary/review hashes and every authorization field to the human-reviewed digest."""
    return input_digest({key: value for key, value in manifest.items() if key != 'artifact_sha256'})


def require_trusted_event(settings, event_name, ref, repository, event, applying=False):
    if repository != settings['repository']:
        raise ValueError('Workflow repository differs from configured repository')
    if applying or event_name in ('push', 'workflow_dispatch'):
        if ref != 'refs/heads/main' or event_name not in ('push', 'workflow_dispatch'):
            raise ValueError('Main-branch plans and applies require a main-branch event')
        if applying and event_name != 'workflow_dispatch':
            raise ValueError('Apply requires manual workflow dispatch')
    elif event_name == 'pull_request':
        pr = event['pull_request']
        if pr['head']['repo']['full_name'] != repository or pr['base']['ref'] != 'main':
            raise ValueError('Live PR plans require a trusted branch targeting main')
    else:
        raise ValueError('Unsupported live workflow event')


def summarize(plan, ownership=None, cleanup=False):
    counts = {'create': 0, 'update': 0, 'delete': 0, 'read': 0, 'no-op': 0}
    changes = []
    for item in plan.get('resource_changes', []):
        actions = item['change']['actions']
        if item.get('mode', 'managed') == 'managed' and ownership is not None:
            if item['address'] not in ownership:
                raise ValueError('Plan contains an object outside demonstration ownership')
            before = item['change'].get('before') or {}
            if before.get('id') != ownership[item['address']]:
                raise ValueError('Plan identity differs from adopted demonstration identity')
        if 'delete' in actions:
            if not cleanup or actions != ['delete'] or ownership is None:
                raise ValueError('Deletion/replacement is protected; use reviewed demonstration cleanup')
        elif cleanup and item.get('mode', 'managed') == 'managed' and actions != ['no-op']:
            raise ValueError('Cleanup must contain only deletion of demonstration identities')
        for action in actions:
            counts[action] = counts.get(action, 0) + 1
        if actions != ['no-op']:
            changes.append({'address': item['address'], 'actions': actions})
    outputs = [name for name, change in plan.get('output_changes', {}).items()
               if change['actions'] != ['no-op']]
    if cleanup and (ownership is None or {x['address'] for x in changes if x['actions'] == ['delete']} != set(ownership)):
        raise ValueError('Cleanup must retire exactly the complete demonstration inventory')
    return {'actions': counts, 'changes': changes, 'changed_outputs': outputs,
            'noop': not changes and not outputs}


def validate_artifact(manifest, plan_bytes, reviewed_digest, settings, commit, inputs, authentication, now=None, cleanup=False, review_bytes=None):
    if not re.fullmatch(r'[0-9a-f]{64}', reviewed_digest):
        raise ValueError('Provide the SHA256 shown by the reviewed plan run')
    if artifact_digest(manifest) != reviewed_digest or manifest.get('artifact_sha256') != reviewed_digest:
        raise ValueError('Reviewed artifact checksum does not match the stored manifest')
    if digest(plan_bytes) != manifest['plan_sha256']:
        raise ValueError('Stored plan differs from its reviewed manifest')
    if review_bytes is None or digest(review_bytes) != manifest['review_sha256']:
        raise ValueError('Stored review text differs from its reviewed manifest')
    if manifest['repository'] != settings['repository'] or manifest['ref'] != 'refs/heads/main':
        raise ValueError('Only a plan from this repository main branch can be applied')
    if manifest['event'] not in ('push', 'workflow_dispatch'):
        raise ValueError('PR plans are for review and cannot be applied')
    if manifest['commit'] != commit:
        raise ValueError('Plan commit is stale; create and review a new main plan')
    if manifest.get('cleanup', False) != cleanup:
        raise ValueError('Use the apply operation matching the reviewed plan mode')
    if manifest['execution_sha256'] != execution_digest(inputs, authentication):
        raise ValueError('Inputs or Conjur credentials changed; create and review a new plan')
    age = (time.time() if now is None else now) - manifest['created_at']
    if age < 0 or age > settings['plan_max_age_seconds']:
        raise ValueError('Plan review window expired; create and review a new plan')
    return manifest['summary']


def redact_review(text, secrets):
    """Mask recovered dynamic-field credentials in addition to Terraform's schema masking."""
    forms = set()
    for value in secrets:
        if value:
            forms.add(value)
            forms.add(json.dumps(value, ensure_ascii=False)[1:-1])
            forms.add(json.dumps(value, ensure_ascii=True)[1:-1])
    for value in sorted(forms, key=len, reverse=True):
        text = text.replace(value, '<redacted>')
    return text


def managed_values(values):
    """Flatten observable managed objects, including child modules, without sensitivity metadata."""
    result = {}

    def visit(module):
        for resource in module.get('resources', []):
            if resource['mode'] == 'managed':
                result[resource['address']] = resource['values']
        for child in module.get('child_modules', []):
            visit(child)

    visit(values.get('root_module', {}))
    return result


def require_no_new_drift(reviewed_plan, refresh_plan):
    # Freshness: Compare with what was observed during review, not older backend attributes.
    reviewed = managed_values(reviewed_plan.get('prior_state', {}).get('values', {}))
    # Refresh-only plans contain observations in prior_state; planned_values can be empty.
    current = managed_values(refresh_plan.get('prior_state', {}).get('values', {}))
    changed = sorted(address for address in reviewed.keys() | current.keys()
                     if address not in reviewed or address not in current or reviewed[address] != current[address])
    if changed:
        raise ValueError('Remote state changed since review; create a new plan. Addresses: ' +
                         ', '.join(changed[:20]))


AUTHENTICATION_KEYS = ('PANW_MGMT_CLIENT_ID', 'PANW_MGMT_CLIENT_SECRET', 'PANW_MGMT_TSG_ID',
                       'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY')


def execution_digest(inputs, authentication):
    return input_digest({'inputs': inputs, 'authentication':
                         {name: authentication[name] for name in AUTHENTICATION_KEYS}})


def observed_credentials(plan, bindings):
    """Include old dynamic credentials when generating review text for a rotation."""
    names = {binding['path'][-1].lower() for binding in bindings}
    names.update(('request_headers', 'headers', 'authorization', 'auth_code', 'api_key',
                  'key', 'password', 'client_secret', 'access_token', 'auth_settings',
                  'configurations', 'variables', 'oauth2_auth', 'check_parameters'))
    found = set()

    def visit(value, secret=False):
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, secret or key.lower() in names)
        elif isinstance(value, list):
            for child in value:
                visit(child, secret)
        elif secret and isinstance(value, str) and value:
            found.add(value)

    for resource in plan.get('resource_changes', []):
        visit(resource['change'].get('before'))
        visit(resource['change'].get('after'))
    return found
