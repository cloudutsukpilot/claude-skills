# Plan: software-factory plugin

**Status (2026-11-19):** Phase 1 done: 0.1.0 merged, tagged and installed at user scope on the Spark. Phase 2 done: the first factory PR (job-hunter-agent#62) merged 2026-11-19.

## Goal

A `/factory` command I can run in any repo, from my user-level Claude Code install, that takes the
feature requests written in that repo's `docs/features/` folder and turns each into a reviewed pull
request: intake → spec → build → gate (the repo's own checks) → reviewers → approver. It never merges:
every pull request waits for me, because on most Cloudutsuk Platform repos a merge to `main` is a
deploy (Argo CD, Terragrunt apply on merge, Pages).

It is standalone. It doesn't use platform-wardens, Temporal, the wardens console or LiteLLM; it runs
in the Claude Code session that starts it, on my plan.

## Origin

The design follows the "software factory" from
[zazencodes-season-3](https://github.com/zazencodes/zazencodes-season-3/tree/main/src/software-factory-claude-code-v2)
(reviewed 2026-11-19): file-per-agent hand-offs, a scripted state machine as the only writer of job
state, a scripted gate before any reviewer, reviewers routed by risk, protected paths. That repository
is GPLv3, and this marketplace is MIT, so **no file is copied from it**; everything here is written
from scratch.

What differs from it:

| zazencodes v2 | software-factory |
|---|---|
| GitHub issues labelled `factory` are the queue | Feature files in `docs/features/` with `status: ready` (format in `plugins/software-factory/reference/feature-format.md`) |
| Approver merges what it is sure of | Approver recommends or escalates; I merge every PR |
| Installed by copying files into each repo | One plugin, installed at user scope; a repo only adds `.factory/` (checks, optional config and review lenses) |
| Reviewers: code, security, UX, UI | code, security, ui, infra (Kubernetes, IaC, CI), docs; a repo can add its own checklist per reviewer |
| Intake on Fable | Intake on Opus (configurable) |
| Cost read from transcripts | Not in v1 (transcript format isn't a documented interface) |

## Decisions (2026-11-19, with the owner)

- Lives in `cloudutsukpilot/claude-skills` as the `software-factory` plugin, installed at user scope so
  `/factory` works in any project.
- The queue is a folder of feature files in each repo's `docs/`, one standard format for every repo.
- The factory never merges (the safe default; the owner didn't choose otherwise).
- Job state is runtime data in `.factory/jobs/` (gitignored by `.factory/.gitignore`); worktrees live
  outside the repo in `~/.cache/software-factory/worktrees/`.

## Progress

| Phase | Status | PRs | What is left |
|---|---|---|---|
| 1. Plugin: skill, agents, `factory.py`, feature format, README | Done (2026-11-19) | #6 | Merged, tagged `software-factory-v0.1.0`, installed with `claude plugin install software-factory@cloudutsuk` (scope user). Tested: `claude plugin validate`; a scripted run of every stage of `factory.py` (refusals, routing, protected-path gate failure, feedback round, sync); one real headless `/factory run` on a scratch repo with a stub `gh` (intake → spec → build → gate → review → approver → recommended, correct code and test) |
| 2. Onboard the first repo (`.factory/` + `docs/features/`) and run one real feature | Done (2026-11-19): pilot job-hunter-agent | job-hunter-agent#60 (setup), #61 (feature 001), #62 (the factory's PR) | First job (stepper status change) ran 2026-11-19: intake ACCEPT (rescoped, medium, ui + docs), gate and all three reviews PASS in round 1, approver RECOMMEND; +395/−34 with ADR 0029 and tests (364 passed). Two orchestrator misreads on the way, fixed in 0.1.1 (#8). #62 merged 2026-11-19 and the job synced (worktree and branch removed). Its deploy waits on job-hunter-agent#63 (soupsieve CVE at the image gate, not from the factory) |
| 3. Onboard the other platform repos (GitOps, services, portal, IaC) with their checks and lenses | Planned | — | After the pilot |
| 4. Extras: dashboard page, cost per job, features that span repos | Planned | — | Only if the pilot shows a need |

### Waiting on the owner

- Merge claude-skills#8 (0.1.1).
