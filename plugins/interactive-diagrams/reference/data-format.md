# Data format

One YAML file per diagram. The tier that introduces each key is in the **Level** column; a level-1
diagram only uses level-1 keys.

## Top level

| Key | Level | Notes |
|---|---|---|
| `title` | 1 | Required. The page title and the diagram's accessible name |
| `description` | 1 | One sentence under the page title (also the page's meta description) |
| `level` | 1 | Level shown on every load (default 1) |
| `levels` | 1 | Names for the level buttons, Level 0 first: `[Context, Containers, Components]` |
| `direction` | 1 | Root flow, default `right`; per group `direction: down` |
| `arrange`, `cols` | 1 | `arrange: flow` places every container's children in rows, left to right then top to bottom, in the order written (stable layout only); `cols` is the root row length (default: all in one row). Default `layered` (ELK) |
| `bands`, `hubs` | 1 | With `arrange: flow`: horizontal swimlanes `[{id, label?, main?}]`, top to bottom (labelled ones are drawn on the top level, with a header column); `hubs: false` stops components with 3+ incoming siblings moving to their own band |
| `wrap`, `aspect` | 1 | `wrap: true` wraps a long single chain into rows |
| `layout` | 1 | `stable` (default): every component keeps its place when another opens or closes. `auto`: the whole diagram is laid out again on every change (the behaviour before 1.4) |
| `min_zoom` | 1 | Opening zoom floor (default 0.62), so large diagrams open readable |
| `zoom_lock` | 1 | `true`: open with the zoom locked at the opening zoom (the padlock at the foot of the sidebar toggles it). While locked, buttons, Ctrl + scroll, pinch and +/- don't zoom, and level changes, Fit and use cases only pan |
| `accent`, `accent2` | 1 | `#RRGGBB`: accent = focus, level buttons and tour trail; accent2 = the tour pointer |
| `nodes` | 1 | Required. The component tree (below) |
| `edges` | 1 | The arrows (below) |
| `certs` | 2 | Certificate catalog `{id: {label, type, by, issuer, valid, trust, key?, stored?, note?}}` |
| `views` | 2 | Tabs for cross-cutting arrows: `[{id, label, icon?}]`. `Main flows` is always first and `Show all` (id `*`) last; don't define `*` |
| `scenarios` | 3 | Use cases `[{id, title, summary?, modes?, steps}]` |
| `loop` | 3 | `true`: Play repeats the selected use case instead of stopping after its last step |
| `details` | 3 | `true`: open with the Details box ticked, so the step card shows each step's `detail` (the reader's own choice, once made, wins) |
| `lock` | 3 | `true`: open in lock mode, so use cases play on the reader's layout without opening or closing components (the padlock in the player toggles it) |
| `tour` | 3 | Legacy single story `{title, modes?, steps}`; counts as one use case |
| `map` | 3 | Geo backdrop `{name: world, lon: [w, e], lat: [n, s], width, height}` |

## Component (`nodes`, nested through `children`)

| Key | Level | Notes |
|---|---|---|
| `id` | 1 | Required. Lowercase, digits, `-`, `_` |
| `label` | 1 | Required. Under ~28 characters |
| `sub` | 1 | A second line under the label |
| `icon` | 1 | Built-in name, `si:<slug>`, a file path relative to the YAML, or an https address |
| `color`, `tone` | 1 | Palette name or `#RRGGBB`; tone `ok`, `warn`, `fail` |
| `status`, `phase` | 1 | `built`, `planned`, `deferred`, `external`; phase only with planned/deferred |
| `facts` | 1 | `{summary, how, where?, when?, url?, api?}` ([structure.md](structure.md)) |
| `detail` | 1 | Extra notes, Markdown, under ~600 characters |
| `config` | 1 | `{title, lang, code}`, a real snippet, copied exactly |
| `direction` | 1 | `down` stacks a group's children |
| `arrange`, `cols` | 1 | `flow` (or `layered`) for this group only; `cols` = components per row (default up to 4) |
| `band` | 1 | The band (an id from the parent's `bands:`, the top level's for a top-level component) this component sits in; default the main band |
| `bands`, `hubs` | 1 | On a group: its own bands (labels are not drawn inside groups) and hub setting |
| `children` | 1 | Nested components |
| `views` | 2 | Shown **only** in these view tabs |
| `lat`, `lon` | 3 | Position on the `map` backdrop |

## Arrow (`edges`)

