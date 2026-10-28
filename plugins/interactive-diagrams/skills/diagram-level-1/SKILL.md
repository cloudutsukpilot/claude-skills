---
name: diagram-level-1
description: >-
  Create an interactive, explorable architecture diagram of any system as one self-contained HTML page:
  components nest in levels of detail (level 0 is the system in its context, each level opens one more
  layer, click a component to expand or collapse it), the canvas pans and zooms like a map, layout is
  automatic (ELK), components are icons or real logos, every component's side panel shows its status,
  a lead sentence, how it works, where, when, links and its API, and arrows carry protocol:port pills,
  colours per kind of communication and moving dots for streams. The diagram is data
  (diagrams/<name>/diagram.yml), validated, built into diagrams/<name>/index.html and checked in a
  real browser. This is the default level. Use it when the user asks for an "architecture diagram",
  "interactive diagram", "explorable diagram", "zoomable diagram", "C4-style diagram", "diagram with
  levels", "drill-down" or "system map", or says "level 1". For certificates, TLS details and view
  tabs use diagram-level-2; for animated use cases or a guided walkthrough use diagram-level-3.
---

# Interactive diagram: Level 1 (structure)

| Level | Skill | Adds |
|---|---|---|
| **1** | **diagram-level-1** | Components in levels, facts panels, arrows with why, protocol and port |
| 2 | diagram-level-2 | Certificates on every arrow, the exchange on the wire, view tabs |
| 3 | diagram-level-3 | Use cases: packets travel the arrows step by step, with outcomes |

A level-1 diagram can be raised to level 2 or 3 later without changing what it already has.

## 0. Paths

`PLUGIN` = two folders above this skill's base directory (it holds `engine/`, `scripts/`,
`reference/`, `templates/`, `examples/`). Read `PLUGIN/reference/workflow.md` once: it has the
standard layout, commands and checks every level shares.

## 1. Intake

Topic, scope and the source of truth (docs, code, IaC, manifests the user points at). Ask for what is
missing in one message: the main components and where they run, how they connect (protocol, port),
hostnames and consoles. Never invent a fact.

## 2. Model

Follow `PLUGIN/reference/structure.md`: a C4-style tree (level 0 = 3 to 9 components), `status` and
`facts` on every component, arrows between the deepest components with `why`, `proto` and `port`.
Default ports: `PLUGIN/reference/protocols-ports.md`.

## 3. Write

Copy `PLUGIN/templates/level-1.yml` to `diagrams/<name>/diagram.yml` and replace every `<…>`. Keys:
`PLUGIN/reference/data-format.md`.

## 4. Validate

`python3 "$PLUGIN/scripts/validate.py" diagrams/<name>/diagram.yml --level 1`; fix every error and
warning.

## 5. Build

`python3 "$PLUGIN/scripts/build.py" diagrams/<name>/diagram.yml` → `diagrams/<name>/index.html`.

## 6. Check in a real browser

Run `setup.sh` and `preview.cjs` as in `workflow.md` step 6. Read `light-desktop-level1.png`, the
deepest level's screenshot, `panel.png` and `card.png`; fix overlaps or crowded levels and rebuild.

## 7. Report

Paths, what each level shows, facts you could not verify, the preview result. Commit only when asked.
