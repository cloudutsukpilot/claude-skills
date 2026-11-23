# Changelog

Versions are per plugin and tagged `<plugin>-v<version>`.

## interactive-diagrams 1.9.0 — 2026-11-23

- The use-case pointer is now a packet: a small frame with a header strip and the arrow's protocol on
  it (`HTTPS`, `gRPC`, `Redis` …), upright so it reads on any arrow, with a chevron showing which way it
  travels; requests in `accent2`, replies green.
- Packet inspector. A press on a moving packet, or the new magnifier in the player's controls, pauses
  the use case and opens the side panel on that step's hops (a tab per hop), layer by layer: Network,
  Transport (TCP/UDP and ports), Security (TLS/mTLS and its certificates, or why there is none),
  Application (the protocol's message, then the packet's own first line and headers) and Payload (the
  body, its size, Copy). The step counts as reached, so Next and Play continue from the next one; the
  inspector follows the steps until another panel opens.
- New optional keys: `packets` on a step (`{<edge id> | ~<edge id>: packet}`) and `packet` / `reply` on an
  arrow, each `{summary, line, headers, body, lang, note, source, illustrative}`. Without them every hop
  still shows the layers its arrow describes. `validate.py` checks the keys, that each `packets` key is a
  hop of its step, asks for `source` or `illustrative: true`, and rejects anything that looks like a live
  token or key. The web-shop example records five packets.
- `build.py` adds the Inspect button to the controls; `preview.cjs` checks the packet's shape, pressing a
  moving packet, Inspect, a recorded packet's content and that the inspector follows the next step.

## interactive-diagrams 1.8.0 — 2026-11-23

- The player's controls move into the step card, which becomes a narrow box (about 22rem) in the
  canvas's bottom-right corner, instead of a drawer hanging from the top of the canvas plus a card across
  the bottom. Its head has `n/N`, the use case and a close button; then the step's title, the banner line
  and the description; the controls (play, previous, next, restart, speed, padlock, mode, Details) at its
  foot. Details makes the same box taller.
- A click on a use case in the sidebar plays it and opens the box; the box stays while the use case runs
  (also when paused) and goes 5 s after the last step, or at once with the close button, which stops the
  use case and restores the reader's layout. A single use case is now listed in the menu too, since a
  click there is how it starts.
- While the box is up, the camera frames each step in the room left of it.
- `build.py` renders the controls inside `.dgm-banner`; the `.dgm-player` drawer and `.dgm-step-n` are
  gone. `preview.cjs` checks the box: none before a use case, opened and playing on a click, in the
  bottom-right corner with the controls at its foot, the close button, open while playing, gone 5 s after
  the end.

## interactive-diagrams 1.7.2 — 2026-11-23

- Details always changes the step card. Before, it showed `detail` only on steps that had one, so on a
  diagram with a few details (wardens: 9 of 60 steps) ticking it seemed to do nothing. A step without
  `detail` now shows its `text` and then each hop it makes: from → to, protocol:port and the arrow's
  `why` (a reply whose request is in the same step is folded into it). The box is offered whenever a
  step has a `detail` or a hop. `validate.py` now names, per use case, the steps without `detail`, and
  the docs ask for `detail` on every step. `preview.cjs` checks that Details changes every step's card.

## interactive-diagrams 1.7.1 — 2026-11-23

