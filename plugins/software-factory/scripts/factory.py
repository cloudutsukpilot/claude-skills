#!/usr/bin/env python3
"""The software factory's spine: the only writer of .factory/jobs/<job>/job.json.

Every stage change goes through this script, which checks the files that justify it and refuses
anything else. The deterministic work (worktrees, the gate, pushing, the pull request, labels of
state) happens here too, so the orchestrator never improvises it. Run it from anywhere inside the
repo's main checkout.

Usage:
  factory.py init-check                 is this repo set up? prints what is missing
  factory.py queue                      what /factory run should do: new features and unfinished jobs
  factory.py create <feature>           new job for a `ready` feature (number, slug or path); prints the job id
  factory.py advance <job> <stage>      move a job to <stage>, or refuse
  factory.py gate <job>                 run the base branch's .factory/checks.sh in the worktree
  factory.py review-done <job>          after a review round: → approve, build or needs-human
  factory.py finish <job>               after the approver: PR ready + comment, → recommended or needs-human
  factory.py feedback <job>             recommended/needs-human → build, with stdin as feedback-<k>.md
  factory.py answer <job>               needs-info → intake, with stdin as answer-<k>.md
  factory.py reject <job>               any open job → rejected, with stdin as rejection.md
  factory.py sync                       mark jobs whose PR was merged or closed; remove their worktrees
  factory.py status [<job>]             table of jobs, or one job's json
  factory.py prompt <job> <role>        the opening line every agent prompt starts with
  factory.py check <feature>            is a feature ready to run unattended? fixed rules, then the folder and
                                        prompt line for intake's preflight (a file path, or a feature on the base)

<job> is a job id (004-dark-mode) or its number (4).

FACTORY_NON_INTERACTIVE=1 (CI): nobody answers during the run. Every prompt line says `Mode: non-interactive`,
and the agents decide with stated assumptions instead of stopping to ask.
"""

import fcntl
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REVIEWERS = ("code", "security", "ui", "infra", "docs")

TRANSITIONS = {
    "intake": {"spec", "needs-info", "rejected"},
    "needs-info": {"intake", "rejected"},
    "spec": {"build", "rejected"},
    "build": {"gate", "needs-human", "rejected"},
    "gate": {"review", "build", "needs-human", "rejected"},
    "review": {"approve", "build", "needs-human", "rejected"},
    "approve": {"recommended", "needs-human", "rejected"},
    "recommended": {"build", "rejected"},
    "needs-human": {"build", "rejected"},
}
TERMINAL = {"merged", "closed", "rejected"}
NON_INTERACTIVE = os.environ.get("FACTORY_NON_INTERACTIVE") == "1"
# Sections a feature needs before it runs unattended: reviewers and the approver judge against Done when.
REQUIRED_SECTIONS = ("What", "Why", "Done when")
WAITING = {"needs-info", "recommended", "needs-human"}


class Refused(Exception):
    pass


# ---------------------------------------------------------------- helpers

def sh(*args, cwd=None, check=True, input=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                       **({"input": input} if input is not None else {"stdin": subprocess.DEVNULL}))
    if check and r.returncode != 0:
        raise Refused(f"`{' '.join(args)}` failed: {(r.stderr or r.stdout).strip()}")
    return r.stdout.strip()


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def repo_root():
    top = sh("git", "rev-parse", "--show-toplevel", check=False)
    if not top:
        raise Refused("not inside a git repository")
    common = Path(sh("git", "rev-parse", "--path-format=absolute", "--git-common-dir"))
    # From inside a worktree, the main checkout is the parent of the common .git dir.
    return common.parent if common.name == ".git" else Path(top)


REPO = repo_root() if __name__ == "__main__" else None


def jobs_dir():
    return REPO / ".factory" / "jobs"


def load_config():
    cfg = json.loads((PLUGIN / "templates" / "config.json").read_text())
    local = REPO / ".factory" / "config.json"
    if local.exists():
        for k, v in json.loads(local.read_text()).items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k] = {**cfg[k], **v}
            else:
                cfg[k] = v
    return cfg


def worktree_root():
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    tag = hashlib.sha1(str(REPO).encode()).hexdigest()[:6]
    return base / "software-factory" / "worktrees" / f"{REPO.name}-{tag}"


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "#")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.split(" #")[0].strip().strip("\"'")
    return out


