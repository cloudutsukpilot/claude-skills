# Adding or changing a skill

## Standard structure

Every skill lives in a plugin. Related skills share one plugin, and anything they share (scripts,
engines, references, templates) sits at the plugin root, not inside a skill.

```
plugins/<plugin>/
├── .claude-plugin/plugin.json
├── README.md
├── skills/
│   └── <skill>/SKILL.md          # frontmatter: name + description (when to use it)
├── scripts/                       # shared tools the skills run
├── reference/                     # shared rules, loaded on demand by the skills
├── templates/                     # starter files
└── examples/                      # a complete, working example
```

Skills refer to the shared folders as `PLUGIN` = two folders above the skill's base directory, so a
skill never depends on where the plugin is installed.

### Tiered skills (`<topic>-level-<N>`)

When one job comes in richer versions, split it into levels instead of one huge skill:

- **Level 1** is the default: the smallest useful result, fewest prerequisites.
- **Each level includes the one before** and adds one clear capability. Its rules live in its own
  reference file (`structure.md` → `connections.md` → `stories.md`), and level N reads files 1..N.
- **Same sections in every level's SKILL.md:** a table of the levels, `0. Paths`, `1. Intake`,
  `2. Model`, `3. Write`, `4. Validate`, `5. Build`, `6. Check`, `7. Report`. Only the content of
  intake, model and the checks changes by level.
- **One template per level** (`templates/level-<N>.yml`) that validates cleanly at that level.
- **The validator takes `--level N`** so each tier is checked for what it promises and nothing more.
- Descriptions say when to pick *this* level and point to the others, so the right one triggers.

### Naming

- Plugin and skill names are lowercase with dashes and describe the job, not a product or a person
  (`interactive-diagrams`, `diagram-level-2`).
- No site-, blog- or company-specific paths, hosts or facts in a shared skill. Put those in the
  consuming project (its own `.claude/skills/` or `CLAUDE.md`), which can call the shared skill.

## Versioning and releases

Plugins follow [semantic versioning](https://semver.org) in `plugin.json` (and the matching entry in
`.claude-plugin/marketplace.json`):

| Change | Bump |
|---|---|
| Fix a typo, a validator false positive, a rendering bug | patch `1.0.x` |
| New optional key, new skill, new check that only warns | minor `1.x.0` |
| Rename a skill, remove or rename a data key, a check that now fails old files | major `x.0.0` |

Release:

1. Update `version` in `plugins/<plugin>/.claude-plugin/plugin.json` **and** in `marketplace.json`.
2. Add an entry to `CHANGELOG.md`.
3. Run the checks below.
4. Commit, open a PR, merge, then tag `main`: `git tag <plugin>-v<version> && git push --tags`.

Users on `main` get it with `/plugin marketplace update cloudutsuk`; users who pinned a tag stay
where they are until they move the pin.

## Checks before a PR

```bash
claude plugin validate .                              # marketplace manifest
claude plugin validate plugins/<plugin>               # plugin manifest and skills
```

For `interactive-diagrams`:

```bash
P=plugins/interactive-diagrams
for n in 1 2 3; do python3 $P/scripts/validate.py $P/templates/level-$n.yml --level $n; done
python3 $P/scripts/build.py $P/examples/web-shop/diagram.yml
eval "$(bash $P/scripts/setup.sh)"
CHROME=$CHROME node $P/scripts/preview.cjs --url "file://$PWD/$P/examples/web-shop/index.html" --id web-shop --out /tmp/diagram-preview/web-shop
```

## Trying a change locally before pushing

```
/plugin marketplace add ~/path/to/claude-skills
/plugin install interactive-diagrams@cloudutsuk
```

Or run Claude Code with `claude --plugin-dir ~/path/to/claude-skills/plugins/interactive-diagrams`.
