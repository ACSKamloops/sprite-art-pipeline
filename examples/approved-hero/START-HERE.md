# RPG hero animation workspace

The current delivery is the [RPG animation library](exports/rpg-library-v1/README.md):18 action types in the existing east-three-quarter view,25 playback clips plus a ready still. The original H3 walk is preserved, and the user endorsed the repaired punch/jump as a working baseline. New clips have individual review scores and remain candidates for human timed acceptance.

Open [the local animation player](http://localhost:8889/game-ready-v6/current-project/work/rpg-library-v1/review/index.html?clip=run), or use the [self-contained Godot project](exports/rpg-library-v1/godot/project.godot). Read [the current results and handoff](docs/rpg-library-results.md) for coverage, editable art, verification, quality limits and next steps.

Six planned painted actions remain missing after the H3 quota limit; the user chose to finish the available clips first. Their guides are preserved. Front/back/west art, calibrated physical jump/ground motion, equipment anchors and effects remain separate work.

The sections below document the original approved walk and first punch/jump production. [Earlier action player](http://localhost:8889/game-ready-v6/current-project/work/action-production-v1/viewer.html?clip=jump_latest) and [first action results](docs/action-results.md) remain available.

## Use the approved art

- `approved/walk/manifest.json`:30 original128×128 RGBA PNGs, exact1/24s holds,1.25s loop. Original PNG bytes are retained.
- `approved/walk/sheet.png` and `clips.json`: verified6-column atlas and portable engine contract; every cell is exact fullRGBA.
- `previews/walk.mp4` and `previews/walk.apng.png`: original tested presentations.
- `editable/walk.project.json`: self-contained30-cel fine-edit project, one unlocked flat layer.
- `editable/walk.aseprite` plus adjacent `.sprite-lab.json`: actual LibreSprite save/reopen output and native timing sidecar.
- `character.json`: identity, costume, scale, view, reference files and source hashes.
- `approvals/walk.user.json`: current scoped human acceptance. Historical mechanics receipts keep their original status wording.

Check the released snapshot with `sha256sum --status -c PROJECT-FILES.sha256` from this folder. Intentional editing requires a new snapshot and scoped review. `work/` and prepared provider jobs are mutable and excluded.

## Reproduce and inspect

The exact submitted appearance, dithered guide, literal prompt, saved H3 return and sanitized request fields are in `references/` and `reproduction/`. Read `docs/successful-walk-recipe.md` for the complete evidence chain. The later cleaner guide is a different input. Repeating a stochastic API request does not guarantee the same output; offline reconstruction from the retained return is reproducible.

From this folder, with Python3, Pillow, NumPy, ffmpeg and ffprobe available:

```bash
mkdir -p work
python3 tools/bake_native_sprites.py --video reproduction/returned-h3-native.mp4 --recipe reproduction/bake-recipe.json --output work/my-fresh-bake
python3 tools/animation/scripts/animation_assets.py validate clips.json --report work/atlas-check.json
python3 tools/sprite-toolkit/scripts/sprite_edit.py validate editable/walk.project.json
```

The bake output must be fresh. The supplied `work/offline-rebuild` is an actual completed reconstruction; `work/offline-rebuild-verification.json` binds all124 matte PNGs and all30 approved selected PNGs to the historical outputs. All3525 green-channel edits replay/undo. `work/rational-clock-check` exercises a non-unit2/3s native hold with an actual video.

The existing local-server shortcut is http://localhost:8889/game-ready-v6/current-project/tools/sprite-toolkit/editor/?project=../../../editable/walk.project.json (while that server is running).

For the browser fine editor, serve this folder locally and open `tools/sprite-toolkit/editor/?project=../../../editable/walk.project.json`. Edits stay in the loaded project until exported/downloaded. Use masks, onion skins, guides/diff, pencil/eraser, undo/replay and editable exports. The body is flat paint, not an anatomical rig.

For a fresh editable-project delivery:

```bash
python3 tools/animation/scripts/project_delivery.py editable/walk.project.json work/my-fresh-delivery --animation walk --toolkit tools/sprite-toolkit --actor generic_rpg_hero --columns 6
```

This yields exact clock/source manifests and a Godot resource-test project. It is not a completed gameplay controller. Read `docs/toolchain.md` for provider preparation, claim-next and the Godot timing limitation.

## Start the next actions

Read `actions/briefs.json`, `docs/next-actions.md`, `actions/project-bindings.json` and `docs/equipment-tracks.md`.

1. Author a same-view neutral/ready pose and the strongest punch/jump keys. Check character identity, complete limbs/costume, silhouette, framing and pose mechanics before generating the rest.
2. New actions use a fixed192×192 stage with unchanged painted body scale and constant source padding(+32,+64), nominal pivot[96,170]. Keep the accepted walk128 unchanged; align clips through their declared pivots. All new frame borders and airborne height still require checks.
3. Punch phases: ready, load, strike, follow-through, retract, settle. Jump phases: crouch, takeoff, rise, apex, fall, contact, absorb, recover. Proposed counts/times/events are authored briefs, not made art or verified gameplay.
4. Keep ground movement, airborne height, body cels, equipment, damage windows and effects separate. Jump landing is driven by actual ground contact, not the end of a video.
5. Validate all adjacent pairs/transitions and actual timed play, source-owned fine edits, editor roundtrip and Godot behavior. Human playback decides whether the performance is useful.

Weapons use measured per-frame anatomical hand/grip anchors and front/back/hand occlusion. Swaps require compatible motion profiles; a punch does not become a sword swing merely by adding a blade. `actions/attachments.example.json` leaves unmeasured anchors null and is explicitly not render-ready.

The original consolidation submitted no provider generation. Subsequent action production is recorded separately in `docs/action-results.md` and `actions/production-status.json`; the frozen briefs remain the original planning inputs. New art remains candidate work, and the attachment renderer is still pending. Old experiments remain preserved under the research root recorded in `evidence/source-copies.json`.
