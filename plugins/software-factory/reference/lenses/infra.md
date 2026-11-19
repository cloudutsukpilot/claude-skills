# Lens: infra

Covers Kubernetes manifests, Helm values and charts, Terraform/Terragrunt, Dockerfiles, CI workflows,
and host scripts. If the branch touches none of these, write PASS and say so.

- **What a merge does:** say in Summary exactly what merging changes in a running system (a deploy, a
  resource created, replaced or destroyed, a restart). Anything destroyed or replaced that the spec
  didn't ask for is CHANGES.
- **Validity:** manifests and modules validate the way the repo validates them (render, lint, `terraform
  validate`, policy tests). Run a read-only check when one exists and the gate didn't cover it.
- **Admission and policy:** workloads meet the cluster's policies as the repo documents them (image
  pinning, security context, resource requests and limits); IaC meets the repo's policy checks.
- **State and data:** no change that recreates stateful resources, drops volumes, or moves state
  without a migration step in the spec.
- **Idempotence:** scripts are safe to run twice; no manual step hidden in a comment.
- **Secrets:** referenced from the secret store, never inlined.
