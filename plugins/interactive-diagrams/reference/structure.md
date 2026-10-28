# Level 1 rules: structure

Every diagram, at every level, follows these rules. Levels 2 and 3 add to them; they never relax them.

## The source of truth

Facts come from the user, their docs, their code or their running systems: names, ports, hostnames,
schedules. Never invent one. When a fact is missing, ask the user (see "Intake" in the skill) or leave
the optional key out. For something that doesn't exist yet, set `status: planned` and say "Planned:".

## 1. Model the system as a tree

Think C4. **Level 0** is the system in its context: the people, the system itself and the external
systems it talks to, about 3 to 9 components. Each level below opens one more layer: clusters or
containers → areas → services → components.

- Group by **where things run** first (edge, clusters, regions, external SaaS), then by **purpose**
  (frontend, data, model serving). A group with 2 to 7 children reads best. If a level would show
  more than about 45 components, add an intermediate group.
- `direction: down` on a group stacks its children top to bottom. Use it when a group would otherwise
  be a very wide row (for example a host with 6 or more clusters).
- Name the levels: `levels: [Context, Containers, Components]` (one name per level, Level 0 first).
- `level:` is the level every load opens at. Keep the default, 1, unless the user asks for another.
- `id`: lowercase letters, digits, `-` and `_`. Keep `label` under about 28 characters; put the rest
  in `sub` (a second line) or in the facts.

## 2. Facts on every component

**Every component has `status` and `facts`, leaves and groups alike.** The side panel shows them by
importance: the name with a status badge, `where` and `when` as chips, the lead sentence, "How it
works", link buttons, then the API.

```yaml
- id: api
  label: Orders API
  icon: api
  status: built                 # built | planned | deferred | external; planned/deferred may add `phase: 2`
  facts:
    summary: "Owns carts and orders, and takes payments."
    how: "A REST API on Kubernetes; reads and writes PostgreSQL, caches sessions in Redis."
    where: "cluster `prod` · ns `shop`"
    when: "always on"
    url: {Swagger: https://api.example.com/docs}
    api: "`api.shop.svc:8080`"
```

| Key | Shows as | Rules |
|---|---|---|
| `status` (+ `phase`) | Badge next to the name | `built`, `planned`, `deferred` (amber on the canvas) or `external` (someone else's service). `phase` only with planned or deferred |
| `summary` | Lead sentence | Required. What it is **and** why it's here, one sentence, under ~200 characters. Don't restate the name |
| `how` | "How it works" | Required. Mechanism, protocol, auth, what it owns; 1 or 2 sentences, under ~280 characters |
| `where` | Chip | Optional, under ~60 characters: cluster · namespace, host:port, region. Leave it out when the group already says it |
| `when` | Chip | Optional, under ~60 characters: "always on", "every 6 h", "on deploy" |
| `url` | Link buttons | What a person opens: a map of button label to address (`{Console: https://…}`) or a bare address |
| `api` | Lines with Copy | What a program calls: a string or a list of Markdown; a single `code` span gets a Copy button |

Give at least one of `url` and `api`. A component without an address of its own says what reaches it
instead ("None of its own: `kubectl` against the cluster API"). Leave out an optional fact rather
than pad it. A group's facts describe the group (groups open their panel with the ⓘ button).

- `detail`: optional extra notes under the facts (numbers, caveats, 1 to 4 sentences, Markdown). Don't
  repeat the facts.
- `config`: `{title, lang, code}`, only when the user or the repo gives the real snippet; copy it
  exactly and say where it comes from in `title`.

## 3. Icons and colours

- `icon`: a built-in name (`validate.py` lists them when one is wrong): api, balancer, bell, bolt,
  browser, bucket, cert, chart, check, clock, cloud, cluster, code, container, cpu, cross, database,
  file, firewall, function, gear, git, globe, key, laptop, lock, mail, message, package, phone, queue,
  rocket, router, search, server, shield, terminal, user, users.
- A real logo: `si:<slug>` (a [Simple Icons](https://simpleicons.org) slug such as `si:kubernetes`,
  `si:postgresql`), or a file path relative to the YAML (`logos/acme.svg`, inlined at build time), or
  an https address.
- Colours: explicit `color` (blue, sky, teal, green, lime, amber, orange, red, rose, pink, violet,
  indigo, slate or `#RRGGBB`), else `tone` (ok, warn, fail), else the icon's role, else one per
  top-level component. `accent` and `accent2` at the top level colour the focus and the tour pointer.

## 4. Connect the deepest components

Write each arrow between the **deepest** components that really talk to each other. When a group is
collapsed the engine redraws the arrow to the group and merges parallel arrows (`HTTPS ×3`,
`2 links`), so one data set serves every level.

- **`why` on every arrow (required):** 1 or 2 short sentences, under ~220 characters, saying **when
  this path is used or why it exists**, from the reader's point of view. Start with the trigger
  (`Used when…`, `Every 6 hours…`, `Always on:`, `On a cache miss…`, `Planned:`), then the purpose.
- **Protocol and port** on every arrow between systems: `proto: PostgreSQL, port: 5432`. Use the
  source's values, else the product's default port ([protocols-ports.md](protocols-ports.md)).
- **Kind and colour** come from `proto`. Set `kind:` (request, stream, event, data, telemetry,
  control) when there is no protocol or it is unusual.
- **Movement:** streams and telemetry get continuous moving dots (`stream: true/false` overrides);
  WebSocket moves both ways (`both: true` for other duplex links).
- `label` is a short verb or note (`sync`, `every 6 h`). `detail` is an extra technical note shown in
  the arrow's card and panel. Quote flow-map values that contain a comma
  (`label: "metrics, logs, traces"`).
- `oneway: true` on fire-and-forget arrows (a commit, a notification, a queued event).

At level 1 the arrow panel already shows the protocol exchange it can infer from `proto` (TCP → TLS →
HTTP and so on). Level 2 adds the certificates, explicit cards and view tabs.
