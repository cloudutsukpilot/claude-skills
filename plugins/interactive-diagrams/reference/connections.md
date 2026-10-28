# Level 2 rules: connections

Level 2 adds to [structure.md](structure.md): every arrow says how it is secured, what crosses the
wire, and cross-cutting arrows move into view tabs so the main flows stay readable.

## 1. TLS

`HTTPS`, `WSS`, `AMQPS`, `MQTTS`, `LDAPS` and port 443 imply TLS. Set `tls: true` where the source
says a hop is encrypted ("every service-to-service call is HTTPS"). The exchange then includes the TLS
1.3 handshake (mutual TLS when `certs` names a client certificate). SSH, WireGuard and DNS never get
TLS: they bring their own encryption, or none.

## 2. Certificates on every arrow (`certs`)

Say for each connection which certificate secures it, or why none does. The hover card shows a
one-line hint (🔒 name). The arrow's side panel shows the connection, then the exchange, then
**Certificates**: one collapsed line per certificate that expands to its details.

Describe each certificate once in a top-level `certs:` catalog and reference it from the edges:

```yaml
certs:
  pub-app:
    label: app.example.com           # the subject or name a reader recognises
    type: public                     # public | private | cluster | self | key (SSH, WireGuard)
    by: "The ingress controller (TLS ends there)"     # who presents it
    issuer: "Let's Encrypt R11 → ISRG Root X1; ACME DNS-01 via cert-manager"
    key: "ECDSA P-256 · TLS 1.3"                      # optional
    valid: "90 days; cert-manager renews it 30 days before expiry"
    stored: "Secret `app/app-tls`"                    # optional; never the secret itself
    trust: "Public chain: every browser and OS trusts ISRG Root X1"
edges:
  - {id: lb_app, …, certs: pub-app}                                      # the server's certificate
  - {id: svc_db, …, certs: {server: db-server, client: svc-client}}      # mutual TLS
  - {id: app_cache, …, certs: {none: "Plain TCP inside the cluster; TLS ended at the ingress."}}
  - {id: new_link, …, certs: {planned: "Planned: not designed yet."}}
```

- An edge's `certs` is a catalog id, `{server, client?, note?}` (ids or lists; a `client` makes it a
  mutual-TLS handshake), `{none: why}` for a plaintext hop, or `{planned: what is known}`.
- Where TLS ends at an ingress or load balancer, the certificate is presented `by` it, and the hop
  behind it is `none`.
- Bearer tokens, OIDC JWTs and API keys aren't certificates: mention them in `note` or the edge's
  `detail`.
- **Never** put a private key, a token or a secret URL in the catalog.
- Check the facts where you can instead of from memory: `openssl s_client -connect host:443
  -servername host </dev/null | openssl x509 -noout -subject -issuer -enddate` for what is served,
  `kubectl get certificates -A`, ingress annotations and Helm values for who terminates TLS. When you
  can't check, ask the user, or use `{planned: …}` / leave the field out and say so in the report.

## 3. The exchange (cards)

An arrow's panel shows **one looping, animated sequence diagram** of everything on the wire, grouped
on a bracket rail: the connection (TCP), its security (TLS 1.3, mTLS, or SSH's own key exchange) and
the conversation (HTTP, webhook, gRPC, OIDC …). The groups come from `proto`:

| proto | Cards |
|---|---|
| HTTPS | tcp, tls, http |
| Webhook | tcp, [tls], webhook |
| SSH | tcp, ssh |
| WireGuard | wireguard |
| OIDC | tcp, [tls], oauth |
| gRPC | tcp, [tls], grpc |

`cards: [tcp, tls, http]` overrides them, in order. Names: tcp, tls, mtls, http, websocket, sse,
grpc, kafka, amqp, mqtt, webhook, oauth, ssh, wireguard, kerberos, stream, query.

## 4. Views (tabs) for cross-cutting connections

Logs to a collector, audit trails, metrics scrapes, secret fetches, DNS lookups and image pulls connect
almost everything to everything; drawn all the time they bury the main flows. Put them in **views**:
tabs at the top of the canvas (`Main flows`, one tab per view, then a built-in `Show all`).

```yaml
views:
  - {id: observability, label: Observability, icon: chart}
  - {id: security, label: Security, icon: lock}
  - {id: networking, label: Networking, icon: router}
nodes:
  - {id: otel, label: OTel collector, icon: chart, views: [observability], status: built, facts: {…}}  # only in that view
edges:
  - {id: app_logs, from: app, to: otel, view: observability, kind: telemetry, why: "…", certs: …}
  - {id: app_idp, from: app, to: idp, view: security, main: true, why: "…", certs: …}   # main flow, also highlighted in Security
```

- **Which view:** telemetry (logs, metrics, traces, audit, alerts) → `observability`; identity,
  tokens, secrets, certificates, policy → `security`; DNS, tunnels, ingress, image pulls → `networking`.
  Add another view (for example `data`) only when it has at least 3 arrows. 2 to 5 views is right.
- **Delivery view.** When the system has a build and deploy path, add a `cicd` view (label `CI/CD`,
  icon `rocket`) that follows one change from commit to running workload: push, CI runner, secrets,
  tests and scans, image build, registry push, GitOps commit, deploy tool sync, apply, image pull.
- `view:` on an edge (a name or a list) puts it in that view and **hides it from the main view**. Add
  `main: true` when it is also a main flow.
- `views:` on a component shows it **only** in those views. Its arrows must be in one of them.
- **Always-on streams stay visible.** A continuous stream whose two ends are both main-view components
  gets `main: true` as well as its view, so its moving dots run on the main diagram.
- Keep the main view to about 45 arrows or fewer; the validator warns above that.
