# Native Terraform adoption: starting snapshot

This snapshot begins with **four import blocks and no resource declarations**. Terraform will retrieve the selected live objects and generate their HCL. It is the first stage of one evolving project; keep the same state throughout the walkthrough.

Follow the [numbered getting-started guide on main](https://github.com/cdot65/prisma-airs-terraform-adoption-demo/blob/main/README.md), starting with discovery. It explains how to supply management credentials through environment variables and record the four discovered identities in an ordinary `terraform.tfvars` file.

Use Terraform **1.16.4** and provider **0.12.0**. On Linux amd64:

```bash
python3 ci/install-terraform.py
export PATH="$PWD/.ci-bin:$PATH"
mkdir -m 700 .local
cp terraform.tfvars.example terraform.tfvars
# Set your four existing unmanaged identities and management environment variables.
terraform init
terraform plan -generate-config-out=generated.tf -out=.local/import.tfplan
```

Review the generated HCL and require **4 imports, 0 creates, 0 updates, 0 destroys** before applying the saved plan. Generation writes configuration; applying the import-only plan records state ownership. Continue through the main guide to parameterize settings, migrate this state, and hand off to CI/CD.

The final resource definitions, backend templates, and pipeline helpers live on `main`. The guide explicitly retrieves them at the appropriate stages. This starting snapshot deliberately cannot pass `terraform validate` before its resource declarations are generated.
