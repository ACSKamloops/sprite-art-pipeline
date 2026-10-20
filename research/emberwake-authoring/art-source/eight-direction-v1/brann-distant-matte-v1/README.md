# Scoped distant matte export

Frozen Brann SE/NE source paintings and review packets remain unchanged. An attempted isolated bake correctly refused9 stage-edge alpha1 black pixels in4 original cels. Diagnostic script now names offending actor/view/path/bbox; the gate was not relaxed. FAILED-BAKE.json preserves the failed config and partial output path.

A separate matte layer erases165 exactblack alpha1/2 pixels farther than3nativepixels from the largest8connected alpha24 body. All otherRGBA, including all paint within3px, stays exact. No global alpha threshold, part recenter, contour simplification or source-score promotion. The initial speck cause remains undetermined. This rule is scoped to these unarmedwalkcels; particles/accessories require other explicit ownership.

cleaned/inputs closes all16 original PNG dependencies; cleaned/MATTE-RECEIPT.json contains every literal before/after coordinate and outputhash. SOURCES.json and original-producer.py preserve initial ingestion provenance. Portable replay reads only retained local inputs:

    python3 -B replay.py --out /absolute/fresh/directory

Replay verifies each originalRGBA witness, independently checks no alpha24 surface within3px, restores the original pixels by undo, and reproduces all16 exact outputPNG bytes/bounds. This is a reversible literal erasurejournal, not an intrinsic sprite-editor/GUI claim.
