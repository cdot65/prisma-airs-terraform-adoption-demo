# 3. Move settings into typed variables and tfvars

First adopt what exists, then improve how humans edit it. Terraform generated literal resource values. Refactor them into meaningful resource names, typed variables, and an ordinary HCL tfvars file without changing their Terraform addresses.

The generated Runtime block contains:

```hcl
resource "prisma-airs_runtime_custom_topic" "demonstration" {
  topic_name  = "tf-adoption-demo-20261005"
  description = "Requests to change the demonstration infrastructure settings."
  examples    = ["Rename the demonstration infrastructure project.", "Update the example Terraform configuration settings.", "Change the demonstration environment resource description."]
}
```

The finished `ai-runtime-security.tf` references a typed input:

```hcl
resource "prisma-airs_runtime_custom_topic" "demonstration" {
  topic_name  = var.runtime_topic.name
  description = var.runtime_topic.description
  examples    = var.runtime_topic.examples

  lifecycle {
    prevent_destroy = true
  }
}
```

`variables.tf` declares an object with string name/description and `list(string)` examples. `terraform.tfvars` supplies those values. Keep the entire example list: omitting it during update can clear the remote list.

To use the tested parameterized definitions while keeping your current state and four identity inputs:

```bash
for file in ai-runtime-security.tf ai-red-teaming.tf ai-gateway.tf ai-supply-chain-security.tf variables.tf outputs.tf; do
  git show origin/main:"$file" > "$file"
done
mv generated.tf .local/generated.original.tf
```

Append the four settings objects to your existing `terraform.tfvars`, using the settings actually recovered from your objects. The [sanitized example](../terraform.tfvars.example) illustrates the shape; copying unrelated settings could propose unwanted changes. Do not duplicate resource declarations or replace the discovered IDs.

Gateway provider discovery selects an existing active upstream by its name, then uses the returned slug. You do not supply an upstream integration UUID or import its credentials. This lesson's routing document has only a provider reference, model override, and bounded retries. Preserve any additional routing fields from your own recovered object if you adapt the example to it.

The provider's dynamic routing document distinguishes collection types. The final code converts typed status-code inputs into a tuple with `[for code in ... : code]`, matching the generated document. The first parameterization attempt without this conversion proposed a representation-only update; the corrected real plan has no managed changes. We retained full drift detection.

```bash
terraform fmt
terraform validate
terraform plan -out=.local/parameterize.tfplan
terraform show .local/parameterize.tfplan
```

The new ownership output can require a state-only output update. Confirm all four resource actions are unchanged, then apply that saved plan and run `terraform plan -detailed-exitcode` again; it must return 0.

Commit your resource declarations and typed variables. Public Git gets sanitized `terraform.tfvars.example`; the private execution repo will track the real nonsecret values as `vulture.tfvars`.

Next: [migrate the same state](04-state.md).
