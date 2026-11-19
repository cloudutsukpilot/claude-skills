# Feature files: the factory's queue

Every repo keeps its feature requests in one folder, one Markdown file per feature:

```
docs/
  features/
    README.md                   optional: a line saying what this folder is
    001-reading-time.md
    002-not-found-page.md
  plans/                        plans stay where they are; a plan's Progress row can link a feature file
```

Number features in order (`001`, `002`, …) with a short kebab-case slug. The number and slug never
change; the factory names the job, the branch (`factory/<number>-<slug>`) and the worktree after them.

## The file

```markdown
---
title: Show reading time on blog posts
status: ready
plan: docs/plans/blog-ux.md
priority: 2
---

## What
What should exist when this is done, from the point of view of whoever uses it.

## Why
The problem it solves, or the plan step it delivers.

## Done when
Optional. Observable checks you already know you want, one per line.

## Notes
Optional. Pointers: files, earlier PRs, constraints, things not to touch.
```

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | One line. |
| `status` | yes | See below. |
| `plan` | no | Path of the plan doc this feature delivers, relative to the repo root. |
| `priority` | no | Integer; lower runs first. Without it, the number decides. |

Only `## What` is required in the body. Write it like an issue: the factory's intake reads it, may
narrow it to a first slice that fits one pull request, and asks when only you can decide something.

## Status

| Status | Who sets it | Meaning |
|---|---|---|
| `draft` | you | Being written. The factory ignores it. |
| `ready` | you | Queued. `/factory run` picks it up. **Only `ready` on the base branch runs**: setting it is your approval to spend a job on it. |
| `done` | the factory's PR | The builder sets it, and adds a `## Factory` section (job id, date, what was built and what was left out), in the feature's own pull request. Merging the PR closes the feature. |
| `rejected` | you | Won't do. Add one line under `## Notes` saying why. |

While a job runs, its state (intake, building, waiting for you) lives in the job, not in this file:
`/factory status` shows it. The factory never edits a feature file on the base branch.

## Linking from a plan

A plan's Progress table points at the feature files that deliver each step:

```markdown
| 2. Reading time | In progress | #41 | [feature 001](../features/001-reading-time.md) |
```

## A feature that needs other repos

A job works in one repo. When a feature needs changes in another repo, write a feature file there too
and say in `## Notes` which feature it pairs with. Intake reports cross-repo needs it finds.
