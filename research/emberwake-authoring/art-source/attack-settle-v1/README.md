# Attack-to-idle settle candidates

**Selected:** `selected-candidate/{lyra,brann}/{south,east,north,west}.png`. Eight new native128px cels; no runtime atlas, manifest, combat script, animation event or prior tab repair was changed. Art/motion approval remains pending independent review.

Two built-in OpenAI ImageGen edits were made, one four-view sheet per character. No CLI, local model, H3, API credential or third generation call was used. Each literal tool prompt and complete actual arguments are retained in the character folder's `literal-prompt.txt` and `tool-call.json`. `input-provenance.json` binds the actual input images, source atlas, source manifest, raw output and prompt. The prompt file has one final newline; the separate actual argument hash binds the exact submitted string without that newline.

## Reference roles and registration

The source was the root project's read-only `art-source/characters-v2/bake-v3/{character}/atlas.png`. The actual edit input is a transparent2x2 grid of guards f13/f41/f69/f97, in south/east/north/west reading order, with each128px stage replicated4x. The second actual input is the matching following idle f14/f42/f70/f98, for pose endpoint and appearance context. Both input PNGs were viewed before the call. `offline-attack-context.png` freezes all six original attack keys plus both idles per direction for the timing proof; it was **not** passed to ImageGen.

Requested1024-square sheets returned actual **1254x1254 RGBA**. One nearest-neighbor resize of the complete sheet to256x256 establishes the four128px cells. There is no individual bbox fitting, per-view scaling or per-cel translation. The returned body/limb drawings are new paint, not whole-cel translations or fabricated in-betweens made from repeat exposures.

There were a few remote raw background specks with alpha1/255, including at cell borders. The registration removes exactly alpha==1 texels to RGBA zero; every alpha>=2 value stays intact. Untreated and cleaned transports are preserved separately. This is recorded cleanup, not a claim that the raw model output obeyed every transparency constraint.

## Head ownership and the rejected composite

The registered generated heads were compatible with existing same-view paint, so literal small head/neck masks restore existing pixels, including transparent pixels needed to clear old generated edges. The final donor is the **following existing idle head**. A first attempt using the guard head also copied a fingertip near Lyra's side-view jaw; that composite was rejected. Using the known unobstructed idle head avoids inventing hidden face anatomy or retaining a detached old glove. The actual final triptychs were inspected after this repair.

`head-protection.json` records the masks and donor role. Pixels inside each mask exactly match the existing idle; pixels outside exactly match the cleaned generated registration. This protects identity in that declared region; it does not prove an anatomical rig or unchanged torso paint. Brann retains his red-orange hanging tab and gold accents in the new drawing. North remains a back view with no visible face.

The initial partial output is `candidates/`. `candidates-v2/` retains the rejected guard-head composite; `candidates-v3/` has the same final pixels as `selected-candidate/`, before the documentation/source-role freeze. Raw neighboring triptychs and first-draft head plans remain available for diagnosis. Only `selected-candidate/` is proposed for review/integration.

## Timing proof and remaining limits

Each selected folder includes native and3x guard→settle→idle triptychs, the four native PNGs, masks, the complete registered sheet, and four before/after APNGs. APNGs preserve the same1.57-second whole-attack-plus-two-idles clock in both panels. The proposed final105ms guard hold becomes35ms original guard +35ms new settle +35ms existing first idle. The previous305ms of attack are unchanged; total attack410ms and gameplay hit160ms remain proposals for root integration, not edits made here.

The generated arms in several views lower closer to idle than the requested exact halfway position. Feet narrow substantially; the stance often provides the clearer intermediate. **Guard-to-settle endpoint differences remain.** New torso shading and small sole-position differences also remain possible. Border-clearance checks do not establish planted-foot contact or smooth full-speed game motion. One new key is a bounded candidate repair, not proof of a complete recovery solution or an8/10 score.

## Reproduce and verify

Requires Python and Pillow; no model call or source project is needed for replay because the exact input grids and offline context are frozen here. From the project root:

```sh
python art-source/attack-settle-v1/register_settles.py \
  --output art-source/attack-settle-v1/replay-fresh
python art-source/attack-settle-v1/verify_settles.py \
  --candidate art-source/attack-settle-v1/replay-fresh
```

`verification.json` records44 successful checks. Its independent per-pixel reconstruction uses the saved raw1254 image, an explicit integer source-coordinate map, alpha1 cleanup and literal same-view idle-head ownership. It reproduces all eight selected RGBA cels exactly, verifies the actual prompt/reference hashes, retains128px stages without border clipping, and measures the actual1570ms APNG clocks. These are provenance/preservation/timing checks; normal-speed game rendering, equipment/stance continuity and independent art acceptance remain root's next steps.
