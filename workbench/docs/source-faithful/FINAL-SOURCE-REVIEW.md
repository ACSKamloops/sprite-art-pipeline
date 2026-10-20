# Final bounded source workflow review

Reviewed runtime: `f0af029ad4bcdeb49c0fb1a31cc31555db10a5f9`, followed by
the four-line Recent input correction `f4e10a72a1597e4cf355de316e563250d8216311`.
Independent reviewer worktree: `pixellab-workbench-methods`.
No blocking source-method substitution or control feedback defect was found in
the reviewed workflow. This is a bounded review of source recipe/control/render
integration, not a review of every editor method or all possible source branches.

## Source authority and input flow

Read `web/source-vfx.js`, its `web/app.js` and `web/index.html` integration,
`source_workflow.py`, `source_controls.py`, and the packaged preset contract.

- Preset loading copies the packaged raw recipe into the input textarea.
- Reading controls submits raw recipe plus explicit values to the source service;
  the returned effective recipe is displayed as evidence, not substituted into
  the textarea. The frontend creates sliders/selects from returned declarations.
  It contains no equivalent of the original binding, shading, repair, or raster math.
- Render submits the raw textarea recipe and current values through the local
  job handler. `render_controlled_effect` sends declared input to the unchanged
  source renderer, which applies bindings once. Its effective inspection recipe
  is not fed back into rendering.
- Save recipe JSON requests the current source controls snapshot and downloads
  `declared_recipe`, preserving raw layer values and declared control values.
- Recent selection reads `source-controls` and restores `declared_recipe`, then
  obtains controls through the source service. It does not reuse normalized
  `rng:null` or already applied control output as input.
- Preview draws retained PNG frames directly on Canvas. Timeline arithmetic only
  selects retained frames using exact sequence durations and loop metadata.
  Editing rendered pixels is a separate explicit navigation to the local editor.
  It does not rewrite the source recipe or substitute a local algorithm into
  source rendering.
- Every stream's immutable sequence metadata includes the `pixellab_controls`
  receipt; existing editable export tests verify portable retention of that
  receipt and renderer identity. Candidate/unreviewed status is preserved.

No runtime files were changed by this review.

## Preset identity

The packaged `SOURCE-VFX-PRESETS.json` hash is
`f0c0e9d1a84fb1feb244b70124218381729850ed27d60448ab97aad892bbc40f`,
pinned by `source_workflow.py`. Its only recipes are `slash_arc` and
`energy_orb`. Both equal the original retained `get_preset` responses and existing
fixture recipes. Their provenance hashes, extracted JSON text hashes, and
canonical recipe hashes are checked by the existing packaged-preset test.
The independent fidelity tests additionally inspect the selected original HAR
requests: IDs 124 and 110 request preset names with `peek:true`, not locally
authored recipe payloads. Exact original response hashes are retained in
`FIDELITY-REVIEW.md` and the contract.

Focused verification completed with **3 passed**:

```
python -m pytest \
  tests/test_source_workflow_adversarial.py::test_two_packaged_presets_are_exact_pinned_retained_raw_responses \
  tests/test_source_fidelity.py::test_source_fidelity_presets_are_returned_vendor_data -q
```

No duplicate identity test was added: the integrated test already checks the
packaged data against the actual returned recipes, and independent tests check
the corresponding request provenance. These three checks do not constitute a
new whole-suite count. Root reported 527 passing whole-suite tests at this
runtime; this review did not independently rerun that full suite.

## Retained browser evidence inspected

Read root checkout `output/playwright/source-orb-variant-result.log`,
`source-restore-result.log`, `source-save-recipe.log`, and
`source-playback-samples.log`, plus the actual downloaded
`.playwright-cli/pixellab-declared-recipe.json`.

The retained variant result records size 14, eight 48×48 frames, candidate status,
and sequence
`509337e59fe567c3f5dc0506670ae7446c36071c45c974cc70efd2be834bfd7a`.
Recent restoration records that same sequence and size 14 without a visible
error. The downloaded JSON has raw `core.radius = 10` and declared size control
14, confirming the intended distinction from effective radius 14. The playback
record contains all eight sampled frames, 26 transitions, and three loop wraps
over its approximately 2.1 second sampling interval. These are inspected retained
browser records, not a browser session independently executed by this reviewer.
Root's reported Canvas-versus-Store byte comparison and mobile/editor checks
remain root-owned evidence.

## Limits and nonblocking observations

The independent original-bundle differential covers 17 retained family examples,
two retained server recipes, and selected diagnostic alpha/mirror/seed/clock and
control scenarios. It establishes selected adapter fidelity, not every branch,
all recipes, visual quality, private models, or current deployed server identity.

The initial review found that Recent restored recipe/controls but left separate
subject/images fields untouched. Root corrected this repeatability defect in
`f4e10a7`: fetch the original effect-recipe record, check its kind, and restore
its subject and image IDs alongside the raw declaration. This is input selection
plumbing; no original algorithm changed. The reviewer inspected the correction
and executed the actual updated class in an isolated Node host with minimal DOM
stubs: both nonempty raster-input restoration and clearing stale inputs for an
empty-input render passed, while raw core radius 10/control value 14 stayed
unchanged. These two host scenarios are separate from the Python suite counts.

The first retained browser attempt to seed stale values timed out because the
optional inputs were hidden and was excluded from acceptance. The completed
rerun's `source-stale-before.log` explicitly records subject `aaaa…` and named
image `stale: bbbb…`. After Recent selection, `source-final-input-result.log`
records empty subject, empty images, size 14, the same variant sequence, and no
visible error. The reviewer inspected this retained before/after pair; root
executed the browser interaction.
Save recipe JSON saves a recipe rather than bundling separate raster dependencies.

The underlying local raster/construction editor remains locally authored;
opening the exact rendered frames in that editor does not establish PixelLab
private pixel-workbench handler parity. Existing wording and the explicit
source/editor boundary should remain qualified that way.