- Play runs only the use case the reader picked: after its last step (and the outcome's pause) the player
  stops and the diagram goes back to the reader's layout, instead of moving on to the next use case.
  `loop: true` now plays the same use case again. `preview.cjs` checks that Play stops on the same use case.
- The step card shows only while a use case runs: none before it is played, every step while it plays
  or is stepped through, and it goes 5 seconds after the last step completes (the player also waits those
  5 seconds before it puts the reader's layout back). It now spans the canvas's whole width at the bottom
  (left of the side panel when one is open) instead of sitting in the middle. `preview.cjs` checks all three.

## interactive-diagrams 1.7.0 — 2026-11-23

- One sidebar on the left: **Levels**, **Views** and **Use cases** are collapsible menus (each head
  folds its items; the choice is remembered per diagram), and the zoom lock, zoom in, zoom out, Fit and
  fullscreen buttons sit at its foot, always in view while the menus scroll. The `«` toggle folds the
  whole sidebar to a strip that keeps those buttons. The toolbar above the diagram and the view tabs
  on top of the canvas are gone, so the canvas starts at the top.
- Zoom lock: the padlock at the sidebar's foot holds the current zoom. While it is locked the zoom
  buttons are off, Ctrl + scroll, pinch and `+`/`-` don't zoom (a hint says the zoom is locked), and the
  camera moves of levels, opening a component, Fit and use cases only pan, centred on the point they
  aimed at. Dragging still moves around. `zoom_lock: true` opens the diagram locked at its opening zoom.
- The player moved to the top of the canvas: a tab with the play state and the step `n/N` hangs from
  its top edge, and hovering it (clicking on touch, or keyboard focus) drops the controls down. They fold
  back when the pointer leaves and whenever a use case starts playing. The per-step dots are gone: the
  `n/N` count is the progress.
- One description: the caption under the canvas is gone and the step card on the canvas carries
  everything (the step's `n/N` and title, the use case's title on the right, the action line, the
  text). Before the first step the card introduces the use case. With Details on, the same card grows a
  little (wider and taller, a long `detail` scrolls inside it) instead of moving under the canvas.
- `preview.cjs` checks the sidebar (menus, a menu folding, the buttons at its foot, folding the whole
  sidebar), the zoom lock, the player drawer (closed by default, opens on hover, folds while playing)
  and the merged card, with `sidebar.png`, `player-open.png`, `zoom-locked.png` and `collapsed.png`.

## interactive-diagrams 1.6.1 — 2026-11-22

- Arrow labels no longer sit on other arrows' pills. With `layout: auto`, ELK kept room only for the
  protocol pill, beside the arrow, and the renderer then drew the pill on the line with the text label
  18px above it, so two close parallel arrows collided: in the web-shop example's level 0 the "paid"
  label of the Payments webhook covered the "HTTPS :443" pill of the charge arrow. ELK now keeps an
  inline box centered on the line that holds the pill and its label, and both layouts place pills and
  labels with one pass (`placeLabels`) that checks each label as its own box, as wide as its text,
  against components and every pill and label placed before; a label on an arrow without a pill is
  placed the same way. The stable layout (the default) keeps its component positions.

## software-factory 0.3.0 — 2026-11-21

- `/factory init` also writes `docs/plans/README.md` (from the new `templates/plans-README.md`), so every repo keeps
  its plans in the same folder: one file per plan, each with a Progress table whose rows link the feature files that
  deliver them. A plan already kept elsewhere (often a single `docs/plan.md`) stays where it is and the README links
  it. `factory.py init-check` reports a missing `docs/plans`.

## interactive-diagrams 1.6.0 — 2026-11-21

- Bands for flow diagrams: `bands:` (top level or a group) lists horizontal swimlanes, `band:` puts a
  component in one. The main band keeps the main path in rows; every other band is a single row in the
  order written, each component slid under the components it connects to, so arrows run straight down
  between bands instead of converging in the middle of the main row. Labelled top-level bands are drawn
  as swimlanes with a header column (light and dark), and Fit includes them.
- Hubs: in a flow container with no `band:` set, a component that receives arrows from 3 or more
  siblings and leads to at most one moves to its own band below the main path (`hubs: false` keeps
  it in place).
- The validator checks `bands`, `band` and `hubs`.

## interactive-diagrams 1.5.0 — 2026-11-21

- `arrange: flow` (top level, or `arrange:` on one group): components are laid out like a flowchart
  page instead of by their arrows: in the order they are written, left to right in rows of `cols`, rows
  top to bottom, every row top-aligned. The top level defaults to one row, a group to rows of up to 4.
  An opened group grows right and down from its closed box, pushing the rest of its row right and the
  rows below down; closing it restores the layout exactly. For process maps, where ELK's layered
  placement put the phases on a staircase because of the arrows that skip ahead or loop back.
  Stable layout only; the default stays `layered`. The validator checks `arrange` and `cols`.

## software-factory 0.2.0 — 2026-11-20

- `/factory check <feature>` (`factory.py check`): is a feature ready to run with nobody to ask? It checks
  the fixed rules (frontmatter, `status: ready`, non-empty What, Why and Done when, a `component:` that is
  in `docs/project.yaml`, the repo set up for the factory), then runs intake as a preflight
  (`Mode: preflight`) that asks every question an unattended run would have to guess. Nothing is written
  to the repo and no job is created.
- Non-interactive runs: with `FACTORY_NON_INTERACTIVE=1`, `factory.py queue` prints `mode non-interactive`,
  every agent prompt line ends with `Mode: non-interactive`, intake and the builder decide with stated
  `## Assumptions` instead of asking or blocking, and the orchestrator never waits for a reply. For the
  homelab's label-triggered CI (homelab-gitops `portfolio-tasks.yaml`).
- Feature files may name a `component:` and the extra `plugins:` a CI run should load.

## interactive-diagrams 1.4.1 — 2026-11-20

- Stable layout: opening a component inside an open group no longer moves that group back to its base
  position. Before, the component opened last and its open ancestors were pinned at their base centers,
  so when a level opened several groups at once (and one had been pushed aside), opening a component
  in the pushed group sent it back and pushed its neighbours the other way: on 4 of 7 blog diagrams,
  opening some components put a neighbour on its other side. The layout is now replayed in the order
  components were opened, each step starting from the one before, so a box pushed earlier stays where
  it is. Closing still restores the layout exactly.

## interactive-diagrams 1.4.0 — 2026-11-20

- Stable layout, the new default for every level: opening or closing a component no longer lays out the
  whole diagram again. Each container's children are placed once (ELK, as closed components, with
  every arrow lifted to them); an opened component grows around its own center and only the components
  it would touch are pushed straight away from it, cascading outward. The component you opened stays
  at the same place on screen: the camera doesn't pan, and zooms out around it only if it no longer
  fits. Closing it puts everything back exactly.
- New orthogonal arrow router for the stable layout (A* around the components, fewest bends, parallel
  arrows in their own lanes) and pill placement that avoids other pills and components. An arrow's
  label now sits just above its pill.
- `layout: auto` keeps the old behaviour (full ELK relayout on every change). `map:` diagrams are
  unchanged.
- `preview.cjs` checks the stable layout: the opened component stays put on screen, the others stay
  on their side of it, and closing it restores every position.

## software-factory 0.1.1 — 2026-11-19

- `/factory run` trusts the queue: a `new` row becomes a job and a `resume` row is driven from its stage. The orchestrator no longer guesses from git
  history that a feature is already built (the commit that added the feature file named it, so the first
  real run on a repo started nothing). Intake still rejects a feature that already exists.
- The skill writes the script's full command each time instead of `F="python3 …"; $F …`, which doesn't
  split into words in zsh.

## software-factory 0.1.0 — 2026-11-19

- New plugin. `/factory` (skill `software-factory:factory`) runs feature files from `docs/features/`
  through intake → spec → build → gate → routed reviewers → approver, and ends each as a reviewed pull
  request that you merge; the factory never merges.
- Agents: `intake`, `spec-writer`, `builder`, `reviewer` (lenses `code`, `security`, `ui`, `infra`,
  `docs`), `approver`.
- `scripts/factory.py`: the only writer of job state; refuses illegal moves; worktrees, the gate
  (`.factory/checks.sh`, protected paths, merge conflicts), push and draft PR, `escalate_paths`, sync.
- Standard formats: feature files (`reference/feature-format.md`) and per-repo `.factory/`
  (`reference/repo-setup.md`).

## interactive-diagrams 1.3.0 — 2026-11-10

- Step card with Details on: the card moves out of the canvas and sits under it at the figure's full
  width, shows the whole description without a scroll box and covers no component (the camera no
  longer keeps room for it). With Details off it floats at the canvas bottom as before. In full
  screen a long description scrolls inside the card.
- `reference/stories.md`: how to write `detail` for a semi-technical reader (What happens / Why it
  matters / How, the function named in `code`, terms explained, gaps stated) and `details: true`.
- `preview.cjs`: checks the card sits under the canvas at full width with Details on, and back on the
  canvas with it off.

## interactive-diagrams 1.2.0 — 2026-11-09

- Step card: the banner at the bottom of the canvas becomes a card with the step's number and title,
  the banner line (`action`, then the outcome) and its description. The caption under the canvas now
  shows the use case's title and summary.
- `detail` on a step: 3 to 10 lines of Markdown, shown on the card instead of `text` when the reader
  ticks **Details** in the player. `details: true` starts ticked; the reader's choice is remembered in
  their browser. With Details on, auto-play stays long enough to read each detail (about 250 words a
  minute, at most 25 s, scaled by the speed button).
- The camera frames each step's components above the card.
- `validate.py`: `details` must be true or false; `detail` length (3 to 10 lines, under ~160 words),
  not a copy of `text`; a use case with no `detail` warns.
- `preview.cjs`: checks the card's title and description, ticks Details on a step with `detail` and
  saves `step-details.png`.
- `examples/web-shop`: `detail` on six steps.

## interactive-diagrams 1.1.0 — 2026-11-09

- Lock mode for use cases: a padlock in the player (or `lock: true` in `diagram.yml`) plays every
  use case on the reader's layout (their level, the components they opened, their view tab). Nothing
  opens or closes; the camera still moves to each step. A hop inside a closed component, or on an
  arrow the tab hides, pulses that component and the banner says so ("· inside Shop platform").
- Turning lock on in the middle of a use case puts the reader's layout back and keeps playing.
- `validate.py`: `lock` and `loop` must be true or false; `lock` without use cases warns.
- `preview.cjs`: a lock-mode check (level 1 + one group opened by hand) and `step-locked.png`.

## interactive-diagrams 1.0.0 — 2026-10-28

- First release, made generic from the Cloudutsuk blog's `cloudutsuk-diagram` skill.
- Three tiered skills: `diagram-level-1` (structure), `diagram-level-2` (connections: certificates,
  exchange cards, view tabs), `diagram-level-3` (stories: use cases, geo map).
- `scripts/build.py`: YAML → one self-contained HTML page (engine, styles, data and local logos
  inlined; `si:<slug>` for Simple Icons logos).
- `scripts/validate.py --level N`: checks what each tier promises; reads its tables from the engine.
- `scripts/preview.cjs`: browser check in light, dark and phone views, with screenshots.
- Starter templates per level and a complete example (`examples/web-shop`).
