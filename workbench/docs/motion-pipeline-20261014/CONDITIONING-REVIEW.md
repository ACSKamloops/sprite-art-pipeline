# Independent conditioning review — bounded offline baseline

Scope: staged read-only copies of root's in-progress `motion_workflow.py`,
`calibrated_palette.py`, `motion_services.py`, `motion_provider.py`, and updated
`selection.py`, tested in the isolated state worktree. Only this report and
`tests/test_motion_workflow.py` belong to this review commit. No credential
function, provider submission/poll/download, HTTP request, or new art generation
was executed. Real local Godot and FFmpeg operated on tiny diagnostic fixtures.

## Baseline findings

The 24-case suite completed with **20 passed, 4 failed in 0.97 seconds**. These
are substantive regression assertions, without expected-failure masking. Root
was notified while implementing fixes/export traversal; this baseline does not
claim a final integrated or portable pass.

1. `condition(..., palette={'method':'calibrated-fixed'})` raises unstructured
   `KeyError('reference_raster')` at the original workflow line 171. Registry
   schemas reject the malformed request correctly, but the direct Python API
   needs explicit required-key validation. Other invalid size/method/seed/NaN
   cases reject before selector execution and without new Store writes.
2. `retime(..., holds=None, roles=['a','b'], loop=False)` raises unstructured
   `TypeError` from `len(None)` at original line 227. Direct controls need list
   admission before lengths. These errors do not trigger model or fallback calls.
3. Complete conditioned → retimed → editable export → fresh Store import currently
   reports success while omitting the conditioning mask, recovered selector
   receipt and supplied palette reference. On the fixed tiny fixture, missing
   IDs were mask `1a30dfb3b830a952ae5fde1f1e7f57209d58491c697e88389be7ea03ceeff7a7`,
   palette `9f0d2e235ef1685209263dc881f4ef0138a6466f0c5c4478821cf21232286647`,
   and raster selection
   `adc3315c112c065045994df75f8e042423ae47062d12ace8832b9a431da0a27d`.
   This is the already anticipated new-kind traversal gap, independently measured.
4. A separate tiny three-frame FFV1 decode → authored sample `[2,0]` → condition
   keep → retime → cold editable import loses raw ffprobe evidence from the native
   extraction. The first missing probe was
   `ad6cf4fbe056f6a8bbdf5f3a10516ca49727b7070dc08d196bafc8b73f5e0d76`.
   The same regression also requires preservation of the unsampled native middle
   frame, so an exported sample cannot silently become the only native evidence.

## Verified behavior and boundaries

- **Source/raw preservation:** keeping canvas/background/palette preserves every
  RGBA byte, partial alpha, nonzero hidden RGB, rational hold, integer PTS, frame
  IDs, event declarations and original immutable document.
- **Whole-canvas resize:** 8×8 → 4×16 matches exact nearest-neighbor pixels.
  Frame pivots, `ground_pivot` and per-frame `landmarks` scale by the same declared
  horizontal/vertical factors. IDs, PTS and holds stay unchanged; no pose fitting.
- **Real recovered selector:** a tiny opaque green exterior selects exactly 48
  border-connected pixels; the enclosed same-color patch remains. The original
  source raster remains exact. Execution receipt reports unchanged source input.
  This is the recovered manual selector, not semantic or automatic cutout.
- **Honest mask/palette staging:** mask erasure changes only selected RGBA before
  the global palette. A one-blue-color palette then changes unselected RGB too,
  while preserving all post-cutout alpha. The receipt correctly claims
  `outside_mask_rgba_preserved_before_palette`, not overall outside-mask RGB
  preservation. Hidden RGB can become nonzero after palette remapping; explicit
  editable-copy normalization remains a separate operation.
- **Calibrated palette:** module output is exact against the prior executable
  `scripts/replay_pixellab_fixed_palette.py` on deterministic random pixels and
  matches both retained six-color nondithered response PNGs in complete RGBA.
  Partial/transparent reference palette entries and non-uint8 palettes reject.
  Reference extraction keeps opaque colors in first-seen order without clustering.
  This remains the calibrated quarter-lightness Oklab hypothesis; private source,
  automatic palette construction, tie behavior and deflicker are not recovered.
- **Authored timing:** explicit rational retime retains the parent/native clock,
  source PTS and parent sequence; strips obsolete source `fps`/`duration_ticks`
  from the derivative; stores roles, loop and play count. Existing nonempty event
  metadata rejects without an explicit remapping. No inferred animation events.
