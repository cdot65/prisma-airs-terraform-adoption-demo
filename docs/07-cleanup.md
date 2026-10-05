# 7. Clean up the demonstration deliberately

Cleanup applies only to the four uniquely identified demonstration objects. Never use this procedure to retire an existing production configuration without its own review.

Normal declarations use `prevent_destroy` and the pipeline rejects deletion/replacement. For deliberate cleanup:

1. Open a private PR removing `prevent_destroy` from exactly the four demo resource blocks. Retain their addresses, import IDs, ownership metadata, and all shared prerequisite references. Ordinary PR/main plans should remain no-op.
2. Review and merge that explicit lifecycle-protection change.
3. Manually dispatch **cleanup-plan** on `main`. It runs native `terraform plan -destroy -var-file=vulture.tfvars` and saves the binary artifact privately.
4. Review exactly four deletions, matching every expected address and adopted UUID. The cleanup gate rejects replacement, updates, extra resources, different identities, and partial inventories.
5. Dispatch **cleanup-apply** for that exact main plan and checksum, with `noop_only=false`.
6. Verify remote lifecycle semantics and zero managed resources in the dedicated state. Retire the execution repo from active changes after successful cleanup.

Runtime topic and Gateway routing configuration deletion remove the active objects. Red Team prompt-set deletion archives the set. Supply Chain deletion tombstones the group. Historical records may remain; an archived/tombstoned object is not an active managed fixture.

The regular pipeline refuses an empty or mismatched adopted state, so it cannot silently recreate fixtures after cleanup. This is intentional. Keep recovery/audit artifacts private and retain the backend/version history for inspection; stopping or removing the demonstration runner is an optional operator decision.

The public teaching root retains normal destruction protection. The private reviewed cleanup commit intentionally removes it only for retiring this isolated run.
