# Depth-guided painted planes — failed binding experiment

The fixed3D pose packet supplies hip/knee/ankle and heel/toe projections. `render.py` binds a single generated neutral lower-body drawing to these targets, retaining the original upright-master upper layers. Source part ownership is explicit. Source anchors and hidden joint material are authored assumptions.

Trials1/2 show why correct projected landmarks are insufficient for art: a three-anchor affine foot transform flattens or elongates the painted boot into a slipper, even with near-zero anchor error. Trial1 also had an upper waist/chest registration seam; trial2 corrects the common source offset. Neither is art approved.

The next experiment uses a rigid volume-aware boot mesh with sole corners and upper shoe vertices. The source does not supply complete rear surfaces. Bone projection and texture binding must remain separate from appearance acceptance.

`source/authored-poses.json` preserves the first guide freeze used by these trials. `source/authored-poses-final.json` preserves the later canonical packet with segment frames; it is not silently substituted into earlier artifacts. `source/leg-master-128.png` is generated atlas cell0 used once as the authoritative leg drawing, rather than independently generated anatomy per frame.

`artifacts/trial-v1` and `trial-v2` are retained failed comparisons. Actual v1 video export is `/home/astra/artifacts/captain-depth-projected-art-trial-v1`. Technical exporter success confers no art acceptance.

Actual source-alpha inspection found all four guessed heel/toe locations in trial2 were transparent. This is a binding failure. Anchor equations must be checked against opaque source material before contact evidence is claimed. The subsequent mesh must record its material UVs and actual rendered coverage.
