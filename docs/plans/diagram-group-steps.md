# Plan: group a use case's steps by closed component (lock mode)

**Status (2026-11-24):** Done. 1.10.0, 1.11.0 and 1.12.0 are merged, installed on the Spark and the homelab PC, and tested on the live blog.

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
| 4. 1.11.0 (the owner's choices, 2026-11-24): a use case keeps at least two steps; the player box spans the canvas with the controls in a 2 x 4 grid; a packet rests 2 s on its target and Play waits; drag lock (pan only) with no auto-focus while it is on. Plugin, wardens rebuild, blog | Done (2026-11-24) | claude-skills #27, platform-wardens #378, sakharams.github.io #148 | Tagged `interactive-diagrams-v1.11.0` |
| 5. 1.12.0 (the owner's ask, 2026-11-24): the sidebar opens folded on every load and unfolds in fullscreen; fix the diagram vanishing in fullscreen with the player box open. Plugin, wardens rebuild, blog | Done (2026-11-24) | claude-skills #29, platform-wardens #380, sakharams.github.io #150 | Tagged `interactive-diagrams-v1.12.0`; installed on the Spark and the homelab PC |

Waiting on you: nothing.
