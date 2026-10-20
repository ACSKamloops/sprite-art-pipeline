# Lower-body source-art experiment — unapproved

This tests depth-specific painted leg shells beneath the immutable upright Captain upper body. It does not establish a usable walk.

`prompt.txt`, source-owned reference pieces and `guide.json` document the generation inputs. `raw-sheet.png` is retained unchanged. One whole-sheet nearest resize creates eight fixed128px cells; no per-cell fit is used. The anatomical guide is an authored projected silhouette, not a validated3D skeleton.

The generated sheet does not follow its requested phase order. `assemble_trial.py` explicitly selects cells0,1,2,3,4,6 into six200ms keys, adds one common placement66,120 and shared master pelvis translation, and composites exact source upper layers. Named phases remain proposals. Additional source keys are preserved.

Actual comparison videos: `/home/astra/artifacts/captain-pose-art-six-key-study-v1/`. Native/nearest2x, normal/half speed, color/silhouette, three loops. Successful export does not approve art. Source geometry, support, scale and phase sequence must be judged independently.

Observed benefit: rounded shell volume and visible incoming boot soles. Observed blocks: supporting foot changes size/location, motif proportions vary, free-leg passing remains weak, and upper/lower loading is not a coherent shared skeleton. Preserve this as a source-art comparator while canonical projected pose geometry is developed.

Reproduce the reference and guide with `python make_guides.py`. Build the comparison in a fresh output location with `assemble_trial.py` (its historical output is intentionally guarded). The generation is not deterministic; the saved raw output is the authoritative input for this experiment.
