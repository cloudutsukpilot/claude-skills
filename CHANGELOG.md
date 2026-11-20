# Changelog

Versions are per plugin and tagged `<plugin>-v<version>`.

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
