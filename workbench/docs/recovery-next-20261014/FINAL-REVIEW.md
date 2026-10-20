# Final bounded cross-review

One material labeling issue was identified and corrected by root: the twenty identical main/quantized pairs include **15 animation-related frames plus five UI/terrain outputs**. The consolidated README now says “Retained paired outputs” and gives that split. They must not be described as twenty animation before/after pairs. The separate changed Pro Flash pair is a still image, not a changed animation sequence.

Reviewed canonical README SHA at this pass: `73736d4b994c05ed7978d0826a92117f6a3dd46db0a6fa1c0a6f1e4afd6e4609`. Reviewed phase verifier SHA remains `cd9def6616316b6752b591efd87917ceaa9d4523dc7a618c6b8a9edc47755717`. Root/research/captures were read only. No network, credentials, provider calls or generation were used.

## Independently checked facts

* Both original phase plans pass the final verifier under Python `-O`, writing fresh review receipts: first phase **10 cases/24 returned PNGs/3.7 reported generations**, corrected-connectivity phase **2/2/2.0**. Total:12 listed completed captures,26 returned PNGs including palette strips,5.7 response-reported generations. This is not account-balance reconciliation or proof of unrecorded-call absence.
* Direct comparison of corrected cutout PNGs confirms **89 full-RGBA pixel differences**. An independently written four-neighbor/top-left-background/max-channel-distance≤32 flood candidate misses Complex at exactly **`(20,48)`**: prediction `[0,0,0,0]`, actual `[30,160,80,255]`. That one counterexample prevents calling this an exact recovered mask method.
* Direct epsilon-output checks confirm **zero RGB mismatches** against equal-weight raw sRGB nearest black/white, and **1,591 RGBA differences per frame** against retained nondithered outputs. This does not establish the general positive-strength dither formula.
* The earlier palette analysis binds32,768 RGBA entries with zero weighted-Oklab mapping mismatches using the **returned palettes**. Those entries contain repeated RGB values and duplicated/correlated frames; they are not independent samples or an independent palette-construction prediction. The three4-color centroid agreements and24/32 agreement do not close initialization/convergence/rounding. The explicit requested sizes were4/32; automatic size detection was not tested.

Review receipts and the independent pixel measurements are preserved under `/home/astra/artifacts/pixellab-palette-capture-review-20261014/final-crossreview`. `MEASUREMENTS.json` pins both verifier outputs and measured counterexamples; its SHA is `79f0360ce9e2721fe7b58fbc7a4d6c43a1ed05b804848fa4416a2dda210b3b31`.

## Links and claim limits

The cross-linked detailed palette/dither/cutout/paired-color reports retain their counterexamples and distinguish original source, inferred rules, fitted candidates and unknown private stages. The consolidated README explicitly declines private parity, animation acceptance and completion; its next integration/video checks remain future work. REA is correctly described as independently decoding retained producer HARs, not independently observing the original transaction or attesting server internals.

A local Markdown-link check found only the two anticipated not-yet-created README targets, `VERIFICATION.json` and `ARTIFACT-MANIFEST-PIN.json`. They were pending root's final write and were not reviewed here. No other missing relative Markdown targets were found among the current report files. The broad655-test count is root's retained suite result; this cross-review did not rerun that suite or inspect every historical paired-source file.