def first_line(path):
    return path.read_text().splitlines()[0].strip() if path.exists() and path.read_text() else ""


def header(path):
    """KEY: value lines at the top of an agent file, up to the first blank line."""
    out = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            break
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().upper()] = v.strip()
    return out


def resolve(job):
    d = jobs_dir()
    if job.isdigit():
        hits = sorted(d.glob(f"{int(job):03d}-*")) if d.exists() else []
        if not hits:
            raise Refused(f"no job numbered {job}")
        return hits[0].name
    if not (d / job).is_dir():
        raise Refused(f"no job {job}")
    return job


def read_job(job):
    return json.loads((jobs_dir() / job / "job.json").read_text())


def write_job(data):
    path = jobs_dir() / data["id"] / "job.json"
    data["updated"] = now()
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f, indent=2)
        f.write("\n")
    tmp.replace(path)


def move(data, stage, note=""):
    cur = data["stage"]
    if stage not in TRANSITIONS.get(cur, set()):
        raise Refused(f"{data['id']}: {cur} → {stage} is not allowed")
    data["stage"] = stage
    data.setdefault("history", []).append({"at": now(), "stage": stage, **({"note": note} if note else {})})
    write_job(data)


def changed_files(data):
    wt, base = data["worktree"], data["base"]
    out = sh("git", "diff", "--name-only", f"origin/{base}...HEAD", cwd=wt)
    return [p for p in out.splitlines() if p]


def matches(paths, globs):
    # fnmatch's `*` also matches `/`, so `dir/**` covers everything under dir.
    return sorted({p for p in paths for g in globs if fnmatch.fnmatch(p, g)})


def gh_repo():
    return sh("gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner", cwd=REPO)


# ---------------------------------------------------------------- commands

def cmd_init_check():
    missing = []
    for p in (".factory/checks.sh", ".factory/.gitignore", "docs/features", "docs/plans"):
        if not (REPO / p).exists():
            missing.append(p)
    if not any((REPO / n).exists() for n in ("AGENTS.md", "CLAUDE.md")):
        missing.append("AGENTS.md (or CLAUDE.md)")
    if sh("git", "remote", cwd=REPO, check=False) == "":
        missing.append("a git remote")
    if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        missing.append("gh auth (run: gh auth login)")
    print("ready" if not missing else "missing: " + ", ".join(missing))


def features_on_base(cfg):
    base = cfg["base_branch"]
    sh("git", "fetch", "-q", "origin", base, cwd=REPO)
    names = sh("git", "ls-tree", "--name-only", f"origin/{base}", "docs/features/", cwd=REPO, check=False)
    out = []
    for path in names.splitlines():
        stem = Path(path).stem
        if not re.match(r"\d{3}-", stem):
            continue
        meta = frontmatter(sh("git", "show", f"origin/{base}:{path}", cwd=REPO))
        out.append({"id": stem, "path": path, "status": meta.get("status", ""),
                    "title": meta.get("title", ""), "priority": int(meta.get("priority", 999) or 999)})
    return sorted(out, key=lambda f: (f["priority"], f["id"]))


def cmd_queue():
    cfg = load_config()
    jobs = {}
    if jobs_dir().exists():
        for d in jobs_dir().iterdir():
            if (d / "job.json").exists():
                j = json.loads((d / "job.json").read_text())
                jobs[j["id"]] = j
    rows = []
    for j in sorted(jobs.values(), key=lambda j: j["id"]):
        if j["stage"] in TERMINAL:
            continue
        action = "wait" if j["stage"] in WAITING else "resume"
        rows.append(f"{action}\t{j['id']}\t{j['stage']}\t{j['title']}")
    for f in features_on_base(cfg):
        if f["status"] == "ready" and f["id"] not in jobs:
            rows.append(f"new\t{f['id']}\tready\t{f['title']}")
    active = sum(1 for r in rows if r.startswith("resume"))
    mode = ", mode non-interactive" if NON_INTERACTIVE else ""
    print(f"concurrency {cfg['concurrency']}, active {active}{mode}")
    print("\n".join(rows) if rows else "nothing queued")


