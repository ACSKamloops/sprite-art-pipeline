# Planned interchangeable equipment tracks

**PLANNED ONLY. No weapon art, numerical anatomical anchors, occlusion masks, rendered attachments or runtime implementation exists in this handoff.** The user confirmed both first actions—punch and jump—are unarmed. This contract prepares future interchangeable weapons without baking them into body pixels.

## Attachment coordinates and identity

For each supported body clip and frame, record anatomical `near-hand` and `far-hand` socket/grip anchors, including frames where the relevant glove is hidden. Track the shoulder→elbow→wrist chain through occlusion; never rename whichever glove is most exposed as “near.” A hidden grip with no defensible construction remains null/unknown and is incompatible with visible equipment until deliberately authored and reviewed. Numerical coordinates are not inferred from a bounding box, glove centroid or color alone.

Each frame anchor records native body-canvas position, orientation in the fixed projected camera, optional positive scale, anatomical identity, confidence/status and the exact source frame SHA. Use pixel-center `[x,y]` coordinates, x right/y down; angle zero points screen-right and positive angles rotate clockwise. Equipment artwork has its own asset-local grip pivot and neutral orientation. Map that pivot to the body grip with the declared rotation/scale and then the same actor world/height transform. Positive local scale is authored and normally constant across the clip; frame-specific scale requires a declared projected perspective reason and visual review. Do not fit equipment to each visible glove or independently recenter the character.

One camera, body scale and registration convention apply to body, weapons, effects and transitions. The accepted walk remains 128×128; planned action clips use fixed 192×192 with source padding(+32,+64) and nominal pivot[96,170]. Per-frame body-canvas anchor positions refer to the actual bound canvas. A deliberate canvas/pivot migration requires an explicit constant mapping and revalidation; never silently reuse 128 coordinates on 192 art.

## Grip, visual layers and actual occlusion

A weapon definition identifies its asset and local grip pivot(s), native scale, neutral axis, permitted motion-profile IDs and independent damage/effect metadata. A one-hand grip follows exactly one anatomical hand. A two-hand profile designates a primary grip plus a secondary constraint and tolerance; both hands and the weapon must agree in the actual projected image. A ranged profile additionally needs aim/draw/release/recoil states and an independently authored muzzle/projectile-release anchor. Attaching a two-hand object to two arbitrary glove points is not a two-hand animation.

Per frame, a weapon visual may be split into explicit `behind-body` and `front-body` passes. Use authored source-hash-bound masks or layered body art for transitions through torso, hand or forearm depth. The portable compositing contract is: back equipment pass → base body → front equipment pass masked by its permitted region → designated hand/finger foreground layer. If that foreground layer is unavailable, a hand-occlusion mask can exclude the front weapon there, exposing the untouched body below. State exactly which mask convention applies; never simultaneously cut away the glove and expect a missing foreground hand layer to restore it.

Masks are exact native-canvas ownership decisions, not RGB classification. They may need multiple passes where a weapon crosses behind the torso and in front of a forearm. Store mask hashes and affected source frame hashes, and inspect isolated equipment, hand/arm layers, mask coverage and the final composite. A single z-order flag cannot prove a convincing grip. Ensure full tips, pommels, strings and trails fit the fixed action stage with clear margins; do not crop or shrink the body to hide clipping.

## Motion-profile compatibility

| Profile family | Required body motion | Swaps allowed only after validation |
|---|---|---|
| Unarmed | Punch/jump body actions, no visible held weapon | None automatically; the first two actions remain unarmed. |
| One-hand | Authored ready/locomotion and specific slash/thrust/etc. with appropriate arm, torso, support and recovery | Weapons whose grip, reach/mass assumptions, depth, collision and silhouette fit that exact motion profile. A light blade swap may still need timing/contact changes. |
| Two-hand | Both-hand grip chain, torso/support mechanics and compatible ready/attack/jump/recovery | Objects with matching primary/secondary grip placement and measured tolerance, not any object with two named pivots. |
| Ranged | Aiming, draw/charge, release, recoil and return-ready appropriate to the equipment | Matching grip/aim/release semantics; bow, crossbow and firearm motions are not interchangeable by default. |

Use exact profile IDs such as `onehand_slash_A`, not family name alone. A punch with a sword attached is still a punch and must not be advertised as a sword slash. Even simple equipped walking/jumping needs acceptable hand pose, held-object clearance and explicit compatible bindings. Missing combinations are unavailable, not silently substituted with the unarmed clip. These are future profile proposals, not produced clips.

## State, events and separate authorities

The held visual follows its hand socket while attached. Damage uses separate gameplay shapes/volumes and an authored active interval; the weapon silhouette is not automatically a damage hitbox. Muzzle flashes, trails, sparks, projectiles, palette flashes and audio have their own instances, coordinate spaces, clocks and termination. A projectile can transfer to world space at release while the held weapon remains attached. An impact event occurs on confirmed collision, not merely when the animation reaches an attractive extension frame.

All future event names/windows remain proposals. One simulation clock processes crossed equip/attach, hit-start/end, release, detach, completion and interruption events in order, including low-rate updates. Do not spawn effects repeatedly because a held pose stays visible. Equipment selection persists across compatible walk→action→recovery transitions; it must not disappear because the destination binding is absent.

At a requested swap, validate inventory/profile and choose a declared safe state boundary, or play an authored equip/stow transition. Do not replace a blade midway through an active strike unless that exact behavior is implemented and tested. Queue at most the latest valid selection request according to the eventual controller policy.

Interruption policy is explicit per equipment/state: `retain-held` keeps the same instance attached through a compatible hurt/recovery clip; `drop-to-world` detaches once with a recorded world transform and clears hand ownership; `clear-on-reset` removes owned visual, collision and effect instances. Every cancel/end/reset disables active damage immediately and terminates or transfers each effect according to its own policy. Never both drop and retain the same instance, leave stale damage active, or erase an independent world projectile just because the body clip ended. Drop/hurt/recover art remains backlog.

## Hash binding and review

A complete anchor track binds body manifest hash, every frame pixel/file hash, view/camera ID, canvas/pivot convention, weapon asset hash and every occlusion-mask/layer hash. Changes to body pixels, pose order, registration or camera invalidate affected anchors/occlusion reviews. A timing-only change may preserve spatial coordinates after exact frame mapping, but invalidates event/temporal review; rebind and revalidate it explicitly. No stale hash is silently accepted. If a shared body source changes, recheck every dependent weapon profile.

`attachments.schema.json` describes the planned metadata shape and null/unknown anchor status. Schema validation alone cannot establish anatomical correctness, mask ownership, suitable motion or actual rendering. The example binds the real selected EO frame0 and leaves numerical anchors, weapon pivot and masks null because they have not been measured/authored. Its compatibility status is `NOT_READY`; it is not a drop-in rendered weapon.

Future acceptance needs native/2× isolated and composite inspection, actual imported/rendered pixels, complete neighbor/transition coverage, equipment persistence and cleared hit/effect ownership. Test 60/30/15/10 render fps, a250ms hitch, swapped selection requests, forced interruption and repeated reset. Confirm every crossed damage/release/drop event exactly once and actual collision coverage when active poses are skipped. User art approval remains separate from a valid schema or clean event log.
