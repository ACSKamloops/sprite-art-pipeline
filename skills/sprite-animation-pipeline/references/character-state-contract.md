# Character action bindings and physical clocks

Use a declared action catalog instead of hardcoding an inspector to the first
six actions. Validate unique direction/action identifiers, complete selected
bindings, manifest/PNG hashes, positive rational holds and known transitions.
Preserve the original preferred resource, not just a similarly named walk.

For the current unarmed example, the 17 states across eight directions bind
136 resources. These include held/reused poses and shared fall art; the source
catalog must distinguish those from new drawings and from art acceptance.

| State family | Behavioral contract |
| --- | --- |
| Idle/walk/run | Held movement, normalized diagonal direction, distinct run speed and art; releasing run returns to walk |
| Punch/cast | One-shot direction lock; explicit hit/release event data; return to the appropriate ready pose |
| Guard/crouch | Held state; release returns to locomotion/idle; do not claim an unseen transition drawing |
| Hurt/stun | Explicit interruption priority and duration |
| Dash/dodge | Separate root distances/profiles and body art; no implied invulnerability |
| Jump/land | Grounded anticipation, airborne height/travel, stationary ground shadow, explicit landing state |
| Knockdown/get-up | Fall then compatible supported-rise entry; compare the actual boundary pixels |
| Death | Shared fall art is allowed, but final pose is terminal until explicit reset |
| Interact | Ground reach/recovery, one-shot completion; an item pickup effect is separate gameplay |

The example priority is death > knockdown > stun > hurt. This is a design choice,
not a universal engine rule. Attack/effect windows, collision, invulnerability,
weapon sockets and damage need independent gameplay contracts and tests.

Physical displacement must integrate consistently over coarse and subdivided
updates. For jump anticipation, use a declared takeoff delay; only the remaining
flight interval drives the height curve and airborne root motion. Test exactly
before/at takeoff, apex, landing, held inputs, invalid actions, terminal reset,
direction locks and complete state recovery in addition to resource readback.

The repository tools `research/pixelengine-imagen/tools/build-rpg-preview.py`
and `check-rpg-preview.py` support the declared six- and 17-state sets. The latter
uses explicitly labelled pose aliases for a temporary runtime fixture; it is not
new art. Build and validate again against the actual package before delivery.
Actual native Godot resource decoding and an exported Web PCK load are separate
from browser execution. Exercise the genuine Web export's keyboard focus and
rendering in the browser, and retain screenshots/console failures.

Local evidence: `/home/astra/artifacts/hero-action-set-20261022/godot-v1/` and
`browser-proof/`. The native run checked 136 resources/544 exposures and 1,001
runtime assertions. Those counts certify the recorded package only and give no
art score. The inspector supplies root movement and jump height, not collision,
damage, invulnerability or a finished combat game.
