#!/usr/bin/env bash
# This repo's checks for the software factory. Exit 0 only when a branch is fit to review.
#
# The gate runs the base branch's copy of this file with the job's worktree as the working
# directory. Keep it fast, deterministic and non-interactive: no watch modes, no prompts, nothing
# that rewrites files. $FACTORY_CHANGED is a file listing the paths the branch changed, one per line,
# and $FACTORY_BASE is the ref it is compared with (origin/main).
#
# /factory init replaces the lines below with the repo's real commands, for example:
#   npm ci --prefer-offline && npm run lint && npm test && npm run build
set -euo pipefail

echo ".factory/checks.sh has no checks yet: add this repo's lint, test and build commands." >&2
exit 1
