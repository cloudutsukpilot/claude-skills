# Lens: docs

Covers the documentation the repo's rules require with a change. AGENTS.md (or CLAUDE.md) and this
repo's `.factory/lenses/docs.md` say which docs those are.

- **Required updates:** every doc the spec's **Docs** section lists is updated, and so is any the repo's
  rules require that the spec missed (README, ADR, plan Progress row with the date, changelog).
- **The feature file:** `status: done` with a `## Factory` section saying what was built and left out.
- **Accuracy:** docs describe what the code now does: commands that work, paths that exist.
- **Public text:** anything that will be published (a public site, a public repo's README) holds no
  internal ids, tokens, emails, private hostnames or private repo links.
- **Style:** the repo's documentation style as its existing docs show it.
