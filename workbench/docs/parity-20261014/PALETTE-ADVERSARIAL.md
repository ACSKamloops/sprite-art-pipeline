# Palette-image importer adversarial review

Reviewed the unchanged shipped handler and host wrapper from owner commit `b56c733`, then its input-snapshot correction `b1f5f27` (local cherry-picks `59f5890` and `f7213de`). This review used no credentials, provider requests, or network calls. It covers the single-image **canvas-equivalent RGBA** entry point, not browser PNG decoding or the private `/reduce-colors` service.

## Material finding and correction

The initial wrapper serialized the caller's array before executing Node but computed its input hash and visible-RGB count from that mutable array afterward. A deterministic test runs the actual source runner on red/green pixels, then changes the caller's pixels to blue before the wrapper resumes. The returned palette was red/green while its receipt described blue. This is a provenance defect, not a difference in the original color algorithm.

The owner fixed this in `b1f5f27`: after checking the pixel budget, the wrapper copies one C-order snapshot and uses it for execution, hashing, and counting. The same counterexample now passes; the source manifest and original slices are unchanged. The test does not substitute a fabricated subprocess result.

## Independent cases and result

`python -m pytest -q tests/test_parity_palette_adversarial.py tests/test_parity_palette.py`: **27 passed, no skips, 4.69 seconds** in this checkout. The ten new adversarial tests initially produced nine passes and the receipt failure above; all ten pass after correction.

The tests challenge:

- Exactly 256 visible RGB values plus hidden extras: no reduction; first-seen order remains intact.
- More than 256 RGB values in two five-bit bins: equal-frequency ties retain the first RGB, including after input reversal; additional alpha-1 occurrences win by frequency, equally to alpha-255 occurrences.
- 257 RGB values collapsing to one bin: the original UI rejects the one-color result, with no palette update or success warning.
- Duplicate RGB values, alpha zero versus nonzero, and unequal frequencies: first-seen ordering and opaque palette output remain source-exact.
- Read-only arrays with negative strides: row-major input hashes and colors agree, with no caller mutation.
- The maximum 512×512 local budget succeeds; over-budget input fails before launching Node. Timeout and missing Node fail explicitly, without a replacement algorithm.

The source-comparison cases execute `tests/parity_palette_oracle.cjs`, which registers the full retained webpack asset and locates unique lexical anchors independently of the production manifest. Both oracle and production use explicit image/canvas host stubs; this is not an independent implementation of the algorithm and does not prove browser decoding. The retained asset was available for this run; the differential tests explicitly skip when it or Node is unavailable.

## Source pins and scope

Original asset: `/home/astra/artifacts/pixellab-recovery-web-20261014/assets/2713c302f049-create-9c5cec3372075418.js`, SHA-256 `819962c897d4640c126a5efa4b6c5a194819e7eeaf023b242d852a64df74779d`.

Webpack factory `97981`: `e9c6cb49052afbda45b9f16559a109f802dba299eab6fd3b166da3154188e0ee`. Original import handler `S`, UTF-8 bytes `[132618,135186)`: `ba3c98b358af99881d9a64565de8cfddcd9ead4546b3ebf67ff38379ff32dfd1`.

Reviewed final files:

| File | SHA-256 |
| --- | --- |
| `sprite_workbench/parity_palette.py` | `5f181e1b8a0869f5d4086b6fc719ab14b7409286c003f08d3d5ce1d277534128` |
| `sprite_workbench/parity_palette_runner.cjs` | `2b04ab709518b319409d7601b0e98f4dd7fe66321b877b3ea5c1d3ab1ba22d8b` |
| `sprite_workbench/parity_palette_source.json` | `a32ca0ece88e70b9199173f1af0e7ee0c1d1868ea3383df8cc652074565f0d3c` |
| `tests/parity_palette_oracle.cjs` | `2364a1f204c125b8f8001f37110a0b808e46efe8ba0fae5d995380a7353ffb02` |

The original handler has a fixed reduction branch above 256 unique visible RGB values; callers cannot configure a target count. Its distance helper is unweighted Oklab, distinct from previously measured private-service weighted mapping. The adapter admits post-canvas bytes: low-alpha raw PNG RGB can change during actual browser decoding, so raw PNG-to-palette parity is outside this API. The local pixel and execution budgets deliberately restrict the host. These finite synthetic cases do not establish exhaustive algorithm equivalence, private palette construction, GIF/dither behavior, packaging completeness, or whole-product parity.
