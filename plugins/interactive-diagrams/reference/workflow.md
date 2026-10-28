# Workflow shared by every level

Every diagram skill runs the same seven steps; only steps 2 and 3 differ by level.

`PLUGIN` is the plugin folder: two levels above the skill's base directory (it holds `engine/`,
`scripts/`, `reference/`, `templates/` and `examples/`).

## Standard layout of a diagram

```
diagrams/<name>/
├── diagram.yml     # the source: the only file you edit
├── index.html      # built by build.py: one self-contained page (commit it, or rebuild in CI)
└── logos/          # optional: local logo files referenced as `icon: logos/<file>.svg`
```

`<name>` is lowercase with dashes (`payments-platform`); it becomes the DOM id `dgm-<name>` and the
preview's `--id`. Put `diagrams/` at the root of the user's current project unless they name another
place. Never put preview screenshots in the project.

## 1. Intake

Get the facts before drawing. Read what the user points at (docs, a README, IaC, Kubernetes
manifests, docker-compose, Helm values, code). Then list what is still missing and **ask the user in
one message**, grouped: components and where they run, protocols and ports, hostnames/URLs, (level 2)
who terminates TLS and which CA issues each certificate, (level 3) which activities to show as use
cases. Don't guess a fact you can't find; mark it `planned`, leave the optional key out, or ask.

## 2. Model, 3. Write

Start from `PLUGIN/templates/level-<N>.yml` (copy it to `diagrams/<name>/diagram.yml`) and follow the
level's rules: [structure.md](structure.md) (1), + [connections.md](connections.md) (2),
+ [stories.md](stories.md) (3). Every key: [data-format.md](data-format.md). A complete example:
`PLUGIN/examples/web-shop/diagram.yml`.

## 4. Validate

```bash
python3 "$PLUGIN/scripts/validate.py" diagrams/<name>/diagram.yml --level <N>
```

Fix every error and every warning (or tell the user why a warning stays). Needs Python 3 and PyYAML
(`pip install pyyaml` if the import fails).

## 5. Build

```bash
python3 "$PLUGIN/scripts/build.py" diagrams/<name>/diagram.yml      # → diagrams/<name>/index.html
```

It validates first and refuses to build on errors. The page works offline except for ELK (layout,
from jsDelivr) and Font Awesome (toolbar icons, from cdnjs).

**Embedding** in a site (Jekyll, Hugo, MkDocs, Docusaurus, a wiki): copy `index.html` into the site's
static files and embed it with
`<iframe src="/diagrams/<name>/index.html" style="width:100%;height:860px;border:0" loading="lazy"></iframe>`.

## 6. Check in a real browser

```bash
eval "$(bash "$PLUGIN/scripts/setup.sh")"        # once per machine: playwright-core + a Chromium
OUT="${TMPDIR:-/tmp}/diagram-preview/<name>"
CHROME=$CHROME node "$PLUGIN/scripts/preview.cjs" --url "file://$PWD/diagrams/<name>/index.html" --id <name> --out "$OUT"
```

`setup.sh` prints `SETUP FAILED: …` with the fix when npm or a Chromium is missing (for example
`cd ~/.cache/interactive-diagrams && npx playwright-core install chromium`). The preview checks, in
light, dark and phone views: layout at every level with no overlapping components, expand on click,
the hover card, the component panel, the arrow panel (exchange first, certificates below), view tabs,
zoom, the start level, the use cases, fullscreen and no script errors. It exits 1 on any failure.

Read at least `light-desktop-level1.png`, the deepest level, `panel.png` and `card.png`; at level 2
also `edge-panel.png` and the `view-*.png` files; at level 3 also `step-next.png` and `outcome.png`.
Fix what looks wrong (overlaps, a level with too many components, unreadable labels), rebuild and
check again.

## 7. Report

Tell the user: the file paths, what each level shows, the views and use cases, what you could not
verify (facts marked planned or left out), the preview result and the screenshots you read. Commit
only when the user asks.
