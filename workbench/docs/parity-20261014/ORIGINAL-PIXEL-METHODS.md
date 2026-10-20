# Original shipped client pixel methods

`sprite_workbench.parity_pixels.execute(store, operation, **request)` runs six
unchanged method bodies from the recovered Pixelorama extension in real Godot.
Complete original files are vendored with pinned SHA256s. Each receipt records
the verified manifest, function hashes, executed host/runner hashes, input RGBA
hashes, output hash, and input-preservation observation. No research checkout or
network connection is needed at runtime.

| Operation | Inputs | Original behavior |
| --- | --- | --- |
| `serialize` | `raster` | Raw RGBA transport, zeroes hidden RGB only where alpha equals zero; preserves partial alpha and input. Returns raster and raw bytes, not PNG. |
| `transparency` | `raster` | True if any pixel has exactly zero alpha. Partial alpha alone returns false. |
| `reference_palette` | `raster` | Builds 64×64 conditioning image with each visible distinct **RGBA** once, in x-major first-seen order and x-major output order, at most 4096 entries. Frequency is collected but each key is removed after its first write. |
| `mask` | `mask`, `art`; optional boolean `fill_background`, `inpaint_empty_image` | Supplied flattened captures substitute for host capture. Positive painted alpha becomes opaque white, zero becomes opaque black; optional empty-art/background rules are original. |
| `decode` | `media`, `width`, `height` | Valid PNG returns its actual dimensions and RGBA8. Otherwise valid raw RGBA uses declared dimensions. |
| `place` | `source`, `destination`; optional `origin`, `extent`, `preserve_mask` | Original copy/blit into selection rectangle and origin. Alpha-zero source erases destination. Optional preserve mask uses alpha, and Godot clips. Original destination remains unchanged. |

**Mask formats are different.** `mask` produces opaque black=protect and opaque
white=edit; consume RGB. `place` consumes positive mask **alpha**; an opaque black
pixel permits copying. The separate manual-selection tool produces white RGB
with binary alpha. There is no implicit conversion between these formats.

The wrapper admits only canvases 1–512 on each axis, raw RGBA ≤1 MiB, received
encoded files ≤2 MiB, single valid PNG, matching capture/mask dimensions and
bounded integer geometry. It rejects malformed magic-prefixed PNG before the
original decoder; the original could fall through to raw decoding on failure.
This stricter admission rule is local and does not claim original malformed-file
behavior. Original method execution uses external Linux `prlimit`: 4 GiB address
space, 20 CPU seconds, 2 MiB per output file, 128 descriptors, 30-second wall
timeout, two Godot worker threads. Output is verified before immutable storage.

Boundaries: `get_image` capture is a fixture returning supplied flattened images,
not recovered multi-layer application integration. The original undo call writes
to an output sink; this service does not mutate Studio history. Palette-image
conditioning is not a private quantizer, server palette construction, temporal
palette optimization or matte method. `place` currently receives RGBA rasters;
PNG decoding and placement are separate explicit operations. Whole requirement,
private backend and animation/art parity remain open.

`local.parity.to_sequence` requires an explicit rational still-image hold. Before
creating a sequence it verifies the complete receipt shape and source pins,
re-executes the original operation in Godot, and requires the deterministic
receipt ID to match. A copied public manifest hash alone cannot promote a
fabricated result. A changed Godot runtime requires a fresh operation receipt.
The resulting portable closure retains every input/output raster and received
raw/PNG blob. Source-shape painting additionally attaches its ordered original
footprint to the exact history receipt index; subsequent edits, branching,
undo/redo and cold export retain that evidence.
