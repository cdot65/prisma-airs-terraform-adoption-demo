# Appendix: dedicated execution infrastructure

The tested environment reuses existing Forgejo, MinIO, Kubernetes, and Conjur services. This repository supplies the demonstration runner manifests and Conjur policy; it does not install those services or claim to bootstrap an arbitrary new cluster automatically.

## Backend

Create bucket `prisma-airs-terraform-adoption-demo`, enable versioning, and create a scoped S3 user. Permit bucket listing/location, exact `state/demo.tfstate` read/write, `.tflock` read/write/delete, and private `plans/*` read/write. Optional `probe/*` keys support conditional-write and lock tests. Do not grant state-object deletion or access to another bucket. See [the policy template](../infrastructure/minio-policy.json.example).

Verify duplicate conditional puts return 412, a second Terraform operation cannot acquire an existing state lock, and unrelated bucket access returns 403. A disposable `terraform_data` probe does not call AIRS. Never force-unlock an active job.

## Workload identity and runner

Apply `infrastructure/00-namespace.yaml` after reviewing its namespace and pod-security label. Register a **repository-scoped** Forgejo runner, and store its connection UUID/token in a Kubernetes Secret named `runner-connection` in that namespace. The Secret key is `connection.yaml`; keep registration credentials out of Git.

```yaml
server:
  connections:
    demo:
      url: https://YOUR_FORGEJO
      uuid: YOUR_RUNNER_UUID
      token: YOUR_RUNNER_TOKEN
```

The daemon combines this Secret with its nonsecret configuration. Adapt the node selector, image registry, storage class, and server URL to your environment. The Docker-in-Docker sidecar is privileged; isolate this dedicated runner and trust everyone who can submit code to its private repository. A namespace ingress-deny policy and repository scope do not make untrusted workflow code safe.

Copy your **public** Conjur CA into the ConfigMap. Review/apply the runner manifest. The projected service-account token has audience `conjur` and is mounted read-only with the CA into explicitly configured jobs.

An existing `authn-jwt/talos` authenticator maps JWT `sub` to hosts under `apps`, validates audience `conjur`, and also requires Kubernetes namespace/service-account claims. The host policy template includes both annotations; leaving them out produced a real 401 during initial bootstrap. Configure issuer/JWKS/audience/identity-path and claim requirements if your authenticator differs; don't change an existing production authenticator to bypass a mismatch.

Load `conjur-policy.yml.example` using a Conjur administrator, then seed its five management/backend variables securely. The runtime runner receives only their read/execute grant and membership in the authenticator's apps group. It never receives an administrator API key. Prove its JWT can retrieve the five demo variables and cannot retrieve a production-scoped variable.

Apply `20-conjur-ca.yaml` and `10-runner.yaml`; confirm both runner and Docker containers are ready. Bootstrap PATs and administrator credentials are operator-only, must not appear in workflow secrets, and should be revoked/removed after setup.

## Review and recovery

Private binary plans and raw state can contain credentials even if console output is masked. Inspect them only through trusted scoped backend access. Retain state versions and plan evidence; versioning alone is not a tested backup/restore service. For recovery, stop live jobs, inspect lock ownership, back up current state, and compare lineage/serial/identities before any operator restoration.
