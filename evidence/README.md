# Real Vulture adoption run

Recorded on **2026-10-05**, using Terraform **1.16.4** and Registry provider **0.12.0**. These are real results, with credentials omitted and tenant/resource UUIDs replaced by labeled placeholders. The four uniquely named fixtures were initially unmanaged and prepared through direct APIs; they were never used for inference, assessments, or scans.

The [getting-started guide](../README.md) teaches the workflow. This directory lets you inspect the actual generation, plans, and results behind it.

| Step | Observed result |
| --- | --- |
| Native HCL generation | 4 imports; 0 creates, updates, or destroys |
| Apply saved import-only plan | 4 imported; no remote configuration changes |
| Ordinary post-import plan | Exit 0, no changes |
| Refactor to typed HCL tfvars | All four managed actions unchanged; ownership output persisted separately |
| Ordinary post-refactor plan | Exit 0, no changes |
| Native MinIO migration | Original lineage and four identities preserved; serial 2 → 3 |
| First CI apply | Verified no-op; four adopted objects retained |
| Corrected artifact-binding apply | Verified no-op with manifest, binary, and review bound to the reviewed checksum |
| Four-product update | 4 in-place updates; independent API reads confirmed three descriptions and Gateway retry attempts 1 → 2 |
| Post-update plan | Exit 0, no changes |
| Reviewed cleanup | 4 deletions; final state contains 0 managed objects, serial 7 |
| Independent cleanup reads | Runtime topic absent; Gateway GET returned 404; prompt set archived; security group tombstoned |
| Production isolation | Separate 357-resource state unchanged byte for byte; production Git HEAD and clean tree unchanged |

Inspect [native generation output](generated.tf.txt), [native command excerpts](native-run.txt), the [no-op review](review-4477.txt), [four-update review](review-4480.txt), [post-update no-op review](review-4485.txt), and [four-delete review](review-4487.txt). The review files contain actual saved-plan text, with UUIDs sanitized. The native excerpts explicitly identify omitted output.

[CI runs](ci-runs.json) records all 19 executions with their actual statuses and available plan summaries. [CI results](ci-results.json) preserves result-field subsets, omitting private lineage. Important executions:

| Forgejo run | Purpose | Result |
| --- | --- | --- |
| 4472 → 4474 | Initial main plan → first no-op apply | Success; legacy binary-only digest, superseded during review |
| 4477 → 4478 | Hardened main plan → exact no-op apply | Success |
| 4479 | Trusted PR plan for four updates | Success |
| 4480 → 4484 | Main saved plan → manual four-update apply | Success |
| 4481 | Submit the update as no-op only | Expected refusal |
| 4482 | Submit an altered reviewed checksum | Expected refusal |
| 4483 | Submit an old plan from a stale commit | Expected refusal |
| 4485 | Ordinary plan after updates | Success, no changes |
| 4486 | PR removes four lifecycle protections | Success, no changes |
| 4487 → 4489 | Manual cleanup plan → exact cleanup apply | Success |
| 4490 | Ordinary plan after retirement | Expected ownership refusal, preventing silent recreation |

## Problems encountered and corrected

- The first tfvars refactor changed a Gateway collection's Terraform type. It proposed one representation-only update, so we refused apply and preserved the generated tuple shape. The corrected plan had no managed changes.
- A new Conjur JWT host initially returned 401 because the existing authenticator requires namespace/service-account claim annotations. Adding those annotations to the dedicated host fixed authentication without changing the authenticator.
- Native migration into a never-written S3 destination reset metadata. We reproduced Terraform's behavior with disposable local-only probes, recovered the genuine local snapshot, and validated the [output-only destination initialization sequence](../docs/04-state.md). The corrected native migration preserved lineage and IDs; no state push or metadata fabrication was used.
- An independent Gateway read assumed the wrong response envelope; its `config` field is JSON text. Correcting the reader enabled verification.
- Preliminary Codex review found a missing backend-template acquisition step and an integrity gap in the original binary-only reviewed checksum. Both were corrected before the configuration-changing apply. The reviewed digest now binds authorization metadata and review text as well as the binary plan; offline tampering tests and a new live no-op apply passed.
- Operator command/path and cached-backend errors were corrected before proceeding. Complete successes and failures are recorded in the private Obsidian task ledger.

[receipt.json](receipt.json) records version pins, source/evidence hashes, independent checks, and backend/Conjur isolation results. `python3 ci/check-docs.py` checks links and those hashes. The 24 offline control tests cover authorization, tampering, expiry, input/credential rotation, drift, and exact cleanup scope; only the explicitly recorded guards were exercised live.

This run verifies management-plane adoption and configuration updates. It does not prove model inference, routing resilience, scanning, assessment execution, backup restoration, or installation of Forgejo/MinIO/Conjur on a new cluster. Actual tfvars, state snapshots, binary plans, and bootstrap credentials remain private.
