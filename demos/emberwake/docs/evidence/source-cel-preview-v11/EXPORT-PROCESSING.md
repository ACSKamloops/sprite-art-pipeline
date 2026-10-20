# Actual exported texture processing

The first raw-RGBA comparison failed for all three imported texture atlases;
all three exported JSON manifest hashes matched immediately. Those failed
results remain in `EXPORTED-BANKS.json` and `decoded-export/RAW-DIAGNOSTIC.json`.
The initial assumption that only fully transparent RGB changed also failed;
`EXPORTED-BANKS-PIXEL-DIAGNOSIS.json` retains that result.

Measurement finds unchanged alpha everywhere and unchanged raw RGBA at alpha
20–255. RGB changes occur at alpha 0–19, including 625 nonzero-alpha pixels for
Rowan, 911 for Lyra and 4391 for Brann. They are not all invisible pixels.
The existing texture imports use lossless mode, no mipmaps, no premultiplied
alpha and `process/fix_alpha_border=true`.

Godot documents this option as modifying colors around transparency
transitions. See [ResourceImporterTexture](https://docs.godotengine.org/en/stable/classes/class_resourceimportertexture.html#class-resourceimportertexture-property-process-fix-alpha-border).
An actual engine run loaded each raw source PNG, first verified its raw RGBA
hash against Pillow, then applied `Image.fix_alpha_edges()`. Every resulting
RGBA byte matches the decoded texture mounted from the actual served Web PCK.
All three JSON manifest bytes also match the selected bake. The six-resource
processed comparison passes without changing any art, import setting or export.

`inspect_export_processed.gd`, `EXPORTED-BANKS-PROCESSING-EXPECTED.json` and
`processed-export-verification/RECEIPT.json` retain that exact run. Use a fresh
minimal Godot project and fresh output directory to repeat the PCK inspection.
Then run `analyze_export_edges.py --artifact PATH --out FRESH.json` to compare
the retained decoded and expected-processed textures. Raw-source equality
must stay false; the processed expectation is explicit. This establishes
export binding and processing, not visual quality or continuous motion.
