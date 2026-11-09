# Changelog

Versions are per plugin and tagged `<plugin>-v<version>`.

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
