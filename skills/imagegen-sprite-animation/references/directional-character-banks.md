# Four-direction ImageGen character banks

Use this when a flat approved character must become a top-down game set. It records the actual Emberwake route and its repairs. It needs no 3D character model. New front/back anatomy is generated paint, not geometry recovered from the original still.

## Reference and view contract

Keep appearance, pose, edit target and layout authority separate in each request. In the tested case the approved generic hero supplied the appearance; eight retained frames from an older accepted H3 walk supplied only the corrected side-walk poses. All new painted hero/world keys came from the built-in OpenAI ImageGen tool. No new H3 call or local generative model was used. A still alone does not supply motion guides.

Freeze these fields before expanding the bank:

| Field | Required decision |
|---|---|
| Appearance | Hair/face, costume, palette, materials, proportions, distinctive asymmetric features |
| View | Camera elevation/projection, south/front, north/back, east/right, west/left; desired profile versus three-quarter angle |
| Scale | Canvas, actual painted height, foot/pelvis stage origin, permitted reach and crop margins |
| Action | Preparation, contact/release, recovery and entry/exit stance; which limb acts |
| Equipment | Painted into body, separate track, or absent; spell particles separate from body |
| Time | Positive holds, full duration, looping, gameplay event time and interruption policy |

The tested hero is unarmed. South shows the face/chest; north shows the back of hair/tunic without eyes or front chest. Side views must agree with those costume volumes. Check neutral directions together at game scale before accepting a new bank. For a new character, checking a useful walk before requesting a large library avoids propagating a weak design. Historically this case first requested four 24-key sheets and then repaired them; the initial layout was not proof that those keys were ready.

## Actual initial layout and adaptable request

Each direction was requested in a separate call, with the same appearance reference. An already painted south sheet also served as style/costume context for other views, never as their pose or facing authority. The four actual initial returns were 1536×1024: six columns, four rows, 256×256 source cells.

| Row | Six requested cells, in reading order |
|---|---|
| Walk | Opposite contact/support/passing phases, exchanging the leading foot and arms; deliberate wrap |
| Attack | Guard, retract acting fist, punch along facing, follow-through, retract, guard |
| Cast | Neutral, gather, hands prepared, release along facing, return, neutral; no painted particles |
| Other | Idle A, idle B, hurt, hurt recovery, dodge anticipation, evasive pose |

Adapt the literal structure below. Stage measurements are request targets, not output guarantees.

```text
Asset: one character animation atlas, <SOUTH/front | NORTH/back | EAST | WEST>.
Image 1 is APPEARANCE ONLY: <identity, costume, materials, proportions>.
Image 2, if used, is STYLE/COSTUME ONLY, not its direction or pose.
Keep <camera/view description> in EVERY cell. North: back visible, face hidden.
Same body height, stage origin, light and costume throughout. <Equipment rule>.
Transparent PNG, <columns> by <rows> equal cells, complete limbs and reach margins.
Row 1: <individual walk phases, explicit opposite-leg support and passing>.
Row 2: <individual attack phases, SAME acting arm, reach in the facing direction>.
Row 3: <gather/release/recovery phases, body only; effects authored separately>.
Row 4: <idle/hurt/dodge cells>.
No labels, grid, ground, cast shadows, particles or additional characters.
```

Side view warnings: separately painting each direction is necessary when mirroring changes a marked pauldron, glove, scar, weapon hand, lighting or costume. A good side walk does not automatically match a broader three-quarter idle. Emberwake retains a visible walk-to-stance angle change; origin translations did not fix that drawing issue.

## Extract and register the actual return

Read actual dimensions/alpha before slicing. Keep raw output and actual tool-input hashes beside the prompt. Use one sheet transform and declared row corrections, not independent silhouette fitting. Preserve margins and legitimate soft edges.

The case baker used a 128×128 destination stage, pivot `[64,112]`, eight atlas columns and runtime draw scale 0.66 (roughly 63 px painted body height). Its initial banks use source anchor `[128,244]` and scale 0.42. Those are measured/authored compositor settings, distinct from the requested foot baseline; they are not calibrated physical foot contact. Do not copy them onto an unrelated image.

Initial selection exposed north drift and a side row-height jump. Explicit whole-cel root/row offsets corrected staging. Later idle/cast/attack banks needed their own authored pelvis-origin translations. Review the full loop and state joins afterward: centering each frame by its bounding box or forcing every foot to x 64 destroys meaningful motion.

The source baker removed disconnected backdrop/grid fragments from this connected unarmed body, normalized hidden RGB and used the case thresholds alpha<24→0 and alpha>245→255. These are recorded transformations, not universal alpha rules. Do not erase legitimate separated accessories, effects or soft contours just to obtain one component.

## Correct a weak side walk with pose authority

The original east/west row repeated contact-like poses. The successful correction supplied eight existing walk phases as **pose/layout authority**, with the hero image as **appearance authority**. The request specified contacts in cells 1/5 and passing poses in 3/7, complete gloves/boots, one camera and no repeated long-stride contact in every cell.

Its actual return was 1774×887, despite the requested grid. One whole-sheet nearest resize to 1792×896 made a four-by-two grid of 448 px cells; extraction then used one scale 0.248 and source anchor `[224,425]`. The baker applied explicit row shifts −2/+3 pixels. West walk mirrors this corrected east walk with the declared one-pixel stage correction about x 63.5. Other west actions remain separately painted. This is conditional symmetric reuse, not four independently painted walk cycles or eight-direction art.

A new asymmetric character requires a separately authored west walk. Do not mirror an asymmetric character merely because this symmetric unarmed case allowed it.

## Targeted north attacks and passing legs

