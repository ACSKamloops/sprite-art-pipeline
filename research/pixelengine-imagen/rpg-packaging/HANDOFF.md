# RPG bank packaging handoff

The importer and browser are implemented in `../tools/build-rpg-bank.py` and
`../tools/rpg-bank-review.html`. They use Pillow plus the repository's existing
construction, ASE and rational APNG toolkits; no generation, network, credential
or third-party processor call occurs. Root owns integration and additional banks.

Run from the repository root:

```sh
python3 research/pixelengine-imagen/tools/build-rpg-bank.py import-sheet \
  --recipe /external/recipe.json --contract /external/CONTRACT.json \
  --output /external/fresh-bank
python3 research/pixelengine-imagen/tools/build-rpg-bank.py verify-bank \
  --bank /external/fresh-bank --report /external/fresh-verify.json
python3 research/pixelengine-imagen/tools/build-rpg-bank.py assemble \
  --contract /external/CONTRACT.json --bank /external/fresh-bank \
  --bank /external/another-direction --output /external/fresh-review
python3 -m http.server 8936 --bind 127.0.0.1 --directory /external/fresh-review
```

Open `http://127.0.0.1:8936`. All output paths must be fresh. A failed import
retains diagnostics; use a new directory for the repaired attempt. `assemble`
accepts at most one generated bank per direction. Separate assemblies compare
different alpha/palette/preprocessing candidates. A rejected bank remains visible
but contributes no selected resource bindings.

## Explicit recipe

```json
{
  "schema": "rpg-bank-import/v1",
  "direction": "SE",
  "source": {"file": "/external/raw.png", "sha256": "PIN", "size": [1024, 1536]},
  "source_grid": {
    "y_boundaries": [[0,1],[271,1],[526,1],[774,1],[1033,1],[1290,1],[1536,1]],
    "reason": "Measured full-width opaque-alpha zero gutters; no subject cut"
  },
  "transform": {
    "scale": [27,100], "source_anchor": [[128,1],[246,1]], "stage_anchor": [40,72],
    "row_offsets": [
      {"row":1,"delta_source":[[0,1],[-15,1]],"reason":"Retain nominal source origin256"},
      {"row":2,"delta_source":[[0,1],[-14,1]],"reason":"Retain nominal source origin512"},
      {"row":3,"delta_source":[[0,1],[-6,1]],"reason":"Retain nominal source origin768"},
      {"row":4,"delta_source":[[0,1],[-9,1]],"reason":"Retain nominal source origin1024"},
      {"row":5,"delta_source":[[0,1],[-10,1]],"reason":"Retain nominal source origin1280"}
    ]
  },
  "alpha": {"mode":"binary","threshold":128,"canonicalize_transparent_rgb":true},
  "palette": {"mode":"preserve"},
  "clipping": {"mode":"reject"}
}
```

These partitions and offsets are measured **only for the first SE sheet**; other
sheets need their own measurements. Without `source_grid`, boundaries are exact
equal rational divisions of actual dimensions. Optional `x_boundaries` has five
rationals; `y_boundaries` has seven. Partitions increase strictly and span the
whole source. They never normalize pose scale by crop size.

`transform.column_offsets` is symmetric with row offsets:
`[{"column":1,"delta_source":[[-8,1],[0,1]],"reason":"Retain nominal column origin after measured gutter partition"}]`.
Row and column deltas add in source coordinates. Each is common to its whole row
or column, never a pose fit. For changed x partition start `b`, use x delta
`column*nominal_cell_width-b` to preserve the nominal source origin exactly.

For each destination pixel center `(x+1/2,y+1/2)`, source coordinates equal
`partition_origin + source_anchor + row_offset + column_offset + (dest_center-stage_anchor)/scale`.
The integer source coordinate is `floor`; samples outside the declared partition
are transparent. One scale and anchor apply to the whole bank. No alpha bounds
are used for fitting. Preserve registration maps; future geometric recomputation
does not replace them as exact replay authority.

Alpha preservation is explicit:
`{"mode":"preserve","remove_below":8,"canonicalize_transparent_rgb":true}`.
This preserves every RGBA value at alpha>=8, including partial alpha. Binary mode
removes alpha below its threshold and makes remaining positive alpha255.
Optional `chroma_key:{rgb:[r,g,b],max_channel_distance:n}` is a declared pixel
operation, never inferred. Alpha0 RGB is canonical zero for editable exchange.

Palette preservation is explicit. Optional fixed mode uses
`{"mode":"fixed","palette_rgba":[[r,g,b,255]],"source":{"file":"/external/palette-source.json","sha256":"PIN"}}`.
Supply the full ordered palette. RGB nearest uses squared Euclidean distance;
ties take the first color; prepared alpha remains unchanged. It is applied once
to the whole sheet, never learned per frame. The SE candidate uses all33 opaque
colors from the preferred project's34-entry palette (entry0 is transparent).
`exact-rgba-map` with `entries:[{"from":[r,g,b,a],"to":[r,g,b,a]}]` is also supported.
All source/palette bytes and the recipe are pinned. Newly built banks include a
portable `replay-recipe.json`; original recipe bytes remain preserved separately.

