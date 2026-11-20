# Plan: flow arrangement for interactive diagrams

**Status (2026-11-21):** In progress. Plugin 1.5.0 in review; the blog engine is not changed yet.

## Goal

Process maps (a fax intake flowchart, an approval flow) read like a flowchart page: phases on one row,
left to right, and a phase that opens grows down, with its steps in rows, left to right then top to
bottom. ELK's layered placement (the default) places components by their arrows, so arrows that skip
ahead or loop back put the phases on a staircase.

## Decisions

See the 1.5.0 entry in `CHANGELOG.md` and `reference/structure.md`: `arrange: flow` is opt-in (top level
or per group), stable layout only, in written order, `cols` per row (top level: one row; group: up to 4).

## Progress

| Step | Status | PRs | Left |
|---|---|---|---|
| 1. Plugin engine, validator, docs, version 1.5.0 | In progress (2026-11-21) | this branch | Merge, then tag `interactive-diagrams-v1.5.0` |
| 2. Install 1.5.0 on the Spark | Next | — | After the merge: `claude plugin marketplace update cloudutsuk` and `claude plugin update interactive-diagrams@cloudutsuk` |
| 3. First user: the CarePro intake process map (evolent `project-fax-intake`) | Done (2026-11-21) | built with this branch's engine | Rebuild with the released plugin after step 2 (no change expected) |
| 4. Blog engine (`sakharams.github.io/assets/js/diagram.js`, `cloudutsuk-diagram` skill) | Planned | — | Port the same change when a blog diagram needs it |

Waiting on you: merging the PR.
