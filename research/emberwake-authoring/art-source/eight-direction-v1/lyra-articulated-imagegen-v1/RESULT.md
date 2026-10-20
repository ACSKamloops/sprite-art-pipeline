# One built-in ImageGen test: raw pose rejected

The single authorized OpenAI built-in `image_gen.imagegen` call missed the articulated06 pose. No protected-restoration candidate was constructed. The raw return and failure proof are retained; there was no reroll, local model, CLI/API substitute, editor package or game change.

Open `analysis/base-guide-raw-owner-256-light.png` and `analysis/raw-guide-joints8x-light.png`. Native128 and84 comparisons are supplied on light, dark and game-green backgrounds, with joint details on all three. The original raw1254×1254RGBA return is preserved byte-for-byte as `raw/raw-return.png`; the only transport is one uniform nearest resize of the entire canvas to128×128. No fitting, recentering, crop, stretch or alpha cleanup was applied.

The raw foreground limb has a tall conventional brown boot and a more vertical trouser rather than the bent calf from K(52,92) to A(43,93). The protected foot should occupy x36..51/y93..102. The raw image is transparent at the ankle target(43,93) and heel witness(41,101). It covers only42 of136 protected distal coordinates with alpha>=128, and that coverage does not establish matching material or shape. The knee target receives brown leather rather than the guide's charcoal knee. The raw body's registration also differs from the fixed base: its alpha>128 envelope is x38..94/y21..108 versus the base envelope recorded in JSON. These observations are made **before** any protected restoration.

Restoring the fixed toe and upper would conceal those missed relationships and could create a false joined leg. Therefore this test stops at the raw geometry gate. It should not be sent to a critic as a completed pose or assigned an art score. A reviewer can use it as evidence that this one reference/edit request did not achieve the target. This does not establish that ImageGen or articulated sprites are generally incapable of the pose.

The five actual local inputs were copied, hashed, ordered, and individually viewed before the call:

1. Authoritative current06 upper/other leg plus the placed136-texel distal foot.
2. Articulated06 pose/coverage guide, explicitly not an appearance reference.
3. Current04 material/identity appearance reference; its old leg pose was excluded as the target.
4. Current06 appearance/protected-body reference; its old foreground leg was excluded as the target.
5. Allowed-region guide, magenta marking the editable owner.

The pre-call editable owner is161 native pixels and includes all67 declared new-joint guide coordinates. Literal proximal polygons and row runs are retained in `masks/OWNER-SPEC.json`; all source-positive upper, other-leg and distal pixels are excluded. No blind dilation or generic color filter generated this owner. The request required charcoal fabric and brown leather to replace guide colors, a transparent background and no text, shadow or extra parts.

`request/PROMPT.txt` is the exact submitted prompt; `TOOL-ARGS.json` contains the actual ordered local references and transparent-background argument. `REQUEST-RECEIPT.json`, `INPUTS.json`, and `raw/RETURN-RECEIPT.json` bind the call to input/output hashes. The raw SHA256 is `5b81b09bd87fc04973e91512a2074b26cf79aae183b9356c8ca0d3802e1a60bf`. The raw has genuine transparency and very low-alpha scattered pixels; they are preserved. Alpha thresholds in the report are diagnostic measurements only.

`analysis/RAW-GEOMETRY-REJECTION.json` contains native control samples, raw-versus-fixed owner counts and the decision not to construct a candidate. `RAW-AT-PROTECTED-DISTAL.json` retains all136 literal protected-target/rawRGBA comparisons. Raw model paint remains distinct from deterministic source paint; no final articulated pose is claimed.

Portable analysis/proof reconstruction, requiring Python3,NumPy and Pillow:

    python3 -B scripts/analyze_return.py --output /absolute/fresh/output

This command reads the retained raw bytes and local inputs only. It does not call a model, engine or browser. All prior proposals, failed rigs, source studies and the canonical checkout remain unchanged.
