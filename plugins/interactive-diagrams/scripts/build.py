#!/usr/bin/env python3
"""Build a diagram YAML file into one self-contained HTML page (engine, styles and data inlined).

  python3 build.py diagrams/<name>/diagram.yml [-o diagrams/<name>/index.html] [--title TEXT] [--no-validate]

The page needs a network connection for two things only: ELK (the layout library, loaded from jsDelivr
when the diagram first draws) and Font Awesome (toolbar icons, from cdnjs). Everything else is inside
the file, so it can be opened from disk, attached, hosted anywhere or embedded with an <iframe>.

Icons: a built-in name (`server`, `db`, ...) is drawn by the engine; a file path is read relative to the
YAML file and inlined as a data: URI; `si:<slug>` uses the Simple Icons logo of that name; an http(s)
address is used as is.

The DOM id is `dgm-<name>`, where <name> is the YAML file's folder (or its stem when the file is not
called diagram.yml). preview.cjs takes the same <name> as --id.
"""
import argparse
import base64
import html
import json
import mimetypes
import re
import subprocess
import sys
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parent.parent
ENGINE = PLUGIN / "engine"
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{}.svg"
FONT_AWESOME = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css"


def diagram_name(path):
    path = path.resolve()
    return path.parent.name if path.stem == "diagram" else path.stem


def resolve_icon(icon, base):
    """Turn a logo reference into something the engine can use as an <image href>."""
    s = str(icon)
    if s.startswith(("http://", "https://", "data:")):
        return s
    if s.startswith("si:"):
        return SIMPLE_ICONS.format(s[3:])
    if not re.search(r"[/.]", s):
        return s  # built-in icon name
    f = (base / s).resolve()
    if not f.is_file():
        sys.exit(f"ERROR logo {s!r} not found (looked for {f})")
    mime = mimetypes.guess_type(f.name)[0] or "image/svg+xml"
    return f"data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"


def resolve_icons(nodes, base):
    for n in nodes or []:
        if n.get("icon"):
            n["icon"] = resolve_icon(n["icon"], base)
        resolve_icons(n.get("children"), base)


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def fallback(data):
    """The no-JavaScript fallback: a nested list of components and the use cases' steps."""
    out = [f"<p><strong>{e(data['title'])}</strong></p>", "<ul>"]

    def item(n, depth):
        sub = f" ({e(n['sub'])})" if n.get("sub") else ""
        summary = (n.get("facts") or {}).get("summary") or n.get("detail") or ""
        text = f": {e(' '.join(str(summary).split()))}" if summary and depth < 2 else ""
        kids = n.get("children") or []
        inner = "<ul>" + "".join(item(c, depth + 1) for c in kids) + "</ul>" if kids else ""
        return f"<li><strong>{e(n['label'])}</strong>{sub}{text}{inner}</li>"

    out += [item(n, 0) for n in data["nodes"]] + ["</ul>"]
    scenarios = list(data.get("scenarios") or []) + ([data["tour"]] if data.get("tour") else [])
    for sc in scenarios:
        summary = f": {e(sc['summary'])}" if sc.get("summary") else ""
        out.append(f"<p><strong>{e(sc.get('title', 'Tour'))}</strong>{summary}</p><ol>")
        for st in sc.get("steps") or []:
            when = f" ({e(st['when'])})" if st.get("when") else ""
            out.append(f"<li><strong>{e(st.get('title'))}</strong>{when}: {e(st.get('text'))}</li>")
        out.append("</ol>")
    return "\n".join(out)


