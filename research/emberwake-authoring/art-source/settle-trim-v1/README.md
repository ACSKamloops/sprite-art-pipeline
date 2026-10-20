# Brann south settle chest repair

Frozen input: `art-source/characters-v2/bake-v5/brann/atlas.png`, target116, same-view idle donor14. Candidate replaces385 torso RGB pixels inside the literal plan mask, excluding original head ownership. Target alpha is preserved exactly; the retained settle interior is alpha253, so this is explicitly a split RGB/alpha operation. Pose, arms, chest silhouette, head, all other pixels and timing remain unchanged.

The independent narrow review preferred the smaller neckline/central fastener and found no conspicuous seam; complete combined-bank review remains separate. Original116 remains stored; append the replacement and retarget only south attack/dodge settle references.

Replay without network/model calls:

```sh
python3 art-source/settle-trim-v1/replay.py --output /ABSOLUTE/FRESH/DIRECTORY
```

`source.png` and `donor.png` are the frozen input cels. `plan.json` binds their complete RGBA hashes and literal authorized coordinates. `journal.json` distinguishes donor RGB from target alpha at every actual changed texel. Mutation invalidates the preconditions. The first broad RGBA copy was rejected by the alpha guard; the fullyopaque-only follow-up made zero edits and earns no credit.
