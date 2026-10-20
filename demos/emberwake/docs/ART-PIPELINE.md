# Art production and coverage

Current runtime authority is `assets/hero/animations.json` and its atlas. Loose proofs under `art-source/hero/` are historical v1/v2 evidence. Current selected proofs are `assets/hero/{game-scale-proof,selected-contact-sheet}.png`, intentionally excluded from the playable export. Review scores bind exact builds; no score automatically transfers across revisions.

## Hero

The appearance lock is the user's existing generic brown-haired hero: blue/gold tunic, silver shoulders/bracers, cream trousers and brown boots/gloves. Four separately generated24-key atlases supply genuine front, back, right and left art. All actual prompts and raw returns are retained under `art-source/hero/`. Generated sheet dimensions and alpha were measured; requested dimensions are not assumed.

An initial side-walk row repeated similar contacts instead of producing a reliable gait. Eight phases from the previously approved walk became pose guides for one new ImageGen painting call. Its actual1774×887 return uses one disclosed whole-sheet nearest resampling before uniform-cell extraction. Only the west **walk** mirrors this corrected east bank; the other west actions are separately painted. This symmetric reuse is intentional and disclosed.

The north strike initially pointed sideways. A targeted ImageGen repair produced useful north-facing keys; a returned contact that switched arms was rejected. The selected first contact is reused in its following exposure. Duplicate exposure is not new art.

The first review found north walk drift, side-walk row-height jumps, wrong phase ordering and disconnected alpha hairlines. The bake now retains full-pose pixels while applying explicit authored stage offsets, a consistent side-row correction and removal of disconnected nonbody components. It preserves the actual character contour instead of raising the alpha threshold to erase legitimate edges.

Four passing-leg keys were generated in two bounded edit calls. The original body above the lower-body ROI and outside `[45,81,87,121)` is pixel-exact. Source art, masks and replay scripts are under `art-source/hero/passing/`. The direct composites were selected; a separate experiment that forced both support feet to the centerline remains unselected because a centered foot is not a universal anatomical requirement. An equal-clock held-pose control is retained for review.

A later source-map trial in `art-source/hero/candidates/low-step-v1/` lowered the raised boot and lifted the support boot, retaining exact isolated boot plateaus and unchanged pixels outside the leg ROI. It remains unselected: reduced foot-depth separation also compressed the support thigh and stretched the swing thigh, while stronger changes introduced opaque overlap. Its 118-file frozen ledger and actual eight-key comparison are retained as evidence of the limitation, not a quality improvement.

The follow-up review found drift within in-place cast/idle banks. Explicit per-pose pelvis-origin translations correct those generated staging errors without resizing or repainting anatomy. They are authored origins for this game, not recovered physical root motion. Native/2× temporal reviews must check whether a correction creates a foot or state-join pop. There is no claim of calibrated sole/world contact, hidden anatomy recovery or a general rig.

`scripts/bake_assets.py` reconstructs the selected atlas and manifests from retained inputs. It verifies exact protected-body pixels for passing keys. The body stage is128×128, pivot `[64,112]`, world draw scale0.66, about63px body height. All four walk cycles are0.45s. Attacks last0.41s; casting0.5s. Those authored game timings are not native video timestamps.

| Coverage | Delivered |
|---|---|
| Four hero views | South/east/north/west |
| Body clips | 24: idle, walk, unarmed strike, cast, hurt, dodge in each view |
| Magic | Firebolt flight, frost nova, impact; independent body/effect clocks |
| Equipment | Hero unarmed; no delivered interchangeable weapon rig |
| Jump, sit, pickup-specific body paint | Not part of this demo's controls/set |
| Death | Gameplay death/retry, held hurt pose and fade; no separate authored collapse cycle |

## Enemies and world

`art-source/world-production/` is the self-contained ImageGen art workspace. Its exact prompts, actual input references, raw outputs and processing scripts cover the essential props, three tiles, title panorama and enemies. Original neutral enemy sprites are retained. The game's selected enemy bank adds front/back neutral/step/windup/strike keys. Left quadrants mirror the three-quarter views; that is not four independently authored cardinal enemy turnarounds.

Earlier Warden back-strike attempts switched its weapon hand. Those returns remain rejected and retained separately. A later bounded ImageGen edit kept the club on the same image side and extended that arm diagonally away/up-left instead of crossing it over the opposite shoulder. The selected `back_strike.png` passed a separate art check for arm ownership, stone/foliage volume and footing; the strike-to-neutral return is a sharper join that needs runtime judgment. `art-source/boss-release-v1/` retains the exact request, inputs,1254×1254 raw return, whole-frame transform and deterministic replay. This is a new full painted key, not an exact protected-body edit or a calibrated ground-impact pose. Back banks use documented whole-bank draw-scale compensation about the same foot pivot. The renderer retains a neutral fallback for a genuinely absent key without turning to front art.

The original shrine depicted a blue altar without a bronze bell. `art-source/bell/` retains its targeted ImageGen edit and registration receipt. The village lantern reuses an actual cottage-lantern pixel component with a literal mask and an authored wooden post (`compose_lantern.py`). World tree/roof canopy fades for the hero and nearby foes while preserving trunk opacity and physical collision.

`bake_ground.py` combines actual ImageGen tiles with the hand-authored map paths into one continuous2304×1728 raster. Continuous feathering removes block edges and cuts browser draw calls. Physical terrain remains separate collision geometry. The final shrine clearing is rounded/feathered. `art-source/GROUND-RECEIPT.json` binds tile inputs and route geometry.

`art-source/effects/` retains the actual ImageGen effect request/return/atlas transform. These images augment engine-drawn trajectories, hit boundaries and warning graphics; an effect image does not decide damage. `compose_audio.py` supplies an original deterministic synthesized score and cues, using no samples/models. Fonts include their license files under `assets/fonts/`.

## Reproduction and verification boundaries

```bash
python3 scripts/bake_assets.py
python3 scripts/bake_assets.py --output art-source/hero/candidates/new-held-control --passing-mode hold
python3 scripts/bake_ground.py
python3 scripts/compose_lantern.py
python3 scripts/compose_audio.py
python3 tests/run_checks.py
```

Use fresh candidate directories when experimenting. Model requests are preserved for analysis, not automatically resubmitted by any rebuild command. Keep world/quest validation, exact pixel preservation, actual export loading, browser controls and subjective art/game scores separate.
