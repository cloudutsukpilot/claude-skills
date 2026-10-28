# interactive-diagrams

Explorable architecture diagrams as **one self-contained HTML page**, written as data (YAML),
validated, built and checked in a real browser. Three skills, each a tier that builds on the last:

| Level | Skill | Adds |
|---|---|---|
| 1 | [diagram-level-1](skills/diagram-level-1/SKILL.md) | Components nested in levels (level 0 = context; click to expand), pan and zoom, automatic ELK layout, icons or logos, a facts panel per component (status, summary, how, where, when, links, API), arrows with why, protocol:port pills, colours per kind and moving dots for streams |
| 2 | [diagram-level-2](skills/diagram-level-2/SKILL.md) | Certificates on every arrow (issuer, validity, storage, trust) or why there is none; the full exchange on the wire as a looping sequence diagram (TCP → TLS 1.3 / mTLS → HTTP, gRPC, OIDC, Kafka, MQTT, SSH, WireGuard …); view tabs for cross-cutting arrows |
| 3 | [diagram-level-3](skills/diagram-level-3/SKILL.md) | Guided use cases: a packet travels hop by hop and back, banners per step, success/fail outcomes, alternative modes; optional world-map backdrop |

Example: [examples/web-shop](examples/web-shop/) — `diagram.yml` and the built `index.html`.

## Use without Claude

```bash
cp templates/level-1.yml diagrams/my-system/diagram.yml          # edit it
python3 scripts/validate.py diagrams/my-system/diagram.yml --level 1
python3 scripts/build.py diagrams/my-system/diagram.yml          # → diagrams/my-system/index.html
```

Requirements: Python 3 with PyYAML. For the browser check (`scripts/preview.cjs`): Node.js and a
Chromium (`scripts/setup.sh` installs `playwright-core` into `~/.cache/interactive-diagrams` and finds
one). The built page loads ELK from jsDelivr and Font Awesome from cdnjs; everything else is inline.

Embed in any site with an iframe:
`<iframe src="/diagrams/my-system/index.html" style="width:100%;height:860px;border:0" loading="lazy"></iframe>`.

## Layout

| Path | What |
|---|---|
| `skills/diagram-level-{1,2,3}/SKILL.md` | The three skills (same seven sections each) |
| `reference/workflow.md` | Standard diagram layout, commands, checks: shared by every level |
| `reference/structure.md`, `connections.md`, `stories.md` | The rules each level adds |
| `reference/data-format.md` | Every key, with the level that introduces it |
| `reference/protocols-ports.md` | Default ports and communication kinds |
| `templates/level-{1,2,3}.yml` | Starters that validate cleanly at their level |
| `engine/diagram.js` | The engine: model, levels, ELK layout, SVG, pan/zoom, panels, cards, use cases, geo |
| `engine/src/diagram.scss` → `engine/diagram.css` | Styles (light and dark), every class prefixed `dgm-` |
| `engine/template.html` | The page shell build.py fills |
| `engine/world.json` | Land outlines for the geo backdrop |
| `scripts/validate.py`, `build.py`, `preview.cjs`, `setup.sh` | Validate, build, browser check, check setup |

## Changing the engine

Edit `engine/diagram.js` and `engine/src/diagram.scss` together, then rebuild the CSS:

```bash
sass --no-source-map --style=expanded engine/src/diagram.scss engine/diagram.css
```

`validate.py` reads ICONS, PALETTE, KINDS, PROTO_KIND, CARDS, FACTS, STATUS, CERT_KEYS and CERT_TYPES
from `diagram.js`, so a new icon or protocol needs no validator change. Keep every class and id
prefixed `dgm-`. Rebuild and re-run `preview.cjs` on the example before a PR, and bump the version
([docs/adding-a-skill.md](../../docs/adding-a-skill.md)).

The engine colours itself from three host variables, `--dgm-host-bg`, `--dgm-host-text` and
`--dgm-host-heading` (set in `template.html` for light and dark).
