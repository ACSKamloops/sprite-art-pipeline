# Source boundaries for the authorized direct-H3 pilot

This report is preparation only. The reviewer made no provider, agent or model
calls and changed no canonical code. The parent owns the separately authorized
pilot and its budget. Retained evidence root:
`/home/astra/projects/pixellab-local-test-20261011`.

## User steering for the actual pilot

After this reference protocol was drafted, the user excluded the Warhammer
Captain from the H3 test and requested an original generic RPG hero made with
built-in image generation. The actual test uses that new hero and a separately
retained walking prompt. The historical case below supplies recovered method
boundaries; its PNGs are not a matched-subject quality comparison for the new
hero. No Captain image was submitted to native H3. Art, mechanical export,
submitted prompt, native task and output evidence are retained under
`/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/`.

## Preserve the historical baseline as method evidence

The earlier `runtime/probes/minimax-walk/request.json` records its exact
first-frame PNG and description. A matched historical comparison would require
those exact inputs; the user-directed generic-hero pilot is a different case.
The submitted PNG is 256×256 and SHA-256
`29266199aec2e9e233beff3c5656be047dd7494838df61b058da422750ecd2fb`.
The body requested eight generated frames, seed 123, background removal true and
enhancement false. It supplied **no last frame and no separate caption fields**.
Its exact description is:

> Walk in place for one full walking cycle, facing the same direction. Keep the camera fixed. Keep the armored knight face, red and gold armor, sword in his right hand, and shield on his left arm consistent.

Request SHA-256:
`1c4ee3aeba17ae3267dead91d61b17db6a1bd78b8325f2e2399e0dffd6e7eedb`.
Completed response SHA-256:
`248803c1614400acc4cca65a9000b14dc22b1e0cecb8a69f78c01ae5277fdac6`.
`last_response.images` contains nine PNGs, independently byte-checked in the
preceding animation evidence report. Return zero equals the submitted PNG;
returns one through eight are retained generated outputs. No source FPS is given.

Do not add an inferred subject, pose, view, direction or last=first condition to
the baseline. Adding any of these is a distinct experiment with a new receipt.
Do not replace the exact prompt with the source documentation's preferred motion
caption format: the real captured request is the comparison authority.

## What the recovered client actually does

| Stage | Exact recovered source and behavior |
| --- | --- |
| Caption slots | Godot `pixelorama-recovered/src/Extensions/PixelLab/lib/pixminimax_caption.gd:28-40` strips nonblank subject/pose text and omits Auto view/direction. `AnimatePixminimax.gd:241-247` selects those four fields. Lua `extension-extracted/PixelLab/pixminimax.lua:91-141` undoubles stored percent pairs, omits blank text/Auto choices and rejects unknown choices. These are serialization rules, not recovered vision captioning. |
| First/last | Godot `AnimatePixminimax.gd:280-304` rejects missing/invisible first image and invisible or unequal-size optional last image. Lines 316-323 send first, description, count, seed, No Background and supplied slots. No optional last was used in the historical pilot. |
| Count/size | Godot `AnimatePixminimax.gd:333-337,353-358` reserves count+1, uses `animate-minimax-h3` and validates sides ≤256 and counts 4..40 in steps of four. Lua `generate-animate-pixminimax.lua:139-179` applies these checks and uses reference dimensions. |
| Selected region/canvas | Lua `generate-animate-pixminimax.lua:150-190` keeps an explicitly selected region and otherwise asks before resizing the host canvas to reference dimensions. It does not prove a hidden neural resize or video sampling algorithm. |
| Codec | Godot `AnimatePixminimax.gd:267-273` sends raw RGBA descriptors; `get_image.gd:101-108` clears hidden RGB only where alpha is zero before base64. Lua `generate-animate-pixminimax.lua:203-216` sends raw RGBA plus dimensions. The public historical request instead supplies encoded PNG. Preserve that public PNG exactly for this pilot. |
| Return placement | `analysis-contract/depth-round2/PIPELINE-SPEC.md:21-25,39-41` separates reserved destinations, false reference markers, main/quantized arrays, raw/PNG decode and mask/selection placement. This is mode-specific editor assembly. It does not authorize universal reference trimming or first-frame freezing. |
| Pixel conversion | The baseline contains no image-to-pixelart conversion request. `analysis-poses/depth-round2/PIPELINE-SPEC.md:7-11,53-65` preserves native versus converted preparation, actual color/alpha observations and separate original/quantized/palette artifacts. Learned conversion, de-flicker, transparent-background extraction, native-video decoding/sampling and temporal repair remain private/unrecovered. Reading a server-returned quantized array is not the quantizer algorithm. |

## Minimal truthful comparison

1. Freeze the input PNG and historical request/response identities above. Record
   the direct API's actual model/version, URL namespace, exact submitted content,
   image bytes/role and prompt. Use the same image as **first-frame conditioning**,
   not a generic style reference. Preserve prompt bytes. Keep direct duration,
   resolution and other API-required choices explicit as new backend parameters.
2. Declare the mismatch before execution. PixelLab uses sprite frame count,
   transparency and seed controls and returns nine native-size PNGs. The retained
   current direct-H3 documentation instead describes video duration/resolution,
   task polling and a video URL; no equivalent requested-eight-frame, seed,
   alpha-extraction, drift-threshold or sprite-caption contract was established.
   Do not submit unsupported PixelLab controls or claim they were honored.
   Direct H3 family/revision is not proved to be PixelLab's served checkpoint.
3. Retain native returned video bytes, codec/dimensions, all decoded frame indices
   and PTS, actual duration, job/result metadata and failures. First inspect the
   native output. A separately labelled 256px display conversion or eight-sample
   inspection derivative may be useful, but requires an explicit sampler/times,
   mapping and transform receipt; it is a local review representation, not the
   recovered PixelLab conversion. Preserve every native frame and the source video.
   Do not quantize, remove background, recolor, interpolate or repair automatically.
4. Keep reference roles separate. Test whether direct output frame zero actually
   matches the conditioning image; never presume equality or prepend the input
   and label it generated. Preserve all nine historical PNGs. An optional historical
   body-only 1..8 view must remain labelled. Neither the historical diagnostic 8-FPS
   preview nor a new eight-sample video derivative supplies a missing model clock.
5. Review the same requested behavior with explicit limits: gait/contact and
   weight transfer, in-place registration/camera stability, recognizable face and
   red/gold armor, sword on the right and shield on the left, weapon attachment,
   blade/guard/grip continuity, silhouette/alpha/color drift and return seam.
   Use native all-frame playback plus chronological contact pages and neighboring
   pairs. First/last similarity alone does not establish a clean loop. The initial
   input already has many colors; do not invent a target palette or quantization
   objective. Record subjective findings separately from exact pixel/alpha/count
   facts. Different durations, resolution and missing alpha make a causal quality
   ranking or exact sprite-pixel parity claim unjustified after one pilot.

The current direct contract comparison is retained at canonical runtime
`docs/provider-preparation/minimax-direct/PIXELLAB-VIDEO-VERIFICATION.md` and its
hashed `public/` documents. Those are a separate versioned API authority, not
the original PixelLab backend implementation. Existing OAuth chat success must
not be reused as evidence that native video generation succeeded.

The prior report `PIXMINIMAX-ANIMATION-EVIDENCE.md` and machine JSON provide the
original OpenAPI H3 naming, HAR ordinals 1/24, all-nine PNG checks and selected
source hashes. This new pilot can test a direct H3 backend against the historical
animation task; it cannot retroactively recover PixelLab's hidden conversion.
