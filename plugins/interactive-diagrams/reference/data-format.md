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
| `wrap`, `aspect` | 1 | `wrap: true` wraps a long single chain into rows |
| `min_zoom` | 1 | Opening zoom floor (default 0.62), so large diagrams open readable |
| `accent`, `accent2` | 1 | `#RRGGBB`: accent = focus, level buttons and tour trail; accent2 = the tour pointer |
| `nodes` | 1 | Required. The component tree (below) |
| `edges` | 1 | The arrows (below) |
| `certs` | 2 | Certificate catalog `{id: {label, type, by, issuer, valid, trust, key?, stored?, note?}}` |
| `views` | 2 | Tabs for cross-cutting arrows: `[{id, label, icon?}]`. `Main flows` is always first and `Show all` (id `*`) last; don't define `*` |
| `scenarios` | 3 | Use cases `[{id, title, summary?, modes?, steps}]` |
| `loop` | 3 | `true`: auto-play starts again after the last use case |
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

## Use-case step (`scenarios[].steps`)

| Key | Notes |
|---|---|
| `title`, `text` | Required. 2–5 words; 1–2 sentences under ~200 characters |
| `action` | Required. The banner line, under ~90 characters |
| `edges` | Arrows that run at the same time (one sender or one receiver) |
| `path` | Hops one after another; `~id` runs an arrow backwards (the response) |
| `lights` | Components to light without a packet |
| `when` | The mode this step belongs to |
| `clear` | Clear earlier highlights first |
| `result`, `outcome`, `at` | `success`, `done` or `fail` on the last step; the outcome text; where to celebrate |

## How it behaves

- **Layout:** ELK `layered`, left to right. Each open group is laid out on its own, and arrows that
  cross groups leave through ports on the group borders.
- **Level buttons** walk to a level one layer at a time; clicking a component opens or closes only it.
- **Opening view:** the whole diagram if it fits at a readable size, else a readable zoom on its start.
- **Interaction:** Ctrl/⌘ + wheel or pinch zooms (the page still scrolls); ⤢ is fullscreen. Hovering a
  component highlights its arrows; hovering an arrow shows its card; clicking opens the side panel
  (resizable, remembered per reader). Keyboard: Tab to a component, Enter to open it, arrow keys pan,
  `+` / `−` / `0` zoom.
- Nothing is kept in the URL: every load opens at `level` on the main view.