def cmd_create(feature):
    cfg = load_config()
    feats = features_on_base(cfg)
    hit = [f for f in feats if f["id"] == feature or f["id"].startswith(f"{feature.zfill(3)}-")
           or f["path"] == feature or f["id"] == Path(feature).stem]
    if not hit:
        raise Refused(f"no feature {feature} in docs/features/ on origin/{cfg['base_branch']}")
    f = hit[0]
    if f["status"] != "ready":
        raise Refused(f"{f['id']} has status '{f['status']}' on origin/{cfg['base_branch']}; only 'ready' runs")
    d = jobs_dir() / f["id"]
    if (d / "job.json").exists():
        j = read_job(f["id"])
        if j["stage"] not in TERMINAL:
            raise Refused(f"{f['id']} already has a job in stage {j['stage']}")
        old = d.with_name(f"{f['id']}.{datetime.now().strftime('%Y%m%d%H%M%S')}")
        d.rename(old)
    d.mkdir(parents=True)
    (d / "feature.md").write_text(sh("git", "show", f"origin/{cfg['base_branch']}:{f['path']}", cwd=REPO) + "\n")
    num = int(f["id"][:3])
    data = {
        "id": f["id"], "title": f["title"], "feature_path": f["path"], "base": cfg["base_branch"],
        "branch": f"factory/{f['id']}", "worktree": str(worktree_root() / f["id"]),
        "port": 5100 + 10 * (num % 100), "stage": "intake", "round": 0, "round_start": 0,
        "risk": None, "surfaces": [], "models": cfg["models"], "reviewers": {}, "reviews": {}, "pr": None,
        "created": now(), "history": [{"at": now(), "stage": "intake"}],
    }
    write_job(data)
    print(f["id"])


def setup_worktree(data):
    wt = Path(data["worktree"])
    if wt.exists():
        return
    wt.parent.mkdir(parents=True, exist_ok=True)
    sh("git", "fetch", "-q", "origin", data["base"], cwd=REPO)
    exists = sh("git", "rev-parse", "--verify", "--quiet", data["branch"], cwd=REPO, check=False)
    if exists:
        sh("git", "worktree", "add", str(wt), data["branch"], cwd=REPO)
    else:
        sh("git", "worktree", "add", "-b", data["branch"], str(wt), f"origin/{data['base']}", cwd=REPO)
        sh("git", "branch", "--unset-upstream", data["branch"], cwd=REPO, check=False)


def route(data, cfg):
    risk = data["risk"] or "medium"
    reviewers = {"code": cfg["routing"].get(risk, cfg["routing"]["medium"])["code"]}
    for s in set(data["surfaces"]) | set(cfg.get("always_reviewers", [])):
        if s in cfg["surface_reviewers"]:
            reviewers[s] = cfg["surface_reviewers"][s]
    data["reviewers"] = reviewers


def cmd_advance(job, stage):
    job = resolve(job)
    data, cfg = read_job(job), load_config()
    d = jobs_dir() / job
    cur = data["stage"]
    if cur == "intake":
        intake = d / "intake.md"
        if not intake.exists():
            raise Refused("intake.md is missing")
        h = header(intake)
        want = {"spec": "ACCEPT", "needs-info": "NEEDS-INFO", "rejected": "REJECT"}.get(stage)
        if h.get("DECISION") != want:
            raise Refused(f"intake.md says DECISION: {h.get('DECISION')}, not {want}")
        if stage == "spec":
            data["risk"] = h.get("RISK", "medium").lower()
            data["surfaces"] = [s.strip().lower() for s in h.get("SURFACES", "").split(",")
                                if s.strip().lower() in REVIEWERS]
            route(data, cfg)
            setup_worktree(data)
    elif cur == "needs-info" and stage == "intake":
        answers = len(list(d.glob("answer-*.md")))
        asked = len(list(d.glob("intake-*.md")))
        if answers <= asked:
            raise Refused("no new answer: use `factory.py answer`")
        n = asked + 1
        (d / "intake.md").rename(d / f"intake-{n}.md")
    elif cur == "spec" and stage == "build":
        if not (d / "spec.md").exists():
            raise Refused("spec.md is missing")
    elif cur == "build":
        status = first_line(d / "build.md")
        if stage == "gate" and status != "STATUS: READY":
            raise Refused(f"build.md starts with '{status}', not STATUS: READY")
        if stage == "needs-human" and status != "STATUS: BLOCKED":
            raise Refused(f"build.md starts with '{status}', not STATUS: BLOCKED")
        if stage == "gate":
            dirty = sh("git", "status", "--porcelain", cwd=data["worktree"])
            if dirty:
                raise Refused(f"the worktree has uncommitted changes:\n{dirty}")
            if sh("git", "branch", "--show-current", cwd=data["worktree"]) != data["branch"]:
                raise Refused("the worktree is not on the job's branch")
            push_and_pr(data)
    elif stage != "rejected":
        raise Refused(f"use the dedicated command to leave {cur}")
    move(data, stage)
    print(f"{job}: {stage}")


