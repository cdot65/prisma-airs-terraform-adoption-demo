# 1. Discover existing objects

The goal is to identify four live objects that no Terraform state already owns. Discovery reads configuration; it does not grant Terraform ownership.

```bash
git clone https://github.com/cdot65/prisma-airs-terraform-adoption-demo.git
cd prisma-airs-terraform-adoption-demo
git switch -c my-adoption stage/01-import-blocks
mkdir -m 700 .local
# Linux amd64 only; other platforms install the pinned version normally.
python3 ci/install-terraform.py
export PATH="$PWD/.ci-bin:$PATH"
```

Select your own tenant explicitly for the CLI. For this recorded demonstration the operator used an isolated tenant registry selecting Vulture, preserving the computer's existing default selection.

```bash
airs cli tenant list
airs cli tenant switch YOUR_TENANT
```

Set `PANW_MGMT_CLIENT_ID`, `PANW_MGMT_CLIENT_SECRET`, and `PANW_MGMT_TSG_ID` in your shell through your approved secret store. The provider reads these environment variables directly. Do not put management credentials in tfvars or paste secrets into command history.

Use the CLI to find names and identities:

```bash
airs cli runtime topics list --all --max 0 --output json
airs cli redteam prompt-sets list --all --max 0
airs cli aigateway workspaces list --plane admin --output json
airs cli aigateway providers list --workspace "$WORKSPACE_ID" --output json
airs cli aigateway configs list --workspace "$WORKSPACE_ID" --output json
airs cli model-security groups list --all --max 0
```

Confirm CLI flags against `--help` for your installed version. Gateway provider listings are paged: check the reported total and request additional pages if needed. The final HCL discovery example refuses a partial page rather than silently choosing from it.

Record the topic ID, prompt-set UUID, routing configuration UUID, and group UUID in `terraform.tfvars`:

```hcl
runtime_topic_id       = "YOUR_EXISTING_TOPIC_ID"
red_team_prompt_set_id = "YOUR_EXISTING_PROMPT_SET_UUID"
gateway_config_id      = "YOUR_EXISTING_CONFIG_UUID"
supply_chain_group_id  = "YOUR_EXISTING_GROUP_UUID"
```

Keep real settings private. Discovery of an identifier is different from adopting it: never import an object already managed by another active Terraform state. The [fixture appendix](08-fixtures.md) supplies four initially unmanaged objects for this demonstration.

Next: [generate configuration and import](02-import.md).
