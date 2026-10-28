# Level 3 rules: stories

Level 3 adds to [structure.md](structure.md) and [connections.md](connections.md): guided **use
cases** that replay one activity hop by hop, with a packet travelling the arrows and the outcome
celebrated at the end. Optionally, components can sit on a world map.

## 1. Use cases (scenarios)

The reader picks a use case from a sidebar; Play runs it and auto-play moves on to the next. Each step
opens the groups its components sit in and closes the ones no later step needs; when the player
finishes, the diagram goes back to the reader's level, groups, view tab and zoom. (`loop: true` at the
top level starts again after the last use case.)

```yaml
scenarios:
  - id: checkout
    title: Place an order
    summary: "Checkout, payment and the confirmation email."
    modes: [{id: normal, label: Normal}, {id: declined, label: "Simulate a declined card"}]   # optional
    steps:
      - {title: Press Pay, action: "Browser → CDN → API: POST /checkout", text: "…", path: [u_cdn, cdn_api]}
      - {title: Load the cart, action: "API ↔ Redis: read the cart", text: "…", path: [api_redis, ~api_redis]}
      - {title: Card declined, action: "Payments → API: declined", text: "…", when: declined,
         path: [api_pay, ~api_pay], result: fail, outcome: "Payment declined"}
      - {title: Confirm, action: "API → CDN → Browser: confirmation", text: "…", when: normal,
         path: [~cdn_api, ~u_cdn], result: success, outcome: "Order placed"}
```

Rules:

- **One activity per use case**, 3 to 10 steps. Never mix two activities ("sign in" and "nightly
  sync") in one scenario; split it.
- **One action per step.** Each step is one hop: a request, a write, a callback. Several arrows in one
  step (`edges: [a, b]`) only when they happen at the same time from one sender or into one receiver.
- **Show every path the packet takes, including the way back.** `path: [api_db, ~api_db]` sends the
  packet to the database and back (a green return packet). `path` hops run one after another and must
  form one continuous route; `~id` runs an arrow backwards. A response that crosses several components
  returns hop by hop. If an arrow is missing for a real hop, add the arrow; never let a packet jump.
  Mark fire-and-forget arrows `oneway: true`; the validator flags any other request whose response
  never comes back.
- **A banner line on every step:** `action`, under ~90 characters, saying what is happening right now
  ("API ↔ PostgreSQL: insert the order").
- **`title`** (2 to 5 words) and **`text`** (1 or 2 sentences, under ~200 characters) on every step,
  naming the protocol and port where it matters.
- **End with the outcome:** the last step of each use case (and of each mode) has `result: success`,
  `done` or `fail` plus a short `outcome`. The engine celebrates at the last hop's target (`at: <id>`
  overrides): confetti and a check for success, a red cross and a shake for fail.
- Order steps as the data really flows (credentials before the call that needs them, the request
  before the reply).
- A use case can have **two modes** for an alternative path; `when: <mode id>` marks a step that only
  runs in that mode.
- `lights: [ids]` lights components without moving a packet (the first "you open the page" step).
- Pick use cases from what the system is for: signing in, the main request, a deploy, an alert, a
  batch job, a failure path. 2 to 6 use cases is typical.
- A single legacy `tour:` (`{title, steps}`) still works as one use case.

## 2. Geo backdrop (optional)

`map: {name: world, lon: [west, east], lat: [north, south], width, height}` draws a world map behind
the canvas; components with `lat` and `lon` are pinned to their place. Use it for multi-region systems
where the geography is the point (regions, edge locations, data residency).
