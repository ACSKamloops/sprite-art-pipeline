# Authored locomotion, contact ownership and actual runtime evidence

Use for a baked walk that must start, stop and collide in a game. This extends clip playback; it does not supply missing anatomy or art approval.

## Source contract

Retain ordered PNG hashes, canvas, pivot, rational holds and the actual loop flag. Keep the physical root, source pivot, final draw origin and any whole-actor visual correction distinct. A fixed camera or a correct ankle target does not prove a planted rendered foot.

For material checks, export isolated foot RGBA **after** depth shading, palette mapping and downstream contour painting. Exclude changing shin/cuff geometry. Export a visible-foot mask from known higher-layer alpha and retain full/visible/occluded counts. Assert RGB agreement only after selecting ownership. Never classify a color mismatch as occlusion: a demonstrated far-foot exporter saved unshaded pixels and an RGB filter then wrongly excluded them as hidden. Preserve and withdraw the invalid result before rerunning the corrected source.

## Held poses and raster placement

A discrete held source pose under a continuous physical root slides within its hold. If a visual stance policy is selected, fix one world target on entry to a conservative flat-contact episode and compute one whole-actor correction. Keep all limbs and equipment together; do not fit each boot separately. Heel/toe rolling phases have intentionally changing material positions and should not be treated as rigid flat contact.

Compute the final actor draw origin from physical root, pivot and correction, then round **once**. In the demonstrated Godot consumer, a top-level nearest-filtered Sprite2D avoided separately rounded parent/local transforms. Nearest filtering alone produced fractional-position texel defects; hierarchical snapping produced one-pixel contact shifts at ties. Recheck the actual GPU after changing camera, scale, origin or snapping policy.

Read the actual saved configuration before comparing motion units. This consumer's walk `stride` is viewport pixels per cycle, while bank-curve offsets and source anchors are native art pixels scaled by the display factor. A30-native-pixel stride requires30 viewport pixels at1× and60 at2×. Movie enlargement is another transform: the RR raw test used engine scale1/stride30, then enlarged its captured movie2×. Its filename did not imply engine scale2. That run verified every imported/isolated texture and711 actual stage screenshots, yet observed1px intra-hold drift and2px at native32 when fractional movement crossed two rounded draw origins. Source-to-GPU fidelity does not establish contact.

Sample several fractions within every held flat pose, both supports, episode changes and loop wrap. Compare all explicitly visible foot material, not only a centroid, target or lowest row. Report within-hold drift separately from across-pose deformation/occlusion. Zero held-pose drift does not establish an invariant whole foot across the entire stance or correct anatomical movement.

For an across-pose material comparison, place each owned visible mask at its recorded actual draw origin and intersect masks in world coordinates. Compare GPU RGB on that common visible material; count newly hidden/revealed pixels separately. Full hidden-part comparisons are source-only. Retain a raw-moving negative control so a comparator that accidentally ignores motion is detectable. The source-bound `runtime-work/O-pilot/measure_world_intersection.py` demonstrated zero changed RGB across16 locked pose boundaries while its raw control detected12078 changed pixels. Its authored ankle-minus2 witness band, two-loop/five-fraction sampling and fixed-scale assumptions are explicit case limits; it is not a generic whole-foot or heel/toe physics test. That same art was rejected at6.8/7.2, so this material result must not become an art score.

## Compare presentation policies separately from physics

A cel-held draw origin can keep the entire held source pose still while the physical root advances continuously. Compare a uniform cel-boundary draw origin against any contact-derived curve with identical physical roots. Measure both within-hold stability and across-pose deformation; a policy can improve the former without solving the latter. Include visual lag/lead, pose-boundary steps, wrap, collision and stop behavior.

In the source-bound29-pose HHH study, actual scale2/stride60viewport pixels meant30native pixels per cycle. A contact-derived held curve eliminated intra-hold drift but produced up to3.472native pixels of sampled visual bias and3px body steps. Uniform cel holding also eliminated intra-hold whole-lower-leg changes, with about1.035native pixels maximum sampled lag; across-pose boot proxies still varied3/4/1px. These proxy differences may include changing sole shape and rolling, not a single planted material point. A collision transient left0.259native pixels of visual lead and an immediate stop switched pose16 to0: starts/stops still need authored coverage. The retained III run checked87 isolated imports,2750 world screenshots, strict clock boundaries and a displaced-source control, plus an actual three-way input-driven capture. Those checks establish that source and configuration only; changing art requires renewed source/GPU fidelity evidence, and no draw policy supplies art approval or missing transitions.

