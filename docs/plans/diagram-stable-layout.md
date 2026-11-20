# Plan: stable layout for interactive diagrams

**Status (2026-11-20):** Done. Plugin 1.4.1 released and installed on the Spark; the blog runs the same engine (live on cloudutsuk.com).

## Goal

Opening or closing a component must not move the diagram around. Today every expand or collapse runs
ELK on the whole visible graph again, so every component can land somewhere new and the camera pans
to the opened group: the reader loses where things were. With the stable layout, every component
keeps a fixed center. An opened component grows around its own center, its children are laid out
inside it, and only the neighbours it would overlap slide straight outward, keeping their order.
Closing it moves them back exactly.

## Decisions (2026-11-20, with the owner)

- **Neighbours are pushed out, order kept.** Each container's children get one base layout (ELK, as
  closed components, with every arrow of every view lifted to them), computed once.
- **Local push, not row-and-column insertion** (changed during phase 1). The first version shifted
  every sibling right of a grown box by `ew/2` (left: `−ew/2`) and the same vertically. That is
  overlap-free by construction, but it inserts a whole row and column of space: on the 107-component
  platform diagram the deepest level covered twice the area of the old ELK layout. The default is now
  a local cascade (`pushLocal`): only siblings that collide move, straight away from the grown box,
  along the axis they were separated on, keeping their base gap (up to 80). The last opened component
  that is still open, and its ancestors, give way last. The row-and-column push stays as the fallback
  when the cascade doesn't settle. Result on the same diagram: deepest level 3837×3918 against ELK's
  7553×4134, layout about 90 ms.
- **Closing restores exactly.** Positions are a function of the base layouts, what is open and the
  order it was opened in (closing a component removes it from that order), so closing gives back the
  layout from before it opened.
- **Replay the open order** (changed in 1.4.1, found while porting to the blog). 1.4.0 pinned only the
  component opened last and its ancestors, at their base centers. When a level opens several groups,
  nothing is pinned and one of them may be pushed aside; opening a component inside it then sent that
  group back to its base and pushed its neighbours the other way (a neighbour crossed to its other side
  on 4 of the 7 blog diagrams). Now the layout is computed step by step: first the groups the level
  opened, then each component in the order it was opened, each step starting from the positions the
  step before left and pinning that step's component and its ancestors. Opening never moves a box that
  was pushed earlier back, and closing still restores exactly (the replay is a function of the open
  order). The camera also compensates if the clicked component moved at all, so
  it stays at the same place on screen when opening and when closing.
- **Hidden components** (view-only, outside their view) keep their base space (making them size 0
  could pull two neighbours into each other). Open groups draw their frame tight around their visible
  children, so the gap shows only between components, not as an empty frame.
- **Arrows** get their own orthogonal router (A* on the obstacle grid, with a bend penalty, and
  parallel segments nudged apart), because ELK only routes graphs it places itself.
- **Camera:** after opening or closing a component the camera does not pan. It zooms out only if
  the opened component would not fit, anchored on that component's center (which stays at the same
  place on screen). Level buttons still fit the whole diagram.
- **Default for every level** (1–3): the engine is shared. `layout: auto` in `diagram.yml` keeps the
  old full-relayout behaviour. `map:` diagrams are unchanged (geo positions are already fixed).
- **Both engines:** the plugin (`plugins/interactive-diagrams/engine/diagram.js`) first, then the
  same file in the blog (`sakharams.github.io/assets/js/diagram.js`, `cloudutsuk-diagram` skill).
  The two engines differ only in their header comment.

## Progress

| Phase | Status | PRs | Left |
|---|---|---|---|
| 1. Plugin engine: stable layout, router, camera, `layout: auto`, validator, docs, version 1.4.0 | Done (2026-11-20) | #10 | Nothing. Merged and tagged `interactive-diagrams-v1.4.0` |
| 2. Install the new plugin version on the Spark (`claude plugin` update) | Done (2026-11-20) | — | Nothing. `claude plugin marketplace update cloudutsuk` and `claude plugin update interactive-diagrams@cloudutsuk`: 1.1.0 → 1.4.0 (restart Claude Code to load it) |
| 1b. Plugin 1.4.1: replay the open order (bug found in phase 3) | Done (2026-11-20) | #12 | Nothing. Tagged `interactive-diagrams-v1.4.1`; plugin updated on the Spark 1.4.0 → 1.4.1 (restart Claude Code to load it) |
| 3. Blog engine and `cloudutsuk-diagram` skill docs | Done (2026-11-20) | sakharams.github.io #124 | Nothing. Deploy succeeded; the live `diagram.js` has the replayed open order |

Waiting on you: nothing. Follow-up outside this plan: the blog's `preview.cjs` crashes on the GA4 page-view post (also with the old engine), tracked in the workspace `PENDING.md`.
