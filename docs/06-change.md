# 6. Make your first reviewed change

Edit the private HCL tfvars to express the intended change. You do not edit Terraform state or regenerate configuration on every run.

For this demonstration, update the Runtime, Red Team, and Supply Chain descriptions to nonempty strings, and change Gateway `retry_attempts` from 1 to 2. Preserve names, IDs, examples, workspace, provider selection, model, and group source type.

1. Create a private branch, edit `vulture.tfvars`, and open a PR.
2. Review the Git diff and private Terraform plan. Expect **4 updates, 0 creates, 0 deletes**. Stop if an object is replaced or anything outside the four identities changes.
3. Merge only after required checks pass.
4. Review the new main plan and its checksum. The PR artifact is not applicable.
5. Manually dispatch `apply` for that exact main plan, with `noop_only=false`.
6. Read the objects independently with CLI/API calls and compare descriptions, retry setting, and original identities.
7. Generate a new ordinary plan and require no changes.

The recorded run checks one configuration-changing write in each product, not data-plane behavior. No inference request proves retry behavior here; this guide demonstrates declarative routing configuration ownership.

Changes made through the AIRS console appear as drift during refresh. Refresh does not rewrite your desired tfvars: review whether to restore Git's desired settings or intentionally update Git to adopt the console change.

Next: [deliberate cleanup](07-cleanup.md).
