# Changelog

Versions are per plugin and tagged `<plugin>-v<version>`.

## interactive-diagrams 1.0.0 — 2026-10-28

- First release, made generic from the Cloudutsuk blog's `cloudutsuk-diagram` skill.
- Three tiered skills: `diagram-level-1` (structure), `diagram-level-2` (connections: certificates,
  exchange cards, view tabs), `diagram-level-3` (stories: use cases, geo map).
- `scripts/build.py`: YAML → one self-contained HTML page (engine, styles, data and local logos
  inlined; `si:<slug>` for Simple Icons logos).
- `scripts/validate.py --level N`: checks what each tier promises; reads its tables from the engine.
- `scripts/preview.cjs`: browser check in light, dark and phone views, with screenshots.
- Starter templates per level and a complete example (`examples/web-shop`).