`clipping.mode=reject` is the default. Empty rasters, source-cell boundary contact
or transformed alpha outside80px stop before action export and retain
`REGISTRATION.json`. Explicit `record` requires a reason and retains warnings;
it is for a disclosed diagnostic candidate, not clipping acceptance. Integer
partition diagnostics report opaque pixels on both boundary lines, allowing a
zero-gutter check stronger than a single connected-edge count.

`review_status` accepts only `unreviewed` (default) or `rejected`; rejection needs
`review_reason`. The importer cannot promote art. `expected_staged_rgba_sha256`
can pin the ordered24 staged rasters for stricter recipe replay.

## Deliveries and stable callable

`BANK.json` records source/recipe/contract/script hashes, raw crop rectangles and
exact rational cell bounds, alpha/palette counts, per-cell source-map/output
hashes, six action manifests and warnings. Binary maps are80x80 row-major
little-endian int32 `(global_source_x,global_source_y)` pairs; `(-1,-1)` means
transparent. They replay against the prepared whole sheet without recalculating
geometry. `verify-bank` replays every map and compares staged/exported PNG, ASE
and independently decoded exact-delay APNG pixels and clocks.

Each `actions/<action>/` contains80px PNGs, atlas, rational `manifest.json`,
editable `project.json`, actual `editable.aseprite` plus exact-timing sidecar,
APNG plus verification receipt, and the existing Godot resource test builder.
ASE timing is a rounded millisecond preview; project/APNG rational holds remain
authoritative. Hand/grip/release anchors are explicitly `pending measurement`.
Events are authored data, not inferred contact, damage windows or gameplay proof.

For an external genuine-processor trial, dynamically import the Python module
and call the stable function:

```python
export_action(out, action, direction, images, data, provenance, cells)
```

`out` is a Path with `construction/` and `actions/` folders; `images` are ordered
RGBA80x80 stages; `data` is `contract['actions'][action]`; `cells` are original
source cell IDs, and `provenance` must bind the actual processor/input/placement
receipts. The function performs construction, ASE roundtrip and APNG checks.
No implicit rescaling or automatic external processor invocation exists.

The assembler copies the entire preferred source folder byte for byte, records
every file hash, and always selects original `walk_SE`. New SE walk is only an
experimental review variant. Other unreviewed banks can supply candidate resource
bindings. `COVERAGE.json` distinguishes missing, preferred, unreviewed and rejected
states, with independent variant roles. `clips.json` is portable resource input;
`build_godot.gd` may be run in Godot but no runtime test is claimed here. The
browser supports direction/action/variant, timed playback, frame steps, integer
scale/background/speed, one-shot hold/repeat/existing-idle recovery and keys.

## Retained task evidence

Artifact root: `/home/astra/artifacts/hero-rpg-expansion-20261021/packaging/`.

- `fixture-import/`:405x607 nondivisible sheet;24 stages, six actions; exact integer
  map replay, ASE RGBA/project roundtrip and APNG holds/pixels pass.
- `SE-preserve/` and `SE-binary-fixed/`: initial equal256 partitions;22 boundary
  contacts retained, not accepted. `SE-binary-fixed-partitioned/`: unsuccessful
  uniform+16 partition trial, with three source-edge warnings and no action export.
- `SE-binary-fixed-gutters/`: final measured partitions; zero warnings, no empty
  stages, no80px edge contact; all map/PNG/ASE/APNG checks pass.
- `SE-REGISTRATION-PROOF.json`: effective source row origins exactly
  `[0,256,512,768,1024,1280]`; every x/y partition has zero opaque pixels on either
  adjacent line. No subject can cross those empty lines.
- `review-SE-gutters/`: seed review package, seven clips/six selected resource
  bindings,42 missing action/view entries. Root should assemble the remaining banks.
  Preferred manifest SHA256 is
  `f8fc1aa82bdc4a17cda628bff262ba04581ffbe1c4c298671b1a9d8e11f826fc`.
- Actual Chromium opened the review UI; frame step/pause, punch→existing-idle
  recovery, missing-view behavior,1x scale and light background checks completed.
  Browser check used the initial equal-grid package; source/UI behavior is the
  same, but it does not approve the replacement pixels. One console404 was only
  favicon.ico; an inline favicon has since removed that request.

No human timed-art approval, external editor GUI save/reopen, gameplay/contact
test or whole-library quality claim. The review worktree remains owned by root
for cherry-pick/integration, then should be removed after its commit is retained.
The task-owned `/tmp/rpg-pack-scratch` copy was only ENOSPC recovery scratch;
the authoritative committed source is in this worktree. No unrelated workspace
or shared cache was cleaned.
