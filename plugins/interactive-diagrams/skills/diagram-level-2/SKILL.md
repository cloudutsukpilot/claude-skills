---
name: diagram-level-2
description: >-
  Create an interactive architecture diagram (everything diagram-level-1 does: nested levels, pan and
  zoom, facts panels, protocol:port arrows) plus the connection details: every arrow says which
  certificate secures it (issuer, validity, where it is stored, why it is trusted) or why the hop has
  none, clicking an arrow plays the whole exchange on the wire as one looping sequence diagram (TCP →
  TLS 1.3 / mTLS → HTTP, SSH, WireGuard, webhooks, gRPC, OIDC, Kafka, AMQP, MQTT, Kerberos …), and
  cross-cutting arrows (logs, metrics, secrets, DNS, image pulls, CI/CD) move into view tabs so the
  main flows stay readable. Output is one self-contained HTML page built from
  diagrams/<name>/diagram.yml and checked in a real browser. Use it when the user asks for a diagram
  that shows TLS, certificates, mTLS, "what happens on the wire", protocol handshakes, security or
  network paths, observability or CI/CD views, or says "level 2", or wants to raise a level-1
  diagram. For animated use cases or a guided walkthrough use diagram-level-3.
---

# Interactive diagram: Level 2 (connections)

| Level | Skill | Adds |
|---|---|---|
| 1 | diagram-level-1 | Components in levels, facts panels, arrows with why, protocol and port |
| **2** | **diagram-level-2** | Certificates on every arrow, the exchange on the wire, view tabs |
| 3 | diagram-level-3 | Use cases: packets travel the arrows step by step, with outcomes |

Level 2 includes everything in level 1. To raise an existing level-1 diagram, keep its file and add
the level-2 keys.

## 0. Paths

`PLUGIN` = two folders above this skill's base directory (it holds `engine/`, `scripts/`,
`reference/`, `templates/`, `examples/`). Read `PLUGIN/reference/workflow.md` once.

## 1. Intake

Everything level 1 asks, plus: where TLS terminates (load balancer, ingress, the app itself), which
CA issues each certificate and how it is renewed, which hops are mutual TLS, and which cross-cutting
flows exist (telemetry, identity and secrets, DNS and networking, build and deploy). Check
certificates where you can (`openssl s_client`, `kubectl get certificates -A`) rather than ask.

## 2. Model

Follow `PLUGIN/reference/structure.md`, then `PLUGIN/reference/connections.md`: a `certs:` catalog
used by every arrow (or `{none: why}` / `{planned: …}`), `tls: true` where a hop is encrypted, `cards`
only to override the exchange, and 2 to 5 `views` for cross-cutting arrows (always-on streams between
main components keep `main: true`).

## 3. Write

New diagram: copy `PLUGIN/templates/level-2.yml` to `diagrams/<name>/diagram.yml` and replace every
`<…>`. Keys: `PLUGIN/reference/data-format.md`. Full example: `PLUGIN/examples/web-shop/diagram.yml`.

## 4. Validate

`python3 "$PLUGIN/scripts/validate.py" diagrams/<name>/diagram.yml --level 2`; fix every error and
warning (at level 2 every arrow without `certs` and every unused certificate is reported).

## 5. Build

`python3 "$PLUGIN/scripts/build.py" diagrams/<name>/diagram.yml` → `diagrams/<name>/index.html`.

## 6. Check in a real browser

Run `setup.sh` and `preview.cjs` as in `workflow.md` step 6. Read `light-desktop-level1.png`, the
deepest level, `panel.png`, `card.png`, `edge-panel.png` (exchange first, certificates below) and each
`view-*.png`.

## 7. Report

Paths, what each level and view shows, which certificates you verified and which came from the user,
the preview result. Commit only when asked.
