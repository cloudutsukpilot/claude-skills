# Plans

One file per plan, `docs/plans/<topic>.md`: work that spans several pull requests, repos or sessions, or more
than a day. A plan has a status line, the steps, decisions it depends on (as ADRs, not in the plan), and a
**Progress** section:

```markdown
## Progress

| # | Step | Status | PRs | Left |
|---|---|---|---|---|
| 1 | Reading time on posts | In progress | #41 | [feature 001](../features/001-reading-time.md) |
```

Status is one of Done (with the date), In progress, Next, Planned or Blocked. List what waits on the owner
under `### Waiting on the owner`, with the exact command or decision. Update the table in the same pull request
as each piece of work, and again after each merge.

Feature files in `docs/features/` that deliver a step name the plan in their `plan:` field, and the step's row
links the feature file.
