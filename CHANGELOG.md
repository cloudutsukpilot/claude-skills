# Changelog

Versions are per plugin and tagged `<plugin>-v<version>`.

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
