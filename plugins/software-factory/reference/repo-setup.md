# Setting up a repo for the factory

A repo needs three things, all committed on its base branch:

```
.factory/
  .gitignore        jobs/            (job state is runtime data, never committed)
  checks.sh         the repo's checks: exit 0 only when a branch is fit to review
  config.json       optional: overrides of the plugin's defaults (below)
  lenses/           optional: extra checklist per reviewer, e.g. lenses/infra.md
docs/features/      the queue (format in feature-format.md)
AGENTS.md           (or CLAUDE.md) how to set up a fresh checkout, run the app, run the tests
```

`/factory init` writes `.factory/` and `docs/features/README.md` from the templates, fills
`checks.sh` from what AGENTS.md, the Makefile, `package.json`, `pyproject.toml` and the CI workflows
say the checks are, runs it on the base branch, and opens a PR.

## checks.sh

The gate runs it with the job's worktree as the working directory, after every build round and before
any reviewer starts. The gate always runs the **base branch's** copy (from the main checkout), so a
branch can't change the checks it is judged by.

- Fast, deterministic, non-interactive: no watch modes, no prompts, nothing that rewrites files.
- Check what CI checks, for the parts of the repo that can be checked locally.
- It may use `FACTORY_CHANGED` (a file listing the paths the branch changed, one per line) to check only
  what changed, for example only the Terragrunt stacks a branch touches.
- Exit 0 only when every check passes.

## config.json

Every key is optional; the plugin's `templates/config.json` holds the defaults.

| Key | Default | Meaning |
|---|---|---|
| `base_branch` | `main` | Branch jobs start from and PRs target. |
| `concurrency` | `2` | Jobs `/factory run` works on at once. |
| `max_rounds` | `3` | Build rounds (gate + review) before the job goes to you. |
| `models` | intake, spec, builder, approver: `opus` | Model per fixed role. |
| `routing` | low: code `sonnet`; medium: code `sonnet`; high: code `opus` | Code reviewer's model by intake's risk rating. |
| `surface_reviewers` | ui: `sonnet`, security: `opus`, infra: `opus`, docs: `sonnet` | Reviewer that joins when intake flags that surface. |
| `always_reviewers` | `[]` | Surfaces reviewed on every job, e.g. `["docs"]` in a repo whose rules ask for doc updates with every change. |
| `protected_paths` | `.factory/**`, `.github/workflows/**` | A branch that changes these fails the gate. |
| `escalate_paths` | `[]` | Globs where any change makes the approver escalate, e.g. `apps/**` where a merge deploys. |

## lenses/<reviewer>.md

Plain Markdown checklists the matching reviewer reads after its own. Use them for what is specific to
the repo: an admission policy every manifest must pass, the docs a change must update, the paths that
deploy on merge. The reviewer names are `code`, `security`, `ui`, `infra` and `docs`.
