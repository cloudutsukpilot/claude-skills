# Lens: code

- **Correctness:** it does what the spec's requirements say. Edge cases, missing awaits, unhandled
  errors, off-by-one, wrong paths, wrong defaults.
- **Simplicity:** the smallest change that fully meets the spec: no speculative options, fallbacks,
  hidden defaults or swallowed errors.
- **Reuse:** existing helpers, components and patterns, not new copies of them.
- **Tests:** new behaviour is tested where the repo has a test runner. Any test that was weakened,
  skipped, deleted or special-cased to pass is always CHANGES.
- **Conventions:** the repo's style as AGENTS.md and the neighbouring code show it.
- **Commits:** short one-line messages, nothing stray committed (build output, local config, secrets).
