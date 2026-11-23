# Plan: packets and the packet inspector for interactive diagrams

**Status (2026-11-23):** In progress. Plugin 1.9.0 in review; the wardens diagram and the blog follow.

## Goal

In a use case, the moving dot becomes a packet, and the reader can open it and see what the hop
carries: who talks to whom, transport and ports, TLS and certificates, the application message and
its payload, like a packet capture.

## Decisions

See the 1.9.0 entry in `CHANGELOG.md`, `reference/stories.md` and `reference/data-format.md`: the
network, transport and security layers come from the arrow, so every hop has them; recorded content
is optional and kept to 1 to 3 hops per use case, copied from code (`source`) or marked
`illustrative`; no secrets (the validator rejects token-like values).

## Progress

| Step | Status | PRs | Left |
|---|---|---|---|
| 1. Plugin engine, validator, docs, example, version 1.9.0 | In progress (2026-11-23) | this branch | Review and merge, tag `interactive-diagrams-v1.9.0` |
| 2. platform-wardens diagram: packets for the key hops, copied from the code | In progress (2026-11-23) | branch `diagram-packets` | 16 packets on 12 steps in 4 use cases (webhooks, bus, incident start, model call, handoff, Slack, kill switch, MCP); review and merge after step 1 |
| 3. Blog engine (`sakharams.github.io`) and its `cloudutsuk-diagram` skill | In progress (2026-11-23) | branch `diagram-packet-inspector` | Engine, validator and docs ported; no blog diagram records packets yet (a public one, such as the GA4 page view, could) |

Waiting on you: reviewing and merging the PRs.