- **Provider boundary:** registry rejects malformed controls; submit while provider
  execution is disabled raises validation before any credential loader. This is
  not a test of enabled provider execution, HTTP routing or paid jobs.

## Exact baseline source pins

| Staged file | SHA256 |
|---|---|
| motion_workflow.py | `0af4031547135c9cb10222c3b0a39d01b3ee9486240cab06453b2f5b5c235016` |
| calibrated_palette.py | `26c9d41b5da8f27c27360cf2c8e85b277e3b756dab97cd01a9b3f3be9babe46a` |
| motion_services.py | `e2eb6cd1a77e95b2ea66477debc282ec4f6907a741633abb7c742176ee710ba8` |
| selection.py | `a08dcf5c707411977967173f0ebec72585e84c78b3be8f0e205b0a79e55c40e2` |
| motion_provider.py (import only) | `cf0dac4b657f00b5d74f5cf250a7a761f6a4972b52637aff2e5407d39e6b696a` |
| baseline export.py | `3d3ea9a037699768389f9c3538ce714754e0fe30eab65d148e93e9a608780fe8` |

External palette fixtures are under
`/home/astra/artifacts/pixellab-reducer-recovery-20261014-phase2/`.
The test freezes source/palette/output SHA256 values individually; the source
cube includes all 4096 RGB cube samples plus gray ramp, and the second response
covers alpha stripes. External fixture absence causes only that retained-probe
check to skip. Ordinary diagnostic checks remain independent of research data.

Run the bounded suite after root's source modules and closure fixes are integrated:

```sh
/home/astra/projects/pixellab-local-workbench/.venv/bin/python -m pytest -q tests/test_motion_workflow.py
```

This baseline preserves the failures. A later append can qualify their resolution
against newly pinned source and a completed rerun. No continuous visual quality,
provider interoperability or complete-system readiness is inferred from these checks.

## 2026-10-14 follow-up — four baseline failures resolved

Fresh canonical working copies were staged read-only against root HEAD `37888f2`.
Because these were in-progress files, the exact file hashes below identify the
reviewed snapshot independently of that HEAD. The targeted suite completed with
**26 passed in 0.99 seconds**; no skipped or expected-failure checks. The original
20-pass/4-failure baseline above is preserved.

- Missing fixed-palette reference and malformed retime list types now return
  `ValidationError`. The `roles=None` case uses the correct hold count, so the
  regression exercises role admission rather than an earlier count mismatch.
- Both fresh-Store export/import tests pass. The conditioned/retimed package
  retains selector receipt, binary-alpha mask, supplied palette reference and
  referenced rasters. The tiny-video package retains original media, raw probe,
  extraction, authored sample decision and the **unsampled** native middle frame.
- The keep/resize canvas limit intentionally expanded from 512 to 2048 per side
  (32-frame/16M aggregate output budget); the invalid-size test now uses 2049.
  A positive 513×8 keep-mode case checks exact nearest pixels, unchanged source,
  original PTS and rational holds, without invoking the selector. A separate
  513×8 recovered-selection request still rejects before selector execution;
  the original manual-selector limit remains 512 per side.
- Real tiny Godot selection, retained nondithered palette-response byte checks,
  geometry transforms, source alpha/clock preservation and disabled-provider
  validation continue to pass. No provider or credential calls were made.

| Reviewed follow-up file | SHA256 |
|---|---|
| motion_workflow.py | `fdd5c103f39b4b7128e683ecc7f37a9648204a65861a459886d679160981f4b3` |
| motion_services.py | `61b559908ea4d012e9f2e143bd78a174c67f47be90085395f281d83fb6a2d2d9` |
| export.py | `c227b083bd60a4199ec08c422a49ded27625ff6af1cc16d124cd6cbfe36be3be` |
| selection.py | `a08dcf5c707411977967173f0ebec72585e84c78b3be8f0e205b0a79e55c40e2` |
| calibrated_palette.py | `d5754ffa1f9a1c1069d0e851ab2ea3741ae27937d94e748b30ea6b9e5c36417f` |
| motion_provider.py (import only) | `cf0dac4b657f00b5d74f5cf250a7a761f6a4972b52637aff2e5407d39e6b696a` |

This closes the four measured backend regressions within the suite's scope.
It does not establish private PixelLab equivalence, continuous animation quality,
full native-video browser compatibility, paid-provider behavior or a full-system
acceptance result. Staged root-owned copies were removed/restored afterward;
only tests and this report are committed in this follow-up.
