# Actual rendered sole-contact experiment

This is a bounded floor-contact experiment, freshly rerun for Copper Scout source revision `5f01d95` (historical revision `7630ea2` is preserved under `revision-7630ea2/`), not approval of anatomy, material quality, attacks, or the complete pipeline. Ground boundary is **y=170**, with opaque sole pixels at **row169**. The tested viewport has five fixed-camera 512px lanes, with a moving world root and one actual boot layer. There is no shadow/hand/component classification heuristic.

`summary.json` is the canonical verdict: per physical stance episode, actual opaque-sole xmin **peak-to-peak** must remain ≤0.5px, without missing sole or below-floor pixels. It records raw xmin/xmax and center ranges. `report.json` contains all 1,924 sample observations: two complete cycles, five fractional samples per tick, both front/rear boots for walk/run, plus endpoint. Its older `max_stance_pixel_error_px` is displacement from the first stance sample, **not peak-to-peak**; the independent summary computes the required metric from every raw pair.

| Route | Live continuous | Baked continuous | Baked draw floor | Baked draw round | Baked draw ceil |
|---|---:|---:|---:|---:|---:|
| Walk front/rear | 0px PASS | 2px FAIL | 1px FAIL | 2px FAIL | 1px FAIL |
| Run front/rear | 0px PASS | 2px FAIL | 1px FAIL | 2px FAIL | 2px FAIL |

Every policy keeps the physical root continuous: walk 24px/60ticks, run 40px/36ticks. Floor/round/ceil affect draw-root placement only, including fractional times. No policy freezes physical movement. Every stance's analytic foot target remains stationary separately, and IK target error is 0; those analytic facts cannot substitute for measured baked pixels. These generic snap policies are therefore **not a passing fix**. A different contact-aware placement policy would require another measured experiment and explicit gameplay/camera contract.

Actual GPU boot caches are made at the clip's integer ticks from the bound source using the same visible-layer filter, saved as PNGs, and shown by nearest-filtered uncentered Sprite2D quads. This is an isolated transparent boot-cache bake, not a claim that another exporter hash was validated. `cache_sha256` records every generated tick image. Current inputs match revision 5f01d95 and `source_unchanged_after_run=true`. GPU was Godot 4.7.2 compatibility renderer, Mesa llvmpipe; exact renderer fields and source hashes are in the report. The experiment has fixed camera, right view only, no equipment or whole-character occlusion.

`runner-at-capture.gd` preserves the exact full-capture executable. `foot_contact.gd` also offers `--witness-only` to render actual-GPU closeup witness frames. The full loop contact strips and zoomed witnesses derive only from these actual GPU PNGs, with nearest enlargement and labels; there are no repaired art pixels.

Repeat on a minimal local Godot project (project.godot can contain only `config_version=5`):

```bash
xvfb-run -a godot --path /tmp/copper-scout-parse \
  --script /home/astra/projects/sprite-construction-lab-rig-pilot/pilot/rigged-character/foot_contact.gd \
  --rendering-method gl_compatibility --audio-driver Dummy
python pilot/rigged-character/contact-proof/summarize.py
```

The independent reducer uses Pillow only for arranging diagnostic PNGs. Full-capture code source is bound separately from rig/design/clip sources. Shader/draw/texture sampling and source metadata all remain relevant when transferring this result to another renderer. Historical first-look art review stays separate; the newer five-clip prototype review does not approve baked locomotion contact.

## Contact-derived shared visual placement (separate follow-up)

`contact-lock-report.json` tests a single GLOBAL draw translation for both boot caches and the complete body, using current continuous pose contact metadata. Physics root remains continuous. The selected contact's desired fixed-camera sole xmin is its analytic world foot plus the measured authored sole offset −9, quantized to the actual raster; the global draw root subtracts the actual held-cache sole xmin. Run flight uses rounded physical root. Both current clips have no simultaneous contacts; the helper explicitly returns residuals if another character has two contacts. An incompatible double contact must be rejected by the consumer's gate.

Both boots now have **0px per-stance peak-to-peak** in walk/run, and **962 actual GPU full-body readbacks** equal the translated held whole-frame RGBA bytes exactly. Every selected-contact analytic pixel anchor matched the separately rendered live boot. Whole-body/boots share one correction, so this is not independent per-foot cheating. Contact pass is bounded to the tested two cycles and five samples/tick; it does not prove all continuous times, arbitrary camera transforms, mirrored views, smoothness, or artistic quality.

Costs stay visible: max physical-to-visual child offset **0.6px walk /1.7778px run**; max sampled draw-root step **1px /2px**, including flight/contact handoff. The earlier generic snaps still fail. `contact-lock-uncorrected-float-report.json` retains the rejected first attempt, where float32 coordinate cancellation crossed integer pixel boundaries; the numerical guard 0.0001px fixes integer-edge calculation, not the 0.5px acceptance criterion. Corrected output matched actual live pixels at all sampled contacts. Diagnostics `*-contact-locked-body-strip.png` show the rendered full body and both boot isolates.

Portable API: load `foot_contact.gd` as a script resource and call its pure static `contact_draw_root(pose_metadata, physical_root, held_cache_sole_xmin, camera_origin=0, sole_offset=-9)`. Return contains selected_contact, physical_root, draw_root, visual_child_offset, desired_xmin and active_contact_residual_px, or error. It rejects unsupported left views, malformed/nonfinite metadata, missing or noninteger selected-cache pixels. `policy-tests.json` records 12 passing contract cases, including preservation of inputs and incompatible double-contact residual reporting. All sprite parts use the same returned draw_root; collisions use physical_root.

`held-sole-cache.json` binds rig/design/clips hashes, the helper hash, each boot PNG hash, and each held whole-frame decodedRGBA hash. It contains tick-indexed sole minima for each right walk/run frame. Consumers must refuse stale source/cache bindings. Whole-frame hashes can validate already baked PNGs without depending on PNG compression. Source edits require regenerated caches and fresh evidence; historical results retain revision 7630ea2; current reports were actually rerendered against revision 5f01d95 after the grounded-rest changes. `cache-refresh.json` confirms all 96 whole walk/run RGBA frames and 192 boot PNGs remain unchanged, while their global source hashes were freshly rebound.
