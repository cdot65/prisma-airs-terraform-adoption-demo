# Adopt existing Prisma AIRS configuration with Terraform

Start with live AIRS objects, generate readable Terraform configuration, import their ownership, then manage their settings through HCL tfvars and reviewed CI/CD.

This demonstration covers four representative objects: an unattached Runtime custom topic, an unused Red Team custom prompt set, an unused Gateway routing configuration, and an empty Supply Chain security group. It does not run inference, assessments, or model scans. Existing Gateway prerequisites are read through discovery rather than managed as resources.

## Start here

You need Terraform **1.16.4**, provider **cdot65/prisma-airs 0.12.0**, AIRS management access to all four products, and an existing Gateway workspace with an active upstream provider. The supplied Linux amd64 installer verifies Terraform's pinned archive digest. Install the same version through your normal method on other platforms.

Follow these chapters in order:

1. [Discover existing objects](docs/01-discover.md)
2. [Generate HCL and import ownership](docs/02-import.md)
3. [Move settings into typed variables and tfvars](docs/03-tfvars.md)
4. [Migrate the same state to MinIO](docs/04-state.md)
5. [Configure Forgejo and Conjur](docs/05-cicd.md)
6. [Make your first reviewed change](docs/06-change.md)
7. [Clean up the demonstration deliberately](docs/07-cleanup.md)

The root on `main` is the **finished parameterized configuration**. The `stage/01-import-blocks` tag is the starting point without resource declarations, so Terraform can generate them. These are snapshots of one evolving project, not independent deployments. Keep the guide open on `main` while following the starting snapshot. Do not create competing states for the same objects.

[Prepare disposable fixtures](docs/08-fixtures.md) only if you need a test environment. Users adopting existing, unmanaged configuration skip that appendix. [Real sanitized run evidence](evidence/README.md) records what this project actually did.

## Files you edit

| File | Purpose |
| --- | --- |
| `imports.tf` | Existing remote identities and their Terraform addresses |
| `ai-*.tf` | Resource ownership, references, and lifecycle protection |
| `variables.tf` | Typed input contracts and helpful validation |
| `terraform.tfvars` locally; `vulture.tfvars` in private Git | Your nonsecret desired settings |
| `outputs.tf` | Adopted identities to compare before and after state migration |
| `backend.tf` / `backend.hcl` | Shared state configuration, introduced during handoff |
| `ci/settings.json` | Pipeline metadata and the four expected ownership identities |
| `.forgejo/workflows/terraform.yaml` | Trusted plans, manual exact-plan apply, deliberate cleanup |

Terraform reads tfvars natively. The pipeline supplies `-var-file=vulture.tfvars`; it does not parse or reconstruct your configuration. Conjur supplies management and backend credentials as environment variables. The JSON pipeline metadata is not Terraform configuration input.

The public repository contains sanitized templates. The companion private Forgejo project contains tenant-specific nonsecret tfvars, backend settings, and ownership metadata. Never commit credentials, raw state, binary plans, or unreviewed generated output. Import cannot recover secrets that an API masks or returns only once.

The existing Vulture production project owns 357 objects separately. This lesson adopts only its four disposable fixtures, with a dedicated bucket, runner, and Conjur identity.

## Check the teaching project

Run these checks without tenant credentials from the finished root:

```bash
terraform fmt -check -recursive
python3 -m unittest discover -s ci/tests
python3 ci/check-docs.py
TF_CLI_CONFIG_FILE="$PWD/ci/registry.tfrc" terraform init -backend=false -lockfile=readonly
terraform validate
```

Live CI/CD runs in the private Forgejo companion. This public repository does not install a GitHub Actions workflow.
