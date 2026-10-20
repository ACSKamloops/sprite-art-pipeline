# Matched H3 / PixelLab comparison boundaries

Initial read-only audit, 2026-10-14 03:03 UTC, updated after all three matched
cases completed and hidden-RGB differences were quantified. No credentials, provider calls, utility
edits, or real artifact writes were performed by this reviewer. Artifact root:
`/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014`.

The valid experiment is a **matched-input service-pipeline comparison**, plus a
separately labelled sprite-workflow assessment. It does not isolate model weights
or justify a base-model ranking. `COMPARISON-PROTOCOL.json` says this explicitly;
its reviewed SHA256 is
`e97df4c6d43aa4bafb8fe836c3497711e7b9d24196e1682bfa017e1d6cb8b8fb`.

## What is actually held the same

Independently decoded the prepared native and PixelLab request image payloads,
compared them to both retained `source.png` files, checked literal prompt UTF-8
hashes and native request hashes, and checked the two captured POST bodies.

| Case | Same submitted PNG SHA256 | Same literal prompt SHA256 |
| --- | --- | --- |
| Walk v1 | `571b74ac6bd1a945263c8c5cdf2b1eab9facf277bbc752c767de6f4412bf8084` | `2f078a8fd63d6c23ef8aacc95d5a051006cf0d1e3741f0af0b828e11a1b3070e` |
| Slash v1 | `571b74ac6bd1a945263c8c5cdf2b1eab9facf277bbc752c767de6f4412bf8084` | `4cb41f264b048ab520cdd845a8442624abb2fd5283300f42d033106ce66ecc35` |
| Slash margin v2 | `e63340b333df3354948b4ee707b2e4bfa23ca901f6b464a941e2ff06281d4a5e` | `4cb41f264b048ab520cdd845a8442624abb2fd5283300f42d033106ce66ecc35` |

Each pair uses one identical 256×256 PNG as `first_frame`, one identical literal
instruction, and no optional last frame. All are the new generic RPG subject;
historical Captain captures are not comparison inputs. The margin-v2 PNG is a
different conditioning case and must be paired with `h3-slash-margin-002`, not
the unpadded H3 slash. A cross-case framing change is not evidence of a backend
quality improvement in isolation.

At the initial audit, walk and slash-margin were completed while slash-v1 had
zero submission attempts. That was a dated snapshot, now superseded: all three
matched PixelLab cases completed with 17 returned images each. The updated
`COMPARISON-VERIFICATION.json` reviewed here has SHA256
`7bf9ce1e4bfc39a326233d7c828c217eeb1510e343e313ccddbb633a42e9c796`.

## Controls and conditioning are not equivalent

The retained public OpenAPI retrieved at `2026-10-14T02:53:57.506763+00:00`
has SHA256 `8cb24ecdd26e9fe48639dc789e44f32b3c78c29e8da8c3121f23ab360ade5dad`;
the file matches `public/RETRIEVAL.json`. Its server prefix is `/v2` and route is
`/animate-pixminimax`.

PixelLab requests 16 generated frames, seed 123, `no_background:true` and
`enhance_prompt:false`. Native requests name MiniMax-H3, request four seconds,
768P, and adaptive ratio. They declare no matching seed, generated-frame-count,
or typed alpha-output control. No corresponding native mapping should be invented.
Seed 123 is a PixelLab pipeline parameter, not proof of a shared H3 random state.

**Literal descriptions match; complete model conditioning is unknown.** All
four PixelLab caption fields are omitted: subject, initial pose, view and
direction. The public route says omitted captions are read from the image by an
AI model. Its no-rewriting statement applies when all four captions are supplied
and enhancement is off. Thus `enhance_prompt:false` does not establish identical
internal captions or prompts here. Native Context-IR was not requested, but this
does not prove absence of private native prompt processing.

PixelLab's `drift_threshold` is also omitted. The schema describes a default
color de-flicker correction policy but discloses no numeric default or algorithm.
This is an unmatched service-default policy, not demonstrated native behavior.
Segmentation, palette conversion, sampling, caption inference, hidden processing
and the deployed checkpoint/fine-tune remain unknown. Public “powered by H3”
does not identify equal deployed weights.

## Reference, cardinality and clocks

The route documents `frame_count+1`: reference slot 0 followed by generated
slots. Returned slot 0 is not PNG-byte-identical or raw decoded-RGBA-identical
to its submitted image, but this does **not** mean visible content was redrawn.
Independent decoding of all three completed responses confirms that **every
alpha value and every visible RGB value is exact**. Only hidden RGB where alpha
is zero differs: 49 pixels in walk, 49 in slash-v1, and 30 in margin-v2. Setting
hidden RGB to zero at alpha zero produces exact full-RGBA identity in each case.
Keep both raw identity flags false while reporting this qualified visual/pixel
preservation result. The extraction helper displays slot 0 separately.