def push_and_pr(data):
    wt = data["worktree"]
    sh("git", "push", "-q", "-u", "origin", f"{data['branch']}:{data['branch']}", cwd=wt)
    if data.get("pr"):
        return
    d = jobs_dir() / data["id"]
    existing = sh("gh", "pr", "list", "--head", data["branch"], "--state", "open", "--json", "number,url",
                  "-q", '.[0] | "\\(.number) \\(.url)"', cwd=wt, check=False)
    if existing and existing.split()[0].isdigit():
        number, url = existing.split(" ", 1)
        data["pr"], data["pr_url"] = int(number), url
        return
    intake_scope = ""
    text = (d / "intake.md").read_text()
    m = re.search(r"## Scope\n(.*?)(\n## |\Z)", text, re.S)
    if m:
        intake_scope = m.group(1).strip()
    body = (f"Built by the software factory from [`{data['feature_path']}`]({data['feature_path']}).\n\n"
            f"## Scope\n{intake_scope}\n\n"
            f"The spec, build notes and reviews are in `.factory/jobs/{data['id']}/` in the main checkout. "
            f"This PR stays a draft until the factory's reviews pass; the factory never merges it.\n")
    url = sh("gh", "pr", "create", "--draft", "--base", data["base"], "--head", data["branch"],
             "--title", data["title"], "--body", body, cwd=wt)
    data["pr"] = int(url.rstrip("/").split("/")[-1])
    data["pr_url"] = url


def cmd_gate(job):
    job = resolve(job)
    data, cfg = read_job(job), load_config()
    if data["stage"] != "gate":
        raise Refused(f"{job} is in {data['stage']}, not gate")
    data["round"] += 1
    n = data["round"]
    rd = jobs_dir() / job / f"round-{n}"
    rd.mkdir(exist_ok=True)
    wt = data["worktree"]
    sh("git", "fetch", "-q", "origin", data["base"], cwd=wt)
    problems = []
    changed = changed_files(data)
    prot = matches(changed, cfg["protected_paths"])
    if prot:
        problems.append("The branch changes protected paths: " + ", ".join(prot))
    mt = subprocess.run(["git", "merge-tree", "--write-tree", "--name-only", f"origin/{data['base']}", "HEAD"],
                        cwd=wt, capture_output=True, text=True)
    if mt.returncode == 1:
        conflicts = [l for l in mt.stdout.splitlines()[1:] if l and not l.startswith(("Auto-merging", "CONFLICT"))]
        problems.append(f"The branch conflicts with origin/{data['base']} in: {', '.join(conflicts) or 'see git'}. "
                        f"Merge origin/{data['base']} into the branch and resolve.")
    checks = REPO / ".factory" / "checks.sh"
    log = rd / "checks.log"
    changed_list = rd / "changed.txt"
    changed_list.write_text("\n".join(changed) + "\n")
    env = {**os.environ, "FACTORY_CHANGED": str(changed_list), "FACTORY_REPO": str(REPO),
           "FACTORY_BASE": f"origin/{data['base']}"}
    try:
        r = subprocess.run(["bash", str(checks)], cwd=wt, env=env, capture_output=True, text=True, timeout=1800)
        log.write_text(r.stdout + r.stderr)
        if r.returncode != 0:
            problems.append(f"checks.sh exited {r.returncode}")
    except subprocess.TimeoutExpired:
        problems.append("checks.sh ran over 30 minutes")
    tail = "\n".join(log.read_text().splitlines()[-60:]) if log.exists() else ""
    verdict = "PASS" if not problems else "FAIL"
    (rd / "checks.md").write_text(
        f"GATE: {verdict}\n\n## Summary\n" + ("\n".join(f"- {p}" for p in problems) or "- All checks passed")
        + f"\n\n## Changed files\n" + ("\n".join(f"- {c}" for c in changed) or "- none")
        + f"\n\n## Last lines of checks.log\n```\n{tail}\n```\n")
    data["gate"] = verdict
    data["reviews"] = {r: "pending" for r in data["reviewers"]} if verdict == "PASS" else {}
    if verdict == "PASS":
        move(data, "review")
    elif n - data["round_start"] < cfg["max_rounds"]:
        move(data, "build", "gate failed")
    else:
        (jobs_dir() / job / "decision.md").write_text(
            f"ESCALATE\n\n## Summary\n- The gate still fails after {cfg['max_rounds']} rounds.\n\n"
            f"## For you\nRead round-{n}/checks.md and the worktree at {wt}.\n")
        move(data, "needs-human", "gate failed, rounds exhausted")
    print(f"{job}: round {n} gate {verdict} → {data['stage']}")


