# 2. Generate HCL and import ownership

The starting snapshot contains provider configuration, typed identity variables, and four `import` blocks. For example:

```hcl
import {
  to = prisma-airs_runtime_custom_topic.demonstration
  id = var.runtime_topic_id
}
```

`to` is the Terraform address you will manage. `id` identifies the existing remote object. The starting snapshot has no matching resource declarations yet.

```bash
terraform init
terraform plan -generate-config-out=generated.tf -out=.local/import.tfplan
```

Terraform retrieves attributes through the provider and writes local HCL into **a new file**. Generation does not populate persistent state or create variables/tfvars automatically. Review `generated.tf`, including any sensitive values, before committing it.

The real run produced four resource blocks; the complete sanitized output is [generated.tf.txt](../evidence/generated.tf.txt). This plan must read:

```text
Plan: 4 to import, 0 to add, 0 to change, 0 to destroy.
```

If it proposes updates, resolve the mismatch before adoption. Generated HCL is a starting point, not a guarantee: omitted desired-only fields, masked credentials, conflicting attributes, and API normalization can require corrections. Do not use `ignore_changes` to conceal an adoption mismatch.

```bash
terraform show .local/import.tfplan
terraform apply .local/import.tfplan
terraform state list
terraform plan -detailed-exitcode
```

Applying the reviewed import-only plan records ownership in local state without changing the four remote configurations. The final command must return **0**, with no changes. Exit **2** means differences remain; exit **1** means an error.

Keep the import blocks as adoption history. Terraform skips imports for addresses already in state. Retaining these IDs never recovers previously unrecoverable secrets.

Next: [parameterize the generated HCL](03-tfvars.md).
