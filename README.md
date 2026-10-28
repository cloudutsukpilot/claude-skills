# claude-skills

Version-controlled [Claude Code](https://docs.claude.com/en/docs/claude-code) skills, packaged as
plugins in one marketplace. Install once on any machine; update with one command.

## Install

In Claude Code:

```
/plugin marketplace add cloudutsukpilot/claude-skills
/plugin install interactive-diagrams@cloudutsuk
```

Restart Claude Code, then ask for a diagram ("create an interactive
architecture diagram of …") or name a skill (`diagram-level-2`).

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

| Level | Skill | Adds | Ask for it like |
|---|---|---|---|
| 1 | `diagram-level-1` | Components nested in levels (C4-style), pan and zoom, facts panels, arrows with protocol:port | "an interactive architecture diagram of our platform" |
| 2 | `diagram-level-2` | + certificates on every arrow, the exchange on the wire (TCP → TLS → HTTP …), view tabs | "… showing TLS and certificates", "level 2" |
| 3 | `diagram-level-3` | + guided use cases: packets travel the arrows step by step, with outcomes; geo map | "… with animated use cases", "a walkthrough of a checkout" |

See it: [examples/web-shop](plugins/interactive-diagrams/examples/web-shop/) (open `index.html`).

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