def cmd_review_done(job):
    job = resolve(job)
    data, cfg = read_job(job), load_config()
    if data["stage"] != "review":
        raise Refused(f"{job} is in {data['stage']}, not review")
    n = data["round"]
    rd = jobs_dir() / job / f"round-{n}"
    verdicts = {}
    for r in data["reviewers"]:
        line = first_line(rd / f"review-{r}.md")
        if line not in ("VERDICT: PASS", "VERDICT: CHANGES"):
            raise Refused(f"round-{n}/review-{r}.md is missing or does not start with a verdict")
        verdicts[r] = line.split()[-1]
    data["reviews"] = verdicts
    changes = [r for r, v in verdicts.items() if v == "CHANGES"]
    if not changes:
        move(data, "approve")
    elif n - data["round_start"] < cfg["max_rounds"]:
        move(data, "build", "changes from " + ", ".join(changes))
    else:
        (jobs_dir() / job / "decision.md").write_text(
            f"ESCALATE\n\n## Summary\n- Review rounds exhausted; CHANGES still open from: {', '.join(changes)}.\n\n"
            f"## For you\nRead round-{n}/review-*.md.\n")
        move(data, "needs-human", "review rounds exhausted")
    print(f"{job}: round {n} " + ", ".join(f"{r} {v}" for r, v in verdicts.items()) + f" → {data['stage']}")


def cmd_finish(job):
    job = resolve(job)
    data, cfg = read_job(job), load_config()
    if data["stage"] != "approve":
        raise Refused(f"{job} is in {data['stage']}, not approve")
    d = jobs_dir() / job
    decision = d / "decision.md"
    verdict = first_line(decision)
    if verdict not in ("RECOMMEND", "ESCALATE"):
        raise Refused("decision.md must start with RECOMMEND or ESCALATE")
    sh("git", "fetch", "-q", "origin", data["base"], cwd=data["worktree"])
    hot = matches(changed_files(data), cfg.get("escalate_paths", []))
    text = decision.read_text()
    if verdict == "RECOMMEND" and hot:
        verdict = "ESCALATE"
        text = ("ESCALATE\n\n> The approver recommended this, but it changes paths this repo always escalates: "
                + ", ".join(hot) + "\n" + text.split("\n", 1)[1])
        decision.write_text(text)
    wt = data["worktree"]
    sh("gh", "pr", "ready", str(data["pr"]), cwd=wt, check=False)
    sh("gh", "pr", "comment", str(data["pr"]), "--body-file", "-", cwd=wt,
       input=f"**Software factory: {verdict}** (round {data['round']})\n\n" + text.split("\n", 1)[1].strip()
       + "\n\nThe factory never merges. Merge this PR to accept it, or send feedback with `/factory feedback`.")
    move(data, "recommended" if verdict == "RECOMMEND" else "needs-human")
    print(f"{job}: {verdict} → {data['stage']} PR #{data['pr']}")


def next_file(d, prefix):
    k = 1
    while (d / f"{prefix}-{k}.md").exists():
        k += 1
    return d / f"{prefix}-{k}.md"


