# Loaded upper-body candidate v2

This localized authored construction separates the existing chest/shoulder/backpack source region above row 127 from the waist below it. Their disjoint masks recompose the original torso pixels exactly at rest. Both are recombined into **one `torso_pack` output layer**, retaining the original nine-layer assembly interface.

Two raised-cosine load pulses at phases .09/.59 compress the chest up to 1.35 px relative to the waist, with opposite 2.3-degree counterrotations around [132,129]. The sword arm and shield attach to this chest transform with restrained additional lag. Cape and tabard retain their original waist attachment. Head **angle** remains zero; head **position** follows 55% of the new attachment movement, bounded to 1.2 px on each axis. It is not position invariant. Source-colored hinge underlap is newly authored construction, sampled from approved source pixel [132,127], clipped to original torso alpha, and covered by the actual waist/chest source pieces. Existing hidden joint backing is inherited and explicitly remains non-source anatomy.

The underlying leg pack, hips, boot poses, convex greave/cap, stride and 1.2-second duration are unchanged. Passing/released poses return through the exact frozen legacy renderer, avoiding split-mask Scale2x edge differences. Scale2x8 is an approximation, not a claim of true RotSprite.

## Rebuild

Run from this techniques checkout:

```bash
python pilot/space-marine-captain/upper-body-rig-v2/build_preview.py --output "$PWD/pilot/space-marine-captain/upper-body-rig-v2/artifacts/loaded-v1"
python pilot/space-marine-captain/upper-body-rig-v2/build_preview.py --output "$PWD/pilot/space-marine-captain/upper-body-rig-v2/artifacts/loaded-repeat"
python pilot/space-marine-captain/upper-body-rig-v2/verify.py
python pilot/space-marine-captain/upper-body-rig-v2/compare.py
```

Existing output directories are refused. The root repository `/home/astra/projects/sprite-construction-lab` is a required readonly input. The wrapper executes its unchanged assembler with `runpy`, redirects `ROOT` to a private copied module under the legacy import name, and uses a readonly leg-pack symlink. The legacy constructor's part/rest/proof writes occur **only in the private snapshot**. Do not run the root assembler directly and describe it as readonly: its constructor writes its own upper-body directory. `receipt.json` binds exact assembler, retimer, upper source, candidate manifest and root frozen-upper bytes. Root's default retimer produces existing v18 holds (12–21 ms, 1200 ms total); this is not a new cadence authoring experiment.

## Bounded evidence

`receipt.json` proves 72 full-body repeat renders and all 648 layer renders byte-identical across independent outputs, hard alpha/source palettes, no canvas boundary clipping, exact lower layers/cape/tabard and physical-root/leg metadata preservation. Forty released full-body poses equal v18 control exactly. The native twelve-key comparison is `review/comparison-native.png`; reproduce the 2x version with `compare.py`.

I viewed the actual twelve-key native/2x comparison: separate chest settle is visible in loaded keys 7/43, restrained near/far counterrotation avoids a new broad body swing, and passing keys preserve the old source silhouette. This is a candidate for independent dense/timed art review, **not an artistic score or production acceptance**. It has one approved source view. It does not inherit a full-actor Godot moving-world contact certificate or prove anatomical correctness merely through partition/attachment checks.
