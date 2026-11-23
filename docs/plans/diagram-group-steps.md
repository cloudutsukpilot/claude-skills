# Plan: group a use case's steps by closed component (lock mode)

**Status (2026-11-23):** In progress. Plugin 1.10.0 in review; the wardens diagram and the blog follow.

## Goal

In lock mode a use case plays on the reader's layout. When several consecutive steps happen inside one
component the reader keeps closed (at level 1, say), they only pulse it, one after another. They become
one step instead: one card listing them, and a shorter use case.

## Decisions

The owner chose (2026-11-23): lock mode only; consecutive steps whose every hop stays inside the same
closed component; one card that lists each step. Details in the 1.10.0 entry of `CHANGELOG.md` and
`reference/stories.md`.

## Progress

| Step | Status | PRs | Left |
|---|---|---|---|
| 1. Plugin engine, preview check, docs, version 1.10.0 | In progress (2026-11-23) | this branch | Review and merge, tag `interactive-diagrams-v1.10.0` |
| 2. platform-wardens diagram rebuilt with 1.10.0 | Planned | — | After step 1 |
| 3. Blog engine (`sakharams.github.io`) and its `cloudutsuk-diagram` skill | Planned | — | After step 1 |

Waiting on you: reviewing and merging the PRs.