def cmd_feedback(job):
    job = resolve(job)
    data = read_job(job)
    if data["stage"] not in ("recommended", "needs-human"):
        raise Refused(f"{job} is in {data['stage']}; feedback goes to a job waiting for you")
    f = next_file(jobs_dir() / job, "feedback")
    f.write_text(sys.stdin.read().strip() + "\n")
    setup_worktree(data)
    data["round_start"] = data["round"]
    move(data, "build", f.name)
    print(f"{job}: {f.name} → build")


def cmd_answer(job):
    job = resolve(job)
    data = read_job(job)
    if data["stage"] != "needs-info":
        raise Refused(f"{job} is in {data['stage']}, not needs-info")
    f = next_file(jobs_dir() / job, "answer")
    f.write_text(sys.stdin.read().strip() + "\n")
    print(f"{job}: wrote {f.name}; now run: factory.py advance {job} intake")


def cleanup(data):
    wt = Path(data["worktree"])
    if wt.exists():
        sh("git", "worktree", "remove", "--force", str(wt), cwd=REPO, check=False)


def cmd_reject(job):
    job = resolve(job)
    data = read_job(job)
    if data["stage"] in TERMINAL:
        raise Refused(f"{job} is already {data['stage']}")
    (jobs_dir() / job / "rejection.md").write_text(sys.stdin.read().strip() + "\n")
    if data.get("pr"):
        sh("gh", "pr", "close", str(data["pr"]), "--comment", "Rejected in the software factory.", cwd=REPO,
           check=False)
    move(data, "rejected")
    cleanup(data)
    print(f"{job}: rejected")


def cmd_sync():
    if not jobs_dir().exists():
        print("no jobs")
        return
    for d in sorted(jobs_dir().iterdir()):
        if not (d / "job.json").exists():
            continue
        data = json.loads((d / "job.json").read_text())
        if data["stage"] in TERMINAL or not data.get("pr"):
            continue
        state = sh("gh", "pr", "view", str(data["pr"]), "--json", "state", "-q", ".state", cwd=REPO, check=False)
        if state in ("MERGED", "CLOSED"):
            data["stage"] = "merged" if state == "MERGED" else "closed"
            data.setdefault("history", []).append({"at": now(), "stage": data["stage"]})
            write_job(data)
            cleanup(data)
            sh("git", "branch", "-D", data["branch"], cwd=REPO, check=False)
            print(f"{data['id']}: PR #{data['pr']} {state.lower()}")
    print("synced")


def cmd_status(job=None):
    if job:
        print(json.dumps(read_job(resolve(job)), indent=2))
        return
    if not jobs_dir().exists():
        print("no jobs")
        return
    rows = []
    for d in sorted(jobs_dir().iterdir()):
        if (d / "job.json").exists():
            j = json.loads((d / "job.json").read_text())
            revs = " ".join(f"{r}:{v}" for r, v in j.get("reviews", {}).items())
            rows.append(f"{j['id']:<32} {j['stage']:<12} r{j['round']} {j.get('risk') or '-':<6} "
                        f"{'#' + str(j['pr']) if j.get('pr') else '-':<6} {revs:<40} {j.get('pr_url', '')}")
    print("\n".join(rows) or "no jobs")


def cmd_prompt(job, role):
    job = resolve(job)
    data = read_job(job)
    line = (f"Plugin: {PLUGIN}. Repo: {REPO}. Job folder: {jobs_dir() / job}/. "
            f"Worktree: {data['worktree']}. Branch: {data['branch']}. Base: origin/{data['base']}.")
    if role in ("builder", "ui"):
        line += f" Port: {data['port'] + (2 if role == 'ui' else 0)}."
    if role not in ("intake", "spec-writer"):
        line += f" Round: {data['round'] + (1 if role == 'builder' else 0)}."
    if NON_INTERACTIVE:
        line += " Mode: non-interactive."
    print(line)


# ---------------------------------------------------------------- preflight

def sections(text):
    """## heading -> body, with HTML comments and template placeholders (<...>) removed."""
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    out, name = {}, None
    for line in body.splitlines():
        m = re.match(r"##\s+(.+?)\s*$", line)
        if m:
            name = m.group(1)
            out[name] = ""
        elif name:
            out[name] += line + "\n"
    return {k: re.sub(r"^\s*<[^>\n]*>\s*$", "", v, flags=re.M).strip() for k, v in out.items()}


