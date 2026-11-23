# Level 3 rules: stories

Level 3 adds to [structure.md](structure.md) and [connections.md](connections.md): guided **use
cases** that replay one activity hop by hop, with a packet travelling the arrows and the outcome
celebrated at the end. Optionally, components can sit on a world map.

## 1. Use cases (scenarios)

The reader clicks a use case in the **Use cases** menu in the sidebar: it plays at once, in the player box, and stops after its last step (click it again, or another one, to play it). Each step
opens the groups its components sit in and closes the ones no later step needs; when the player
finishes, the diagram goes back to the reader's level, groups, view tab and zoom. (`loop: true` at the
top level plays the same use case again instead.)

```yaml
scenarios:
  - id: checkout
    title: Place an order
    summary: "Checkout, payment and the confirmation email."
    modes: [{id: normal, label: Normal}, {id: declined, label: "Simulate a declined card"}]   # optional
    steps:
      - {title: Press Pay, action: "Browser → CDN → API: POST /checkout", text: "…", path: [u_cdn, cdn_api]}
      - title: Load the cart
        action: "API ↔ Redis: read the cart"
        text: "…"
        path: [api_redis, ~api_redis]
        detail: |                                    # optional: shown with the Details box
          - The API reads the session key from the cookie and loads the cart from Redis on 6379.
          - An empty or expired cart stops the checkout here, before any charge.
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
  ("API ↔ PostgreSQL: insert the order"). It is the bold line on the step card.
- **`title`** (2 to 5 words) and **`text`** (1 or 2 sentences, under ~230 characters) on every step,
  naming the protocol and port where it matters. `text` says what the step does and why, not only
  where the packet goes ("The API asks the provider to charge the card; nothing is saved until it
  answers"), so the step card makes sense without opening anything.
- **`detail` on every step:** 3 to 10 short lines (under ~160 words) of
  Markdown: sentences, `- ` lines for a list, a blank line between paragraphs, `code` for names. It
  shows on the step card instead of `text` when the reader ticks **Details** in the player
  (`details: true` at the top level starts with it ticked; the reader's choice is remembered in their
  browser). Say what happens inside the step that the arrow can't show: which function or check
  runs, what it decides, what happens when it refuses, and what the next step depends on. Don't
  repeat `text` or the arrow's `why`. A step without `detail` still changes with Details: the card
  shows its `text` and then each hop it makes (from → to, protocol:port and the arrow's `why`), so
  Details never does nothing; `validate.py` lists the steps that rely on that. Auto-play stays on a step long enough to read its detail
  (about 250 words a minute, at most 25 s; the speed button scales it). Give every use case at least
  one; the validator warns when a use case has none.
- **`detail` for a semi-technical reader** (leadership, product, a new team member), when the
  diagram is for them: give every step one, and write it as three short paragraphs with bold
  leads, each one or two plain sentences:
  - `**What happens:**` the function or check that runs, in `code` (`check_action()`), and what it
    does in everyday words;
  - `**Why it matters:**` the risk it removes or the guarantee it gives (cost, safety, audit, a
    person in the loop);
  - `**How:**` the mechanism and its numbers (limits, retries, timeouts), or a short `- ` list.
  Explain each term the first time it appears ("Temporal, the workflow engine that remembers how
  far each run got"), say known gaps plainly, and set `details: true` so the card opens with them.
- **The player box** across the bottom of the canvas (left of the side panel when one is open and
  the canvas has room, over the panel's foot when it does not) is the one place for the description
  and the player. The description takes the width on the left and the box is as tall as it needs (a
  long description scrolls inside it); the controls sit on the right in a 2 x 4 grid with the toggles
  under it (on a phone, in a row under the description). It
  shows only while a use case runs: a click on a use case opens it, it stays through every step (also
  when paused), and it goes 5 seconds after the last step completes, or at once with its close button
  (which stops the use case and puts the reader's layout back). There is none before a use case is
  played. Its head shows `n/N`, the use case's title and the close button; then the step's `title`,
  the banner line (`action`, then the outcome) and `text` or `detail`, with the close button in the
  box's corner. With Details on, the same box grows taller and a longer `detail` scrolls inside it.
  While it is up, the camera frames each step in the room above it.
- **The packet rests on its target.** Once a packet reaches the end of its hop it stays there for 2
  seconds (at 1x; the speed button shortens it), breathing softly, so a reader can press it and
  inspect it; then the next hop starts. A step with many hops takes 2 seconds more per hop.
- **Drag lock.** The hand at the foot of the sidebar (or `drag_lock: true` at the top level) keeps the
  view where the reader put it: dragging and the arrow keys stop panning, and use cases stop moving the
  camera to each step and to the outcome, so packets travel across the view as framed. Zoom (the
  buttons, Ctrl + scroll, pinch, +/-) and Fit still work.
- **The packet.** Each hop is drawn as a small packet (a frame with a header strip and the arrow's
  protocol on it, a chevron showing which way it goes): requests in `accent2`, replies green.
- **The packet inspector.** A press on a moving packet, or the magnifier in the player's controls,
  pauses the use case and opens the side panel on that step's hops (one tab per hop), layer by layer
  like a packet capture: **Network** (source and destination components), **Transport** (TCP or UDP,
  the server's port, the client's ephemeral one), **Security** (TLS or mTLS with the certificates from
  `certs`, or why there is none), **Application** (the protocol's message, then the packet's own
  `line` and `headers`) and **Payload** (`body`, with its size and a Copy button). The step counts
  as reached, so Next and Play go on from the next step, and the inspector follows the steps until
  another panel opens. Every hop gets the first three layers from its arrow. Record the content
  (`packets` on a step, or `packet` / `reply` on an arrow used the same way everywhere) for the hops
  that teach the most: **1 to 3 per use case** (the request that starts it, the call that decides
  the outcome, the event that ends it), not every hop. Copy it from the code, an API schema or a
  captured request and name that in `source`; anything shortened or invented gets
  `illustrative: true`. No real tokens, keys, passwords or private hosts: use placeholders.
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
- **The player's controls** are at the foot of the player box: play/pause, previous, next,
  restart, speed, the layout padlock, the packet inspector, the alternative mode and Details. They exist only while a use
  case runs, so nothing sits on the canvas otherwise. There are no per-step dots: the `n/N` count in
  the box's head is the progress.
- **Lock mode.** The padlock in the player (or `lock: true` at the top level) plays use cases on the
  reader's layout: their level, the components they opened and their view tab. Nothing opens or
  closes; the camera still moves to each step. A packet aimed inside a closed component travels to
  that component; a hop with both ends inside one closed component, or on an arrow the tab hides,
  pulses the component and the banner says so ("· inside Backend"). Set `lock: true` when the
  use cases read well at the start `level` and opening groups would distract.
- **Steps grouped by a closed component (lock mode).** Consecutive steps whose every hop starts and
  ends inside the same closed component (or that only light components inside it) play as one step:
  one card titled "Inside Backend · 3 steps" lists each step's title and `text` (its `detail` with
  Details on), the `n/N` count and the use case's step count in the menu drop to match, the banner
  line names the step that is moving, and the packet inspector has a tab for every hop of the group.
  A step that also leaves the component, or has `clear`, starts a new step. A use case keeps at least
  two steps: if grouping would fold all of it into one card, every step plays on its own. Opening the component, a
  deeper level or turning lock off shows the steps one by one again. So write each step for the
  deepest level: the grouping is the engine's job, and a step's `title` and `text` must still make
  sense in a list with its neighbours.

## 2. Geo backdrop (optional)

`map: {name: world, lon: [west, east], lat: [north, south], width, height}` draws a world map behind
the canvas; components with `lat` and `lon` are pinned to their place. Use it for multi-region systems
where the geography is the point (regions, edge locations, data residency).
