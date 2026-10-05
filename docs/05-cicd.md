# 5. Configure Forgejo and Conjur

The public repository teaches the workflow. A **private** Forgejo companion contains tenant-specific nonsecret values and executes live operations. Trust every collaborator with the tenant credentials; a repository-scoped runner is not a sandbox against malicious trusted repository code.

Create the private companion and configure the [dedicated infrastructure](09-infrastructure.md). Copy the CI helpers and Forgejo workflow from this repository. Rename the local input file to `vulture.tfvars` and remove the auto-loaded `terraform.tfvars` copy.

```bash
mv terraform.tfvars vulture.tfvars
cp ci/settings.json.example ci/settings.json
```

Configure expected tenant, private repository, Conjur service/prefix, MinIO endpoint/bucket/key, and the exact four imported address/UUID pairs in `ci/settings.json`. `var_file` names the native HCL file. Commit these nonsecret settings **only in the private repo**, using explicit `.gitignore` exceptions for `vulture.tfvars`, `ci/settings.json`, `backend.tf`, and `backend.hcl`.

The runner retrieves five Conjur variables using its projected Kubernetes JWT: management client ID, management client secret, tenant ID, backend access key, and backend secret. They become `PANW_MGMT_*` and `AWS_*` environment variables. Terraform reads your settings directly through `-var-file=vulture.tfvars`; there is no custom configuration loader or TF_VAR inventory serialization.

Pin the provider lockfile and verify the Terraform archive checksum. The workflow runs offline formatting, validation, and control tests on an ordinary runner. Same-repository trusted PR branches can run live plans on the dedicated runner. Fork PRs receive offline checks only; never approve fork execution on the credential-bearing runner.

Protect `main`: disable direct pushes, apply protection to admins, require the two successful PR contexts, and block stale/rejected reviews. PR plans cannot be applied. A merged commit produces a new main plan.

## First apply

Review the private `review.txt`, source commit, plan ID and SHA256. The first plan must have zero resource/output changes. In **Actions → Terraform → Run workflow**, choose `main`, operation `apply`, enter the reviewed `plan_id`/`reviewed_sha256`, and keep `noop_only=true`.

Apply uses the **saved binary plan**. It checks checksum, source/main commit, exact tfvars bytes and credentials, state identities/lineage/serial, 24-hour review window, and newly observed remote drift. It never silently substitutes a freshly generated plan. Rotate a credential or edit inputs after review and you must create/review a new plan.

State, binary plans, and diagnostics remain in the private backend. The human-readable review masks resolved credentials as well as Terraform-sensitive fields. Workflow logs contain only action metadata and safe results.

Next: [make a reviewed change](06-change.md).
