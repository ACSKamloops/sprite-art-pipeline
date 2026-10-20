# Fair animation review and delivery

## Separate three gates

- **Artwork:** identity, drawing/material/anatomy, silhouette, equipment volume, palette, joint/part roles, framing and native readability.
- **Performance:** intended action, preceding/current/following poses, path progression, anticipation/contact/recoil/recovery, holds, boundaries and actual perception limits.
- **Transport/runtime:** exact source bytes or documented normalization, rational timings, editor exchange, engine resources, live frames, GPU/browser output, input/state behavior.

Passing transport cannot raise an art score. A mechanical contact/pivot is not physical foot-contact proof. An asset preview does not supply damage windows or a complete controller.

## Equal-clock controls

When testing a new intermediate drawing, split the original hold into the same exposure slots for both candidates. The control repeats its old pose; the treatment inserts genuinely new or deformed artwork. Keep original key starts, total duration and contact/recovery boundaries unchanged. This isolates the drawing's contribution from timing.

The example's original eight holds were `[2,1,1,1,2,1,1,5]/24s`. Its ten-slot control/treatment uses `[4,2,2,1,1,4,1,1,2,10]/48s`. Total remains7/12s and the old keys keep their starts; the extra slots occur9/48s and15/48s. These are fixture timings, not a universal attack speed. Fewer initial/terminal guard ticks can shorten a file without increasing active movement speed. Compare phase boundaries before calling it faster.

## Independent review

When independent review is part of the task, send only the reference/style brief, anonymized candidate assets, exact holds and the installed animation companion's **case-free** `references/blind-review-card.md`. Do not send this skill's scored case history, producer mappings or earlier results to a cold reviewer. Use isolated write locations/worktrees as appropriate. Freeze reports before unblinding or discussing a provisional preference; disclose exposure and history-aware reviews honestly.

Inspect every pose and adjacent pair at native/nearest enlargement on light, dark and colored backgrounds, including action entry/exit and wrap/retrigger where relevant. Unchanged coverage may transfer only after exactRGBA and timing comparison; changed pairs still need inspection. A still viewer does not imply normal-speed video was perceived. Reconstructing chronology is useful but must be labeled. Human normal-speed and controller acceptance remain separate.

Score consistency/reference/drawing/motion/usefulness/overall separately if ratings are requested. Overall is holistic, not an arithmetic mean. Keep uncertainty, dissent and source hashes. Do not round to a requested threshold or rerate identical pixels to obtain a pass. Request one bounded change tied to a demonstrated defect, then freeze a new comparison. An accepted compact action should not become a stronger windup merely to chase a number.

Keep an early semantic diagnosis provisional until enlarged and game-size
inspection agree. In a rear-diagonal jab, short glove lobes initially looked
like an open spell hand; closer inspection supported only ambiguous knuckles
or partial relaxation. The corrected finding superseded the early wording.
A source-hand replacement earned a slight closed-gesture preference, with no
body-motion credit. A reviewer who raised the original concern can inspect a
repair independently of its producer, but is not a fresh control-blind critic;
disclose that exposure instead of calling the review cold.

## Practical delivery checks

Use the companion construction/animation toolkits rather than reinventing their serializers. On selected files:

1. Render the editable layers and compare every exported PNG/atlas region and hold to reviewed art.
2. Save/reopen in the actual external editor; import with its exact timing/lineage sidecar. Integer milliseconds alone cannot represent1/48s exactly.
3. Decode an actual rational-hold APNG and compare all RGBA/delays. A CFR video must have checked ffprobe timestamps and decoded pose order. Lossy MP4 is a preview, not pixel authority.
4. Verify the actual Godot playback architecture. For SpriteFrames, import/build/save/reload the resource, check regions/durations/loop, then run AnimatedSprite2D. For a custom atlas/JSON renderer such as Emberwake, validate its own schema, loader, frame selection and clocks instead; the generic companion manifest validator does not accept that custom schema without an explicit adapter. In either case observe every exposure, one-shot finish/restart and actual Viewport input behavior. Compare actual static/live GPU captures with source composites; document background and alpha tolerances. A second unused renderer is not required.
5. Check the actual browser player's PNG/canvas output, clock, one-shot/repeat and source mappings. Sample state and pixels in the same RAF callback; an asynchronous screenshot can belong to a later frame.
6. If fine editing is delivered, verify an actual pointer stroke and undo/redo, then replay the exported journal in the deterministic toolkit. Preserve the fully restored production source.

These checks need a real tool execution. A generated script or “passed” field without its run is not evidence. Use explicit absolute engine project paths and limit CPU threads reasonably. Run tests appropriate to changed art/tools; do not continually rerun an unchanged whole library.

Compare exported textures under the actual import contract. In one Godot Web
PCK test, raw RGBA hashes failed because the existing `fix_alpha_border`
processing changed RGB at alpha 0–19, including faint nonzero-alpha samples.
Alpha and stronger samples were exact. Applying the configured engine
`Image.fix_alpha_edges()` transform to raw source reproduced every exported
RGBA byte. Preserve the first raw and partial-alpha failures, measure the
affected alpha range, and name the verified transform; do not discard all
transparent or faint pixels merely to obtain a match. The range is evidence
from that case, not a tolerance for other art or engine versions. Read
[Godot's importer contract](https://docs.godotengine.org/en/stable/classes/class_resourceimportertexture.html#class-resourceimportertexture-property-process-fix-alpha-border)
when using that option. Exact processed pixels establish export binding, not
art quality, and do not imply raw-source equality.

Deliver the selected native frames/atlas, source/sidecar, manifest, maps/ownership, literal edit journal, actual prompt/reference provenance, scoped review reports and runtime receipts. Preserve approved baselines and rejected material separately. For a local AI, provide paths rather than uploading or zipping without request. State which actions/views/transitions/equipment remain uncovered.
