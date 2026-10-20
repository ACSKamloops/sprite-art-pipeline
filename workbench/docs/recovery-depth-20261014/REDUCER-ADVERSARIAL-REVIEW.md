# Independent supplied-palette reducer review

The retained nondithered/zero-strength outputs match an independent scalar implementation of weighted Oklab nearest-palette mapping: **73,728 RGBA entries, zero mismatches**. That count includes repeated requests, repeated gray ramps and the same RGB samples at different alpha values. It is not73,728 independent colors or trials. This is a fitted behavior on seven retained public `/v2/reduce-colors` captures, not recovered private source or certification of the PixelLab animation pipeline.

[REDUCER-INDEPENDENT-EVIDENCE.json](REDUCER-INDEPENDENT-EVIDENCE.json) contains numerical results and exact PLAN/request/transport/HAR/REA/source/output hashes. [The independent helper](../../scripts/recovery_depth/review_reducer_independent.py) reads artifacts only and uses scalar Python arithmetic and Pillow decoding; it does not import, execute or call the root replay/probe scripts. It performs no network, credential, model or provider operations, and writes no artifacts. This review writes reports only in its isolated methods worktree.

## Heldout result and count correction

The nine-color opaque palette heldout produces8,192 exact RGBA matches:4,096 samples in the opaque image and the same RGB samples with striped0/64/128/255alpha. All alpha and hidden RGB predictions match. There are **4,094 distinct RGB colors**, not4,096; two sample repetitions occur. One distinct color also appeared in calibration, leaving4,093 previously unseen distinct RGB colors. The root's initial hardcoded `heldout_rgb_colors_tested:4096` and “4096 fresh RGB colors” wording need the samples/distinct distinction. The final read-only source check confirms the root analyzer now derives both sample and distinct-color counts from the actual heldout input.

For each heldout image, unweighted Oklab differs at1,258 RGB pixels and sRGB Euclidean distance differs at1,011. This discriminates the fitted mapping from those two tested alternatives on these inputs. It does not establish uniqueness against all candidate metrics, precision choices or implementations.

The distance `0.25*dL² + da² + db²` succeeds, but the finite nondithered winner decisions also admit an L-weight interval approximately **[0.249909225276,0.250040381755]**, using the same Oklab conversion. Endpoint ties require separate handling. Thus0.25 is a successful representative fitted value; it is not uniquely recovered private precision or a confirmed server constant. No exact equal minimum-distance ties occur in these retained inputs. The root replay's `argmin` first-palette-entry tie convention remains an untested local convention. Deliberate equidistance probes, duplicate palettes, reordered palettes and nonopaque palette entries were not covered.

## Predeclaration, byte pins and capture authority

The heldout PLAN records its prediction and `prepared_utc=2026-10-14T03:51:04.270766+00:00`; its single HAR entry starts at `2026-10-14T03:51:04.402340+00:00`,0.131574seconds later. All seven retained PLAN timestamps precede their respective HAR start timestamps. This establishes ordering **within the retained self-recorded local timestamps**; it is not an independent external timestamp attestation or an immutable preregistration.

For every case, this review verified:

* PLAN's request-file SHA matches exact retained `request.json` bytes.
* The submitted compact JSON differs from the formatted request-file bytes, but equals independently compact-serialized request values exactly. Its SHA matches `_request_body_sha256`; images/palette base64 values are unchanged.
* The captured request is a POST to the expected public route; captured response is200, matches retained response JSON, and its unredacted text matches the recorded pre-scrub body hash. Extracted output PNG bytes match the captured response descriptors.
* Each REA subject SHA matches its complete HAR file, total-record count is1, and its normalized reported entry equals the actual retained HAR entry. Each REA ID and file hash is retained in the evidence.

The REA authority is `historical-reference`, with a subject bound to local Python-produced HAR. These are retained urllib HTTP records with auth omitted, not browser instrumentation or independent REA witnessing of live traffic. No authorization headers or credentials were read by this review. The seven retained responses report0.7generations in total; this is reported usage, not a new paid run.

## Scope and script review

The supplied palette distribution is fixed by the caller. This review establishes neither automatic palette selection/clustering nor palette-generation behavior. It does not recover ordered/error-diffusion dithering, neural rendering, de-flicker, cutout, temporal processing, MiniMax use of this reducer, model/checkpoint identity or the whole PixelLab pipeline.

The nondithered mapper deliberately fails the positive-strength2×2 dithered cases:1,483mismatches per image at strength5, and1,460per image at strength10. Strength0 matches the nondithered case. Those controls are counterexamples to any generalized “all reduce-colors modes replayed” claim, not unexplained failures of the stated nondithered scope.

`replay_pixellab_fixed_palette.py` truthfully marks its policy as inferred behavior and restricts supplied palettes to opaque entries. It preserves source alpha and maps hidden RGB. It refuses existing output/receipt paths and creates output with exclusive mode, avoiding overwrite. Receipt writing is a separate step: a failure there can leave a newly created PNG without a receipt; there is no transactional two-file guarantee. This is an ordinary incomplete-output state, not an overwrite or false completed receipt. A dangling receipt symlink can also fail only after PNG creation.

The paid probe script pins the prepared request, takes an exclusive persistent `.submission.lock` before POST, records attempted state, and has no automatic retry or redirect. This prevents duplicate submission in the same case directory. It is not global deduplication across copied/new directories or an external budget lock. An exception or crash after lock creation conservatively blocks another same-directory attempt; it may leave an ambiguous/incomplete capture rather than fabricate a successful result. No additional submissions were made here.

At the initially reviewed analyzer hash, provenance checks used Python `assert` and could be disabled under `python -O`. The final read-only source check confirms these are now explicit `require` checks raising `ValueError`, so optimization no longer disables them. The initial hardcoded heldout-color count was also corrected. The evidence pins the corrected analyzer snapshot. Missing files or unsupported data may terminate rather than produce a neat failure receipt: the repeat/zero byte reads occur after the per-case exception handler, and not every structural exception is caught. This is not a false-positive numerical result. The analyzer's explicitly selected `--output` path uses ordinary overwrite behavior; it is a report utility, not the preservation-safe image replay writer. Use a new report path if preserving a prior analysis receipt.

Root script hashes in the evidence identify the actually reviewed snapshots. The numerical independent result does not depend on the root analyzer's assertions, hardcoded counters or reducer implementation. No blocking numerical mismatch was found within the stated nondithered opaque-supplied-palette scope. Count, tie, parameter-uniqueness, timestamp authority and duplicate-safety qualifications must remain with the result.
