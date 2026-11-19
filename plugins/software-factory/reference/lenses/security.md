# Lens: security

- **Access:** every new or changed endpoint, handler, route or query checks who the caller is and that
  they may touch what they touch. Nothing newly reachable from outside without a reason in the spec.
- **Input:** user input is validated and never reaches SQL, shell commands, file paths, templates or
  HTML unescaped.
- **Secrets:** no keys, tokens, passwords or private hostnames in code, config, logs, docs or commits.
  Secrets come from the repo's secret store, never a literal.
- **Exposure:** responses, logs, error pages and public docs don't leak ids, emails, tokens or internals.
- **Supply chain:** new dependencies or images are needed, maintained and pinned the way the repo pins
  them.
- **Workloads:** containers don't gain privileges, host mounts, host network or broader service
  account rights.

Use CHANGES only for real problems this change introduces or makes worse; pre-existing issues go
under Notes.