This observed normalization matches recovered Godot
`pixelorama-recovered/src/Extensions/PixelLab/get_image.gd:101-108`, which clears
RGB at zero alpha. Whole-file SHA256:
`8f7224392a2b3511d124e577a4a360c8e3344d9df60f0692f011dcd1e89aa651`.
Matching behavior does not identify the private service implementation or prove
that this particular client function ran remotely.

Keep complete responses in original order. Do not prepend an untouched reference
and count it as a generated native frame, silently drop native startup/recovery,
or merge the returned PixelLab reference into a 16-frame generated comparison.
The native decoded videos have 107 frames over exact PTS duration `107/24`
seconds; requested/billed four seconds does not replace that observed clock.
There is no temporal correspondence between native indices 0–106 and PixelLab
returned indices 0–16 merely because they are displayed side by side.

The historical client flow is not a common service clock. Lua's animation path
skips its first returned reference; the recovered Godot/browser path retains it.
Lua native Aseprite hold inheritance was not established by the supplied source.
Godot frame duration/project FPS and website 125ms previews/200ms saved defaults
are client choices, not recovered inference timing. A shared nominal two-second
inspection view is therefore an explicit analyst clock, not native PixelLab FPS
or inferred event alignment.

Historical source bindings beneath
`/home/astra/projects/pixellab-local-test-20261011`: the original
`extension-extracted/PixelLab/generate-animate-pixminimax.lua` hash is
`77de402722626a49d006c50872898fa496c920b3ec71fa0a62b9dcdbc1c660e6`;
recovered `pixelorama-recovered/src/Extensions/PixelLab/ui/tools/AnimatePixminimax.gd`
is `514de90de8ea82fd372e2dde8e0ca5d66885d73010d16623bac83479b91f5f2f`.
The bounded source-flow/timing ledger is
`analysis-poses/depth-round2/animation-client-closure/ANIMATION-CLIENT-CLOSURE.md`,
hash `519aff54883e9ea69936b86dbe8a8c2227e882033fb8f4a3e6abeb9c1e24f9eb`.

Evaluate native full video and complete PixelLab outputs first. Separately assess
the local H3 walk candidate `[16,64)`, its authored two-second 8/16-sample loop,
and the endpoint-inclusive one-shot derivative with native PTS holds. Sparse,
phase-selected H3 views are not interchangeable with the whole native take.
The local border-black alpha key (tolerance 12, four-connected), whole-canvas
nearest 256 resize, and their outline/fringe risks must remain disclosed.
PixelLab returned PNGs remain unchanged. Equal derivative sample counts do not
establish matched motion phases. Adjacent-difference flags have unequal temporal
spacing and cannot support a naive cross-provider numerical ranking.

## HTTP/REA provenance and valid conclusions

`network.har` is the Python helper's producer HTTP record, not a browser HAR.
The two captured POST payloads match the prepared JSON; retained Authorization
and Cookie headers are absent. REA import IDs are
`ev_e8d4c08e3a3356ea08f8f56a16c9c151a2ea83325613e159d2c4db0fe666c28f`
(walk) and
`ev_4fff30b778061e3cfbffe5d183cec9d27b6cfb77b578417fc8dbe7ce91406766`
(margin slash). Their match checks establish PNG/text/role equivalence and mark
controls unequal. Those initial imports selected submission ordinal 0 only.
Final imports reported by `COMPARISON-VERIFICATION.json` select ordinals 0 and 2
(submission and completed response):

- Walk: `ev_105561b10d4b294aabcfb93caa7f82be614b640394175469d243fce8677e642b`.
- Slash-v1: `ev_37a69cd8da3b9af4e67c0682e0bef0c2e3dc60843caaaddeffe6d764cc8687c8`.
- Margin-v2: `ev_2cc1259007a0e7e7f36f300e1ac323b3f30b6ca2fc15a7496caa842d02880e99`.

All ordered extracted PNGs are recorded as matching the retained response bytes.
These final imports do not establish private code execution. REA's limitations exclude live
browser transaction attribution and deployment authenticity; no URL was fetched
by this reviewer or by the offline import. Historical captures remain method
references, not these trials' results or proof of current private implementation.

Valid findings can describe native dimensions/alpha/count, source consistency,
clipping, grip/gear continuity, gait/contact/seam, attack progression, recovery,
and the explicit workflow needed for game sprites. Such findings must cite the
actually viewed intervals and separate raw outputs from local derivatives.
They cannot establish isolated model superiority, recovered PixelLab algorithms,
all-branch parity, hit-event timing, or universal artistic acceptance.
