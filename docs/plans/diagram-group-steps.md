# Plan: group a use case's steps by closed component (lock mode)

**Status (2026-11-23):** Done. Plugin 1.10.0, the wardens diagram and the blog are merged; tested on the merged builds and the live blog.

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
| 1. Plugin engine, preview check, docs, version 1.10.0 | Done (2026-11-23) | claude-skills #25 | Tagged `interactive-diagrams-v1.10.0`; installed on the Spark and the homelab PC |
| 2. platform-wardens diagram rebuilt with 1.10.0 | Done (2026-11-23) | platform-wardens #374 | — |
| 3. Blog engine (`sakharams.github.io`) and its `cloudutsuk-diagram` skill | Done (2026-11-23) | sakharams.github.io #145 | Deployed |

Waiting on you: nothing.
