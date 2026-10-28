---
name: diagram-level-3
description: >-
  Create an interactive architecture diagram with everything diagram-level-2 does (nested levels, pan
  and zoom, facts panels, protocol:port arrows, certificates, the exchange on the wire, view tabs)
  plus guided use cases: the reader picks a story (sign in, place an order, deploy, an alert, a batch
  job, a failure), Play sends a packet hop by hop along the real arrows and back, each step opens the
  groups it needs and shows a banner line, and the last step celebrates the outcome (success or
  fail); a use case can have an alternative mode (cache hit, declined card) and components can sit on
  a world map. Output is one self-contained HTML page built from diagrams/<name>/diagram.yml and
  checked in a real browser. Use it when the user asks for an "animated" diagram, a "walkthrough",
  "use cases", "scenarios", a "guided tour", "show the request flow step by step", "simulate a
  failure", a request's journey through the system, a geo/multi-region map, or says "level 3", or
  wants to add stories to a level-1 or level-2 diagram.
---

# Interactive diagram: Level 3 (stories)

| Level | Skill | Adds |
|---|---|---|
| 1 | diagram-level-1 | Components in levels, facts panels, arrows with why, protocol and port |
| 2 | diagram-level-2 | Certificates on every arrow, the exchange on the wire, view tabs |
| **3** | **diagram-level-3** | Use cases: packets travel the arrows step by step, with outcomes |

Level 3 includes everything in levels 1 and 2. To raise an existing diagram, keep its file and add
the missing keys (certificates and views first if it is level 1).

## 0. Paths

`PLUGIN` = two folders above this skill's base directory (it holds `engine/`, `scripts/`,
`reference/`, `templates/`, `examples/`). Read `PLUGIN/reference/workflow.md` once.

## 1. Intake

Everything levels 1 and 2 ask, plus: which activities the reader should be able to replay (2 to 6),
the order of the hops in each (including the replies) and any alternative path worth a second mode.
For a map: the region of each component.

## 2. Model

Follow `PLUGIN/reference/structure.md`, `PLUGIN/reference/connections.md`, then
`PLUGIN/reference/stories.md`: one activity per use case, one action per step, every reply travels
back (`~id`), every step has `title`, `action` and `text`, and the last step has `result` and
`outcome`. Add any arrow a real hop needs; never let a packet jump.

## 3. Write

New diagram: copy `PLUGIN/templates/level-3.yml` to `diagrams/<name>/diagram.yml` and replace every
`<…>`. Keys: `PLUGIN/reference/data-format.md`. Full example: `PLUGIN/examples/web-shop/diagram.yml`.

## 4. Validate

`python3 "$PLUGIN/scripts/validate.py" diagrams/<name>/diagram.yml --level 3`; fix every error and
warning (at level 3 a diagram needs at least one use case, paths must be continuous and requests
must show their response or be `oneway`).

## 5. Build

`python3 "$PLUGIN/scripts/build.py" diagrams/<name>/diagram.yml` → `diagrams/<name>/index.html`.

## 6. Check in a real browser

Run `setup.sh` and `preview.cjs` as in `workflow.md` step 6. Read `light-desktop-level1.png`, the
deepest level, `panel.png`, `card.png`, `edge-panel.png`, the `view-*.png` files, `step-next.png`
(a packet on its arrow and the banner) and `outcome.png`.

## 7. Report

Paths, what each level and view shows, each use case in one line, facts you could not verify, the
preview result. Commit only when asked.