| Key | Level | Notes |
|---|---|---|
| `id`, `from`, `to` | 1 | Required. Ends are component ids, the deepest that really talk |
| `why` | 1 | Required. When the path is used or why it exists, under ~220 characters |
| `proto`, `port` | 1 | `HTTPS`, `PostgreSQL`, `OTLP gRPC` …; port 1–65535 |
| `kind` | 1 | request, stream, event, data, telemetry, control (when `proto` doesn't say) |
| `label`, `detail` | 1 | A short verb on the arrow; a technical note in its card and panel |
| `stream`, `both` | 1 | Moving dots on/off; dots both ways |
| `oneway` | 1 | No response comes back (also used by level-3 checks) |
| `dashed`, `tone` | 1 | Styling |
| `tls` | 2 | The hop is encrypted although `proto` doesn't say so |
| `certs` | 2 | A cert id, `{server, client?, note?}`, `{none: why}` or `{planned: what is known}` |
| `cards` | 2 | Override the exchange groups, in order |
| `view`, `main` | 2 | Put the arrow in a view tab (hidden from the main view unless `main: true`) |
| `when` | 3 | Only drawn in that use-case mode |
| `packet`, `reply` | 3 | What this arrow's request (`packet`) and response (`reply`) carry, for the packet inspector, whenever a use case sends it. Keys below; a step's `packets` overrides them |

## Use-case step (`scenarios[].steps`)

| Key | Notes |
|---|---|
| `title`, `text` | Required. 2–5 words; 1–2 sentences under ~230 characters, saying what the step does and why |
| `action` | Required. The banner line, under ~90 characters |
| `detail` | 3–10 short lines of Markdown (under ~160 words), shown on the step card, which grows a little for it, when the reader ticks Details. Without it, Details shows `text` and the step's hops (from → to, protocol:port, the arrow's `why`) |
| `edges` | Arrows that run at the same time (one sender or one receiver) |
| `path` | Hops one after another; `~id` runs an arrow backwards (the response) |
| `lights` | Components to light without a packet |
| `packets` | What this step's hops carry, for the packet inspector: `{<edge id>: packet, ~<edge id>: reply packet}`; each key must be a hop of this step |
| `when` | The mode this step belongs to |
| `clear` | Clear earlier highlights first |
| `result`, `outcome`, `at` | `success`, `done` or `fail` on the last step; the outcome text; where to celebrate |

## How it behaves

- **Layout (`layout: stable`, the default):** ELK `layered` places the children of every container (the
  top level and each group) once, as closed components, with all arrows (every view and mode) lifted to
  them. Each component keeps that center. Opening a component grows it around its center to fit its
  children; only the components it would now touch move, straight away from it, and the push cascades
  outward. The component just opened stays where it is on screen (the camera does not pan; it only
  zooms out, around that component, if it no longer fits), and closing it puts everything back
  exactly. The layout follows the order components were opened in: opening one starts from the layout
  on screen, so a component pushed aside earlier stays where it is. A component hidden by the view tab keeps its space. Arrows are routed around the
  components (orthogonal, fewest bends); parallel arrows get their own lanes, and pills avoid each
  other and the components.
- **Layout (`layout: auto`):** ELK lays out the whole visible diagram again after every change; each
  open group is laid out on its own, and arrows that cross groups leave through ports on the group
  borders. Compact, but components can move anywhere when one opens.
- **Level buttons** walk to a level one layer at a time; clicking a component opens or closes only it.
- **Opening view:** the whole diagram if it fits at a readable size, else a readable zoom on its start.
- **Interaction:** Ctrl/⌘ + wheel or pinch zooms (the page still scrolls); ⤢ is fullscreen. Hovering a
  component highlights its arrows; hovering an arrow shows its card; clicking opens the side panel
  (resizable, remembered per reader). Keyboard: Tab to a component, Enter to open it, arrow keys pan,
  `+` / `−` / `0` zoom.
- Nothing is kept in the URL: every load opens at `level` on the main view.

## Packet (`packet`, `reply`, a step's `packets`)

What the packet inspector shows under Application and Payload for one hop. The Network, Transport and
Security layers come from the arrow itself (its ends, `proto`, `port`, `certs`), so they need nothing here.

| Key | Notes |
|---|---|
| `summary` | One sentence: what this packet asks or answers (the inspector's lead; default the arrow's `why`) |
| `line` | The first line on the wire: request line (`POST /v1/runs HTTP/1.1`), status line (`HTTP/1.1 202 Accepted`), the gRPC method, the SQL command, the Redis command |
| `headers` | A mapping (`Name: value`) or a list of `Name: value` lines: HTTP headers, gRPC metadata, message properties |
| `body` | The payload: a mapping or list (shown as JSON) or a string (`lang` says what it is). Keep the fields that explain the step and shorten the rest with `…` |
| `lang` | `json`, `yaml`, `sql`, `text`, `protobuf` … (default: `json` for a mapping or a string starting with `{`/`[`) |
| `note` | A short Markdown note under the packet (what a field means, what the receiver checks) |
| `source` | Where it was copied from: a file path, schema or doc. Required unless `illustrative` |
| `illustrative` | `true` when the content is shortened or made up to show the shape; the inspector labels it |

A packet needs one of `line`, `headers` or `body`. Never put a real token, key, password or private
address in one: write `<token>`, `<api key>`, `example.com`. `validate.py` rejects anything that looks
like a live token or key.