def figure(data, name):
    has_story = bool(data.get("scenarios") or (data.get("tour") or {}).get("steps"))
    title = e(data["title"])
    story_nav = ('<nav class="dgm-scenarios" role="tablist" aria-label="Use cases" hidden>'
                 '<span class="dgm-scenarios-head">Use cases</span></nav>') if has_story else ""
    controls = """<div class="dgm-controls" hidden>
<button type="button" class="dgm-btn dgm-btn-primary" data-act="play" aria-label="Play"><i class="fas fa-play" aria-hidden="true"></i></button>
<button type="button" class="dgm-btn" data-act="prev" aria-label="Previous step"><i class="fas fa-backward-step" aria-hidden="true"></i></button>
<button type="button" class="dgm-btn" data-act="next" aria-label="Next step"><i class="fas fa-forward-step" aria-hidden="true"></i></button>
<button type="button" class="dgm-btn" data-act="restart" aria-label="Restart"><i class="fas fa-rotate-left" aria-hidden="true"></i></button>
<button type="button" class="dgm-btn" data-act="speed" aria-label="Speed">1&times;</button>
<div class="dgm-dots" role="group" aria-label="Steps"></div>
<label class="dgm-toggle-mode" hidden><input type="checkbox" data-act="mode"> <span></span></label>
</div>""" if has_story else ""
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    map_data = ""
    if data.get("map"):
        land = json.loads((ENGINE / f"{data['map'].get('name', 'world')}.json").read_text())
        map_data = f'<script type="application/json" class="dgm-map-data">{json.dumps(land)}</script>'
    accent, accent2 = data.get("accent", "#38BDF8"), data.get("accent2", "#8B5CF6")
    return f"""<figure class="dgm" id="dgm-{e(name)}" data-icon-base="" style="--dgm-accent: {e(accent)}; --dgm-accent2: {e(accent2)};">
<div class="dgm-toolbar"></div>
<div class="dgm-body">
{story_nav}
<div class="dgm-stage" tabindex="0" aria-label="{title}: interactive diagram. Drag to pan, Control plus scroll or pinch to zoom, arrow keys to move.">
<svg class="dgm-svg" role="img" aria-label="{title}"></svg>
<div class="dgm-hint" aria-hidden="true">Ctrl + scroll (or pinch) to zoom</div>
<div class="dgm-card" role="tooltip" hidden></div>
<aside class="dgm-panel" hidden><button type="button" class="dgm-panel-close" aria-label="Close details"><i class="fas fa-xmark" aria-hidden="true"></i></button><div class="dgm-panel-body"></div></aside>
<p class="dgm-loading">Laying out the diagram…</p>
<div class="dgm-banner" role="status" aria-live="polite"></div>
</div>
</div>
<div class="dgm-legend"></div>
<figcaption class="dgm-caption" aria-live="polite" hidden><span class="dgm-counter"></span> <strong class="dgm-step-title"></strong> <span class="dgm-step-text"></span></figcaption>
{controls}
<div class="dgm-fallback">
{fallback(data)}
</div>
<script type="application/json" class="dgm-data">{payload}</script>
{map_data}
</figure>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("yaml", type=Path)
    ap.add_argument("-o", "--out", type=Path, help="output .html (default: index.html next to diagram.yml, else <name>.html)")
    ap.add_argument("--title", help="page title (default: the diagram's title)")
    ap.add_argument("--no-validate", action="store_true", help="skip validate.py")
    a = ap.parse_args()

    if not a.no_validate:
        r = subprocess.run([sys.executable, str(PLUGIN / "scripts/validate.py"), str(a.yaml)])
        if r.returncode:
            sys.exit("Not built: fix the validation errors above (or pass --no-validate).")

    data = yaml.safe_load(a.yaml.read_text())
    name = diagram_name(a.yaml)
    resolve_icons(data.get("nodes"), a.yaml.parent.resolve())
    out = a.out or a.yaml.with_name("index.html" if a.yaml.stem == "diagram" else f"{a.yaml.stem}.html")

    page = (ENGINE / "template.html").read_text()
    for key, value in {
        "TITLE": e(a.title or data["title"]),
        "DESCRIPTION": e(data.get("description", "")),
        "FONT_AWESOME": FONT_AWESOME,
        "CSS": (ENGINE / "diagram.css").read_text(),
        "FIGURE": figure(data, name),
        "JS": (ENGINE / "diagram.js").read_text(),
    }.items():
        page = page.replace("{{" + key + "}}", value)
    out.write_text(page)
    print(f"Built {out} ({out.stat().st_size // 1024} KB, id dgm-{name})")


if __name__ == "__main__":
    main()
