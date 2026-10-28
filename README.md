# claude-skills

Version-controlled [Claude Code](https://docs.claude.com/en/docs/claude-code) skills, packaged as
plugins in one marketplace. Install once on any machine; update with one command.

## Install

Run these as **two separate commands**, one at a time, in Claude Code:

```
/plugin marketplace add cloudutsukpilot/claude-skills
```

```
/plugin install interactive-diagrams@cloudutsuk
```

If you go through the `/plugin` menu instead (**Add marketplace**), type only
`cloudutsukpilot/claude-skills` in the source box. Pasting both lines together gives
`… is not a valid GitHub owner/repo shorthand`.

Or from a terminal, outside Claude Code:

```bash
claude plugin marketplace add cloudutsukpilot/claude-skills && claude plugin install interactive-diagrams@cloudutsuk
```

Restart Claude Code. `/plugin` → **Installed** lists `interactive-diagrams`, and the skills appear as
`interactive-diagrams:diagram-level-1`, `-2` and `-3`.

Update later:

```
/plugin marketplace update cloudutsuk
```

Every release is a git tag (`interactive-diagrams-v1.0.0`); see [CHANGELOG.md](CHANGELOG.md) for
what changed. To stay on a release, check out its tag in a local clone and add that folder as the
marketplace (`/plugin marketplace add ~/path/to/claude-skills`).

### For a team or a project

Commit this to the project's `.claude/settings.json`; everyone who trusts the project is offered the
marketplace and the plugin:

```json
{
  "extraKnownMarketplaces": {
    "cloudutsuk": { "source": { "source": "github", "repo": "cloudutsukpilot/claude-skills" } }
  },
  "enabledPlugins": { "interactive-diagrams@cloudutsuk": true }
}
```

## Plugins

| Plugin | Skills | What it makes | Needs |
|---|---|---|---|
| [interactive-diagrams](plugins/interactive-diagrams/) | `diagram-level-1`, `diagram-level-2`, `diagram-level-3` | Explorable architecture diagrams as one self-contained HTML page | Python 3 + PyYAML; Node + Chromium for the browser check |

### interactive-diagrams: which level?

| Level | Skill | Adds | Pick it when |
|---|---|---|---|
| 1 | `diagram-level-1` | Components nested in levels (C4-style), pan and zoom, a facts panel per component, arrows with why, protocol and port | You want a map of the system: what exists, where it runs, what talks to what. The default |
| 2 | `diagram-level-2` | Level 1 + certificates on every arrow, the exchange on the wire (TCP → TLS → HTTP …) when you click an arrow, view tabs (observability, security, CI/CD) | Security, networking or TLS matter, or the diagram is too busy and needs tabs |
| 3 | `diagram-level-3` | Level 2 + guided use cases: a packet travels the arrows step by step and back, banners per step, a success/fail outcome; optional world map | You want to explain a flow: a request's journey, a deploy, an alert, a failure |

See all three levels in one diagram: [examples/web-shop](plugins/interactive-diagrams/examples/web-shop/)
(download `index.html` and open it in a browser).

## Using the diagram skills

Start Claude Code in the project the diagram belongs to. Each skill writes to the same standard layout:

```
diagrams/<name>/
├── diagram.yml     # the source: edit this, or ask Claude to
├── index.html      # the built page: open it in a browser, host it, or embed it with an <iframe>
└── logos/          # optional local logo files
```

Every level runs the same steps: **intake** (it reads what you point at and asks, in one message, for
the facts it can't find) → **model** → **write** `diagram.yml` → **validate** → **build** `index.html`
→ **check** it in a real browser (light, dark, phone) → **report**. It never invents ports, hostnames
or certificates: give it docs, code, manifests or answers.

Ask in plain words (Claude picks the level from what you ask for), or name the skill to force a
level: `/interactive-diagrams:diagram-level-2`.

### Level 1: structure

```
Create an interactive architecture diagram of this repo's services.
Use docker-compose.yml and the README.
```

```
/interactive-diagrams:diagram-level-1 our payments platform: see docs/architecture.md and k8s/
```

You get level 0 (the system, its users and external services), then one layer per level below
(clusters → services → components). Click a component to open it, click its ⓘ for status, summary,
how it works, links and API. Arrows show `HTTPS :443`-style pills and say why each path exists.

### Level 2: connections

```
Make a level 2 diagram of the platform: show which certificate secures each connection,
where TLS terminates, and put logs/metrics and CI/CD in their own tabs.
```

```
/interactive-diagrams:diagram-level-2 raise diagrams/payments/diagram.yml to level 2
```

Everything from level 1, plus: click an arrow to see the whole exchange as an animated sequence
diagram (TCP handshake, TLS 1.3 or mTLS, then HTTP, gRPC, OIDC, Kafka …) and its certificates (issuer,
validity, where stored, why trusted), or why the hop has none. Cross-cutting arrows move into view
tabs so the main flows stay readable. Expect questions about who terminates TLS and which CA issues
each certificate; it checks with `openssl` / `kubectl` where it can.

### Level 3: stories

```
Create a level 3 diagram of the shop with use cases for "browse a product",
"place an order" and "payment declined".
```

```
/interactive-diagrams:diagram-level-3 add a "deploy a new version" walkthrough to diagrams/payments/diagram.yml
```

Everything from level 2, plus a **Use cases** sidebar: Play sends a packet hop by hop along the real
arrows (and back for replies), each step shows a banner line, and the last step celebrates the
outcome. A use case can have an alternative mode ("simulate a cache hit"). For multi-region systems,
components can be pinned on a world map.

### Raising a diagram to the next level

Levels only add keys, so the same `diagram.yml` grows: ask for level 2 or 3 on an existing file and it
keeps everything already there.

### Without Claude

The scripts work on their own (Python 3 + PyYAML):

```bash
P=~/.claude/plugins/marketplaces/cloudutsuk/plugins/interactive-diagrams   # or your clone of this repo
mkdir -p diagrams/my-system && cp $P/templates/level-1.yml diagrams/my-system/diagram.yml   # edit it
python3 $P/scripts/validate.py diagrams/my-system/diagram.yml --level 1
python3 $P/scripts/build.py diagrams/my-system/diagram.yml            # → diagrams/my-system/index.html
```

Every key, with the level that introduces it:
[reference/data-format.md](plugins/interactive-diagrams/reference/data-format.md).

## Repository layout

```
.claude-plugin/marketplace.json     # the catalog: every plugin in this repo
plugins/<plugin>/
├── .claude-plugin/plugin.json      # name, version, description
├── skills/<skill>/SKILL.md         # one folder per skill
├── scripts/  engine/  reference/   # shared by the plugin's skills
├── templates/  examples/
└── README.md
docs/adding-a-skill.md              # how to add or change a skill, versioning and releases
CHANGELOG.md
```

Adding or changing a skill: [docs/adding-a-skill.md](docs/adding-a-skill.md).

## License

[MIT](LICENSE)