North attack initially punched sideways. A row-only repair requested an away/up-screen punch with legitimate back-view occlusion, hidden chest/face and a traceable acting shoulder. One returned contact switched arms; it was rejected and the valid first contact was repeated in the following exposure. Repeated exposure is not another drawing.

Four front/back passing poses were requested together in a two-by-two edit. Inputs included the existing body/layout, previous failed attempt and a schematic pose-only guide. Each cell named its screen-left/right support and swing leg. The compositor restored the old body outside native ROI `[45,81,87,121)` (right/bottom exclusive), including transparency. Source cells were south 1/4 and north 49/52. Equality outside the mask was asserted on actual decoded RGBA; prompt instructions alone did not establish preservation.

The selected outputs are the direct composites. A proposed centering of both support feet was not selected. A later rigid-boot/source-map trial reduced the height gap but stretched/compressed thighs and introduced overlap, so it also remains unselected. Correct coordinates and preserved pixels cannot supply believable anatomy. Keep equal-clock held-pose controls and inspect the full gait, not isolated leg diagrams.

## Selected case manifest and clocks

The atlas stores 116 cells, including unselected older side-walk paint; that is not 116 unique approved poses. Four directions × six body actions = 24 selected clips. There are 116 selected exposure slots using 104 distinct cell indices and 103 distinct RGBA images. Repeated contact exposure and mirrored art remain disclosed reuse.

| Bank | Actual selected walk order |
|---|---|
| South | `5,0,1,112,2,3,4,113` |
| East | `96,97,98,99,100,101,102,103` |
| North | `48,49,51,114,50,52,53,115` |
| West | `104,105,106,107,108,109,110,111` |

All walks have eight holds of 9/160 s, total 0.45 s. Initial per-direction base banks occupy 0–23,24–47,48–71,72–95. The later east/west walks and four passing keys append at 96–115. Atlas row order is not the gait's semantic phase order.

| Clip | Case holds in seconds | Loop |
|---|---|---|
| Idle | `.58,.58` | Yes |
| Walk | Eight × `.05625` | Yes |
| Attack | `.06,.07,.055,.055,.065,.105` | No |
| Cast | `.06,.08,.10,.08,.08,.10` | No |
| Hurt | `.09,.10,.10` | No |
| Dodge | `.045,.105,.055,.055` | No |

The custom `emberwake-animation/v1` manifest records cell/pivot/draw scale, frames, positive holds, loop and per-frame raw source hash/cell/transform. It needs the case baker/game checks, not the companion's generic validator without an explicit schema adapter. These timings are authored gameplay choices, not recovered native motion timestamps. Frame identity, authored event clocks and physical movement remain separate. Damage must not repeat for every render of the contact cel.

The game uses four cardinal sprite facings. Movement can be diagonal; the dominant component selects the sprite, with vertical winning a tie. The last movement supplies facing/aim. This does not create diagonal artwork. Attack aim is locked for its commitment; choosing a different rendering architecture must keep that relationship explicit.

## Enemy views and the final rear release

Enemies use front/back three-quarter neutral/step/windup/strike banks with mirrored left quadrants. Disclose this instead of claiming four cardinal turnarounds. The final selected bank has all 24 enemy pose images across three kinds; its sparse keys still limit fluidity.

Repeated Warden rear-strike requests crossed the club over the opposite shoulder and switched the holding arm. The successful bounded request kept the club on the image-left side of the crown and extended that same arm diagonally away/up-left; the opposite empty fist stayed empty. The 1254×1254 return used a single 256×256 nearest conversion, alpha cleanup and whole-cel `[0,-3]` translation. This is new full-body paint, not a protected-body edit. Independent art review accepted arm ownership/identity/footing; the exported game later displayed `back_windup→back_strike→back_neutral` in actual play. A sampled sequence still does not prove excellent smoothness or calibrated ground impact.

## Reproduce and judge separately

Original single-character example: `/home/astra/projects/emberwake-demo` at commit `faf4362`. The working directory may now contain later character expansions; do not call that mutable path an immutable snapshot. Read `docs/ART-PIPELINE.md`, literal `art-source/hero/*prompt.txt`, `art-source/hero/passing/provenance/request-*.json`, `scripts/bake_assets.py` and `assets/hero/animations.json` for full case-specific offsets and lineage. The passing request's desired centered support foot was not the selected later warp result; follow selected manifest/receipts, not a prompt's intent.

Offline fresh-output commands (no model call):

```bash
cd /home/astra/projects/emberwake-demo
test ! -e /ABSOLUTE/FRESH/hero-replay || exit 1
test ! -e /ABSOLUTE/FRESH/rear-release.png || exit 1
python3 scripts/bake_assets.py --output /ABSOLUTE/FRESH/hero-replay
python3 art-source/boss-release-v1/bake.py --output /ABSOLUTE/FRESH/rear-release.png
```

Replace the placeholder paths with new absolute destinations first. The hero baker defaults to production assets and permits an existing output directory, so supply `--output` and enforce freshness before invoking it. The Warden baker rejects an existing target file. Do not run either against approved files. Check actual atlas/manifest hashes against the retained selected files. The five hero bake artifacts were reproduced exactly. Dependencies are recorded in the project's `requirements-art.txt`; the full project is case evidence, not bundled into this skill.

Review all affected adjacent poses, wraps, idle/action/hurt/dodge joins and all directions at native, nearest 2× and actual game scale. Use the case-free reviewer rubric before scored histories. Separate identity/drawing, consistency, motion and runtime behavior. The hero set received 7.7 overall (motion 6.9); the complete compact demo later received 8.0 overall. Those are distinct judgments. The user liked the demo while explicitly noting more remains to do. Neither result establishes all 24 clips at 8/10 or a finished commercial art library.
