# 4. Migrate the same state to MinIO

This is a state handoff, not another import. A second active state owning the same remote objects would create competing writers.

Provision a **dedicated** bucket with versioning and scoped credentials. The user needs exact-state read/write, lockfile read/write/delete, and private `plans/` access. It must not delete the state object or access production buckets. [The infrastructure appendix](09-infrastructure.md) explains the prerequisites.

Terraform 1.16.4's remote state persistence resets lineage when migrating into a never-written S3 destination. We reproduced that with local-only probes. Initialize the destination with an **output-only snapshot containing zero managed resources** before migrating. This is backend preparation, not a second import or a fabricated state file. Native migration then preserves the original lineage and identities, incrementing the source serial by one.

Before migrating, test conditional writes and actual Terraform lock contention at a separate disposable probe key. `use_lockfile` relies on the backend's conditional S3 writes. Workflow concurrency is additional scheduling, not the state lock.

Supply backend credentials through `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`; set `AWS_ENDPOINT_URL_S3` to your MinIO endpoint and `AWS_DEFAULT_REGION=us-east-1`. For the live run, the operator retrieved these through the demo Conjur workload identity.

```bash
# Back up the actual adopted local snapshot first.
terraform state pull > .local/before-migration.tfstate
terraform output -json managed_resource_ids > .local/before-identities.json
cp backend.tf.example backend.tf
cp backend.hcl.example backend.hcl
# Edit bucket/key for your dedicated demo backend.
# Before activating backend.tf in this root, prepare the empty destination:
mv backend.tf .local/backend.pending.tf
mkdir -m 700 .local/backend-init
cp .local/backend.pending.tf .local/backend-init/backend.tf
cp backend.hcl .local/backend-init/backend.hcl
printf 'output "backend_initialized" { value = true }\n' > .local/backend-init/main.tf
terraform -chdir=.local/backend-init init -backend-config=backend.hcl
terraform -chdir=.local/backend-init plan -out=initialize.tfplan
# Confirm zero managed resource changes; only an output is introduced.
terraform -chdir=.local/backend-init apply initialize.tfplan
# Retire the initializer so it cannot become another writer.
mv .local/backend-init/backend.tf .local/backend-init/backend.tf.retired
mv .local/backend-init/main.tf .local/backend-init/main.tf.retired
mv .local/backend.pending.tf backend.tf
terraform init -migrate-state -backend-config=backend.hcl
terraform state pull > .local/after-migration.tfstate
terraform output -json managed_resource_ids > .local/after-identities.json
cmp .local/before-identities.json .local/after-identities.json
terraform plan -detailed-exitcode
```

Confirm the destination has zero managed objects before approving migration. Compare lineage, serial, all four addresses and IDs; the ordinary plan must return 0. The recorded native migration preserved lineage and all four IDs; its serial advanced from 2 to 3. A serial increment records a new snapshot, not a new ownership lineage. Do not use `state push` or rewrite lineage to make a comparison pass.

Retire any remaining root-level local state/backup into protected recovery storage. Keep backups private, but use the remote backend for all subsequent operations. Stop local live operations once CI/CD takes ownership.

Next: [configure the private pipeline](05-cicd.md).

The backend behavior is explained by [Terraform remote state persistence](https://github.com/hashicorp/terraform/blob/v1.16.4/internal/states/remote/state.go#L176) and [native migration](https://github.com/hashicorp/terraform/blob/v1.16.4/internal/states/statemgr/migrate.go#L54). The guide uses a validated native sequence instead of forcing a state push.
