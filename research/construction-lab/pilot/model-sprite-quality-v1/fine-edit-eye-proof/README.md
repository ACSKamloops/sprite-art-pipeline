# Reversible source-attached eye/brow edit — v11

This is a bounded fine-edit demonstration on the final camera-relative-lighting v11 bow-walk candidate, not promoted artwork or a new-cycle approval. The character's unchanged rig, original UV textures, native 24 fps Walk and lighting generate the imagery. Only the authored eye/brow descriptor color and ellipse radius change, once at source. No frame pixels are painted.

`descriptor-before.json` and `descriptor-after.json` preserve exact source bytes. `semantic-patch.json` declares four color/radius operations, individual before-values, source descriptor SHA and exact archived v11 renderer SHA. `apply_edit.py` rejects stale hashes before writing and uses an atomic replacement. The active descriptor is left exactly rolled back after proof completion. The isolated original model/textures/license copies are checked against protected original hashes; v11 and original source files remain unchanged.

Twelve actual renders cover four directions at native sourceframes 0, 10, 20. All twelve baseline decoded RGBA images equal final v11 keys 0, 4, 8 exactly. The edited packed scene is reopened and actually rerendered in all twelve comparisons, also exact. Undo is proved by actual twelve rollback renders equal to the baseline, plus exact descriptor bytes. A stale second apply rejects without mutation; replay followed by undo also returns the exact source.

`comparison.json` reports each phase's actual changed bounds and component deltas. Actual UV-feature emission masks follow the same animated source UV geometry and visibility; the reported domain includes a two-pixel antialias allowance. At component delta ≥4, all changed pixels lie within that face domain, and alpha is unchanged in all twelve images. At delta ≥1, ten remote pixel occurrences differ outside the domain, magnitude at most3/255. These tiny render/GI differences are retained in the report, not falsely claimed to be zero. Hidden back-view marks make no visible edit. Side changes can be small because the face turns away. The contact/difference sheet was visually inspected for feature tracking and no visible hood/limb marks; this is not anatomy or full animation review.

`final-validation.json` contains 108 independent checks on actual pixels, source hashes, reversibility and localization. `edited/reopen-validation.json` binds the actual packed scene and native Blender reopening. `before-after-difference.png` / `-2x.png` show every compared sample. Difference magenta is a diagnostic, not a paint layer.

## Repeat

Use Blender4.5.9, CPU Cycles128/no denoise, fixed8threads. From this folder, verify existing immutable evidence:

```sh
python verify_final.py
```

To produce fresh renders, first copy this folder to an isolated scratch location while excluding baseline/edited/rollback/feature-masks output folders. Preserve `source/original/`, exact archived renderer, descriptors and scripts. `render_samples.py` is a documented adaptation of the archived renderer: only output destination, sample keys0/10/20 and sample-count metadata are changed. It resolves inputs within the scratch folder and refuses existing output directories.

```sh
blender -b -t 8 --python render_samples.py -- baseline
python apply_edit.py apply
blender -b -t 8 --python render_samples.py -- edited
blender -b edited/ranger-walk-render.blend -t 8 --python verify_edited_reopen.py
blender -b edited/ranger-walk-render.blend -t 8 --python render_feature_masks.py
python apply_edit.py undo
blender -b -t 8 --python render_samples.py -- rollback
python analyze.py
python verify_final.py
```

For a copied scratch folder, update only protected-baseline path resolution when verifying against a separately located frozen v11 pack; do not update expected hashes to bless changed inputs. The producer scripts bind current parent v11 paths in this committed fixture. New model UV layouts, larger radii, another feature or different lighting require fresh masks, renders and visual review. This descriptor only supports the two authored face ellipses; it is not a general clothing or facial topology editor.