def component_ids():
    """Component ids from docs/project.yaml (portfolio-map's manifest), nested sub-components included."""
    manifest = REPO / "docs" / "project.yaml"
    if not manifest.exists():
        return None
    text = manifest.read_text()
    m = re.search(r"^components:\s*\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    return set(re.findall(r"^\s*-?\s*id:\s*[\"']?([\w.-]+)", m.group(1), re.M)) if m else set()


def feature_problems(text, cfg):
    meta = frontmatter(text)
    problems = []
    if not meta:
        return ["no frontmatter (a --- block with title and status)"]
    if not meta.get("title"):
        problems.append("frontmatter: no title")
    if meta.get("status") != "ready":
        problems.append(f"frontmatter: status is '{meta.get('status', '')}', only 'ready' runs")
    found = sections(text)
    for name in REQUIRED_SECTIONS:
        if not found.get(name):
            hint = " (observable checks, one per line: the reviewers and the approver judge against them)" \
                if name == "Done when" else ""
            problems.append(f"## {name} is missing or empty{hint}")
    comp = meta.get("component")
    ids = component_ids()
    if comp and ids is not None and comp not in ids:
        problems.append(f"component '{comp}' is not in docs/project.yaml (known: {', '.join(sorted(ids)) or 'none'})")
    if meta.get("priority") and not str(meta["priority"]).isdigit():
        problems.append(f"frontmatter: priority '{meta['priority']}' is not a whole number")
    return problems


def check_root():
    return worktree_root().parent.parent / "checks" / worktree_root().name


def cmd_check(feature):
    """Fixed rules for running a feature unattended, then a folder and prompt line for intake's preflight.

    A path is read from disk (a feature still on its branch, before the PR); anything else is looked up
    on the base branch. Nothing is written to the repo: the folder lives next to the worktrees."""
    cfg = load_config()
    path = Path(feature)
    if not path.is_absolute():
        path = Path.cwd() / path
    if path.is_file():
        text, stem = path.read_text(), path.stem
    else:
        hit = [f for f in features_on_base(cfg) if f["id"] == feature
               or f["id"].startswith(f"{feature.zfill(3)}-") or f["path"] == feature]
        if not hit:
            raise Refused(f"no feature {feature}: not a file, and not in docs/features/ on origin/{cfg['base_branch']}")
        text, stem = sh("git", "show", f"origin/{cfg['base_branch']}:{hit[0]['path']}", cwd=REPO), hit[0]["id"]
    if not re.match(r"\d{3}-[a-z0-9-]+$", stem):
        raise Refused(f"{stem}: feature files are named NNN-slug.md")
    problems = []
    if not (REPO / ".factory" / "checks.sh").exists():
        problems.append(f"{REPO.name} is not set up for the software factory: run /factory init and merge it")
    problems += feature_problems(text, cfg)
    folder = check_root() / stem
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.md"):
        old.unlink()
    (folder / "feature.md").write_text(text if text.endswith("\n") else text + "\n")
    print("problems: " + ("none" if not problems else str(len(problems))))
    for p in problems:
        print(f"- {p}")
    print(f"folder: {folder}/")
    print(f"prompt: Plugin: {PLUGIN}. Repo: {REPO}. Job folder: {folder}/. Worktree: none (read the code in "
          f"Repo). Base: origin/{cfg['base_branch']}. Mode: preflight.")
    if problems:
        raise Refused("fix the problems above, then check again")


def main(argv):
    cmds = {
        "init-check": (cmd_init_check, 0), "queue": (cmd_queue, 0), "create": (cmd_create, 1),
        "advance": (cmd_advance, 2), "gate": (cmd_gate, 1), "review-done": (cmd_review_done, 1),
        "finish": (cmd_finish, 1), "feedback": (cmd_feedback, 1), "answer": (cmd_answer, 1),
        "reject": (cmd_reject, 1), "sync": (cmd_sync, 0), "status": (cmd_status, None),
        "prompt": (cmd_prompt, 2), "check": (cmd_check, 1),
    }
    if not argv or argv[0] not in cmds:
        print(__doc__)
        return 2
    fn, n = cmds[argv[0]]
    args = argv[1:]
    if n is not None and len(args) != n:
        print(f"usage: factory.py {argv[0]} " + " ".join(["<arg>"] * n), file=sys.stderr)
        return 2
    try:
        fn(*args)
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
