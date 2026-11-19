# software-factory

A software factory you can run in any repo. You write feature requests as files in `docs/features/`;
`/factory run` takes each `ready` one through a fixed pipeline of agents and scripts, and every
feature ends as a reviewed pull request. **The factory never merges**: you read the PR and merge it,
or send feedback for another round.

```
docs/features/NNN-slug.md (status: ready)
  → intake      worth building? at what scope? risk + surfaces      (or asks you, or rejects)
  → spec-writer spec.md with checkable acceptance criteria
  → builder     commits in its own worktree, build.md               ◄──────────┐
  → [script]    push factory/NNN-slug, open a draft PR                         │
  → gate        your .factory/checks.sh, protected paths, merge conflicts ─FAIL┤
  → reviewers   code + the lenses intake flagged, in parallel ───────CHANGES───┘
  → approver    RECOMMEND or ESCALATE, posted on the PR, PR marked ready
  → you         merge, or /factory feedback
```

The design follows the "software factory" idea from zazencodes (a fixed pipeline where scripts move
the state and agents only judge), written from scratch for this marketplace.

## Install

At user scope, so `/factory` works in every project:

```
/plugin marketplace add cloudutsukpilot/claude-skills
```

```
/plugin install software-factory@cloudutsuk
```

Restart Claude Code. The skill is `software-factory:factory` (type `/factory` and pick it). It needs
`python3`, `git` and an authenticated [`gh`](https://cli.github.com/) that can push to the repo.

## Set up a repo

In the repo, run `/factory init`. It writes:

```
.factory/.gitignore     jobs/  (job state is runtime data)
.factory/checks.sh      the repo's lint/test/build commands: the gate
.factory/config.json    optional overrides (models, reviewers, escalate_paths, …)
.factory/lenses/*.md    optional repo-specific checklists for reviewers
docs/features/README.md
```

and opens a PR with them. See [reference/repo-setup.md](reference/repo-setup.md).

## Use it

```
/factory new <description>      write docs/features/NNN-slug.md (status: ready) and open a PR for it
/factory run [<feature>]        work every ready feature (or one), `concurrency` at a time; resumes jobs
/factory status                 every job: stage, round, reviews, PR
/factory answer <job> <text>    answer intake's questions on a needs-info job
/factory feedback <job> <text>  another build round on a job waiting for you
/factory reject <job> <reason>  drop a job: closes its PR, removes its worktree
/factory sync                   mark jobs whose PR you merged or closed
```

Only features with `status: ready` **on the base branch** run, so queuing a feature is a reviewed
change too. The file format is in [reference/feature-format.md](reference/feature-format.md).

## What is where

| Piece | Path | Job |
|---|---|---|
| Orchestrator | `skills/factory/SKILL.md` | The session running `/factory`: spawns agents, calls the script |
| Agents | `agents/intake.md`, `spec-writer.md`, `builder.md`, `reviewer.md`, `approver.md` | Each reads files and writes exactly one |
| Review lenses | `reference/lenses/{code,security,ui,infra,docs}.md` | What each reviewer looks for; a repo adds to them in `.factory/lenses/` |
| Spine | `scripts/factory.py` | Only writer of `job.json`; refuses illegal moves; worktrees, gate, push, PR, sync |
| Defaults | `templates/config.json` | Models, routing, protected paths |

Per repo, at runtime:

- Job state: `<repo>/.factory/jobs/<job>/` (`job.json`, `feature.md`, `intake.md`, `spec.md`,
  `build.md`, `round-N/checks.md`, `round-N/review-<lens>.md`, `decision.md`).
- Worktrees: `~/.cache/software-factory/worktrees/<repo>-<hash>/<job>/`, on branch `factory/<job>`.

## Guardrails

- The factory pushes only `factory/*` branches and never merges, deploys or pushes to the base branch.
- The gate runs the base branch's `checks.sh`, and fails any branch that changes `.factory/**` or
  `.github/workflows/**` (configurable as `protected_paths`), so a branch can't change its own judge.
- `escalate_paths` (e.g. paths that deploy on merge) always escalate, whatever the approver said.
- Feature text, answers and feedback reach agents as data in files, never as their instructions.
  Intake, which reads the request first, has no shell.
- At most `max_rounds` build rounds per job before it waits for you.

## Cost

Every job runs several agents on your Claude plan: intake, spec, builder and approver on Opus by
default, the code reviewer on Sonnet (Opus for high risk), plus one reviewer per flagged lens. Start
with `concurrency: 1`, read every PR, and lower the models in `.factory/config.json` for small repos.