## Finite start/stop banks

The tested `authored-locomotion-bank/v1` consumer binds a source walk by manifest SHA256, named idle variants, finite starts and a finite stop for each permitted walk frame. A bank may use arbitrary canvas sizes, frame counts and idle names; A/B, 96px and 16 frames are case data.

Each transition manifest uses the ordinary PNG/rational-hold contract. Check canvas/pivot and positive holds, reject looping finite transitions, and verify exact first/current and last/destination source pixels. These boundary matches prevent a source switch pop; they do not approve the intervening drawings.

An optional root curve specifies cumulative offsets in native-art pixels relative to the physical root at transition entry. Scale it once into viewport units and consume it through collision movement. Rate changes scale the pose and motion clocks together. Authored joint coordinates can help construct the curve, but only rendered material evidence can support a pixel-contact claim.

Input changes during a finite authored transition can queue the latest request. Test the resulting latency, restart, cancellation and wall behavior. A collision latch can prevent repeated launches into a wall until input is released. Preserve an existing whole-actor draw correction as a constant presentation bias through stop/idle/start when that is the selected policy; clearing it can cause a visible source-origin jump even with byte-identical boundary images.

Source stepping at a fixed physical root is inspection, not a root-motion replay. Reset before using a stepped run to claim authored displacement.

## Clock and evidence separation

Select poses using strict cumulative boundaries. Probe just before, exactly at and just after each boundary, wrap and finite completion. An arbitrary early-boundary epsilon advanced the portable test fixture prematurely. Store rational cumulative boundaries and normalize machine roundoff only when advancing the engine clock; do not widen the selector's interval.

Keep three kinds of proof separate:

1. Actual engine input/state/physics tests, including every legal stop entry and fractional entry time, queued restart, rate, pause, reset and collision.
2. Explicit-state GPU samples that establish selected source-to-render pixel fidelity. Assign state before rendering and record after presentation; these are not live-clock tests.
3. A live input-driven capture using the runtime's own clocks, with no direct per-frame pose/root assignment. Record state, source manifest/frame, physics tick, root, draw origin and bias for every captured PNG, then compare the actual screenshot to the selected art.

Timed movie generation from actual PNGs is a presentation. Retain the input records and screenshot assertions. A deterministic movie clock and normal render-cap behavior are different checks. Chronological decoded-image inspection through an AI interface should not be described as continuous human video perception.

## Proven local case and scope

The generic consumer is bundled in `assets/godot-locomotion-lane/`. Copy it into a fresh output folder, then run its `configure.py` on the selected manifest/bank and launch Godot as shown in the bundled consumer instructions. Configuration copies the chosen PNGs; original absolute paths are provenance, while runtime paths are relative. This local raw-PNG consumer has not been verified as a packed/exported game.

Run `python3 scripts/locomotion_smoke.py FRESH_OUTPUT --gpu` to forward-test the bundled consumer and tiny diagnostic fixture in isolation. Omit `--gpu` for the actual headless engine tests only. The fixture uses a different canvas/pivot, reordered bindings, asymmetric rational holds, two-key finite clips and one idle named `rest`. It tests boundary semantics and state/curve behavior without depending on the hero artwork. GPU checks additionally require `xvfb-run`, Pillow and NumPy; Godot 4.7.2 is the tested local version. Successful fixture checks establish mechanics for that fixture, not art quality or an untested engine version.

`/home/astra/artifacts/pixellab-hybrid-walk-20261015/game-ready-v6/runtime-work/` contains the source-bound implementation, archived failed contact/raster results and separate input, explicit-render and live-capture evidence. Its `portable/` consumer and `portable-smoke/` fixture are the forward-tested reuse sources; consult their current receipts rather than inheriting historical counts.

The hero art remains a quality-development example. Source fidelity, strict clocks, connected alpha, correct state transitions and complete journals did not raise its reviewed anatomy to the user's 9/10 bar. Copy the tested mechanics, not an unearned aesthetic acceptance.
