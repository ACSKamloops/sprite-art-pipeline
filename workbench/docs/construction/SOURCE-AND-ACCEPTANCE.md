# Construction source and acceptance boundary

A corrected local indexed project/history and bounded32-bitRGBA LibreSprite exchange can be added to the workbench. They **do not close native Aseprite/Pixelorama indexed drawing, palette, history or shader parity**, and prior toolkit mechanics or prototype-art approval cannot transfer to the new code automatically.

This source-first specification freezes workbench `8e02205b492bc0527adf369f093efe63a2983250` and the exact current skill toolkit sources. [SOURCE-AND-ACCEPTANCE.json](SOURCE-AND-ACCEPTANCE.json) retains13 original line/UTF8/hash anchors,14 transferable requirements and18 independent future cases. No toolkit/runtime/native/provider/model function was executed during this specification pass. Producer-ready wrappers need a separate adversarial test receipt.

## Transferable state and edit methods

The toolkit contract is `sprite-edit-project/v1`, rather than a flattened RGBA-only document. Dense row-major cel indices, ordered palette entries, stable layer/cel/frame/animation IDs, shared frame bindings, ticks/fps/loop/events, landmarks and pivots must remain immutable and independently recoverable. Palette entry0 is reserved `[0,0,0,0]`; duplicate colors at other indices are valid aliases and must not be deduplicated silently.

The toolkit decodes `palette[index]`. The retained native Pixelorama shader decodes index0 as transparency and indexk as palette slotk−1. These are **different profiles**. Native progress/undo may reconstruct from current indices/palette instead of the proposed compressedRGBA buffer; the separate normal host serializer is not implicitly called by that helper. The9claim/17anchor native report is conditional source evidence, with host/version/GPU and undefined shader-fetch boundaries remaining. Local corrected snapshot undo is a named method, not proof that the native helper was reproduced.

A shared-cel edit intentionally affects all frames that refer to it. Every accepted transaction must bind the expected project and, for candidate patches, cel hash. Locked cels and palette edits affecting indices used by locked layers reject. Masks are unique full-canvas coordinates; outside-mask indexed data and candidateRGBA are guarded separately. Nonzero transparent aliases still count as occupied indices for translation clipping unless explicitly allowed. Timing/pivots change only by their named transactions; a timing edit that invalidates events must reject atomically.

Raw celRGBA and compositeRGBA are separate authorities. `render_cel` retains hiddenRGB; the composite skips alpha0 and normalizes an entirely transparent output to black. Partial-alpha composition follows the exact integer formula in core59–71. An independent one-pixel golden is `[106,95,136,136]` for front `[201,33,18,64]` over back `[21,151,241,96]`. A browser premultiplied readback or flattened PNG cannot prove index aliases or editable raw cel state.

History must preserve palette/index aliases, shared identities, ticks, events, pivots and project hashes through undo/redo, journal replay and branching after undo. Returned copies must not mutate accepted history. Recomputed receipt/precondition checking, rather than accepting supplied after-hashes, is required. The toolkit's mutable in-memory attributes are not themselves an immutable Store/transaction service; wrappers must enforce admission and content-addressed state.

## Upstream hazards that must not inherit approval

| Hazard | Exact source | Required local policy |
|---|---|---|
| Aggregate work is not bounded by one canvas cap | core19–46, history4–23, ASE35–49, export11/27–33 | Bound document/depth/strings, palette/layers/cels/frames/history/reference counts, total indexed pixels, rendered bytes and atlas/decoded work before copying or allocation. Test tiny over-count inputs or decoder spies, not memory exhaustion. |
| Integer conversion can leak a raw exception | canonical12–15, core40 | Reject unsafe huge direct integers before `math.isfinite`, and use finite portable JSON admission. Do not inherit canonicalization errors as unclassified process failures. |
| ASE decompression is eager | aseprite47 | Replace unbounded `zlib.decompress` with an expected-length-limited stream; reject oversized/truncated/trailing input before full decoded allocation. |
| Layer-order detection is ambiguous | core25, aseprite55 | Duplicate layer names are allowed by the project, while ASE import identifies order using names alone. Reject ambiguous exchange or preserve a verified stable identity. Do not claim all reorders are detectable. |
| Sidecar parsing and timing are not a hostile-input contract | aseprite55–57 | Strict finite schema and original-project binding; recompute selected sequence/cumulative timing, rather than trusting edited sidecar lists merely because they match an edited file. |
| Upstream exporters overwrite | aseprite31–32, export11–14 | Fresh/exclusive output and immutable masters. An ASE/sidecar pair is not automatically a crash-atomic transaction. |
| ORA is another unbounded archive path | export27–33 | Keep unsupported unless member/expansion/XML/PIL and ownership limits are separately provided. Existing LibreSprite proof does not establish ORA acceptance. |

These are observed source mechanisms and explicit ambiguity/resource questions, **not incidents already reproduced against forthcoming wrappers**. A wrapper may resolve them by safe admission or intentionally supported subset boundaries. Any vendored core changes need a patch/provenance record, rather than an identical-source claim.

## Editable exchange expectations

The declared ASE route is selected-animation, normal-layer,32-bitRGBA exchange. It can preserve cropped/linked cels with their actual offsets and fork edited frame bindings while retaining untouched frames. Groups, opacity/blend/z-order transforms, resized canvases, changed names/order/count/timing or unsupported chunks must not silently become a flattened success.

Authoritative ticks/fps/events/pivots/landmarks stay in the sidecar. Actual export code20–22 uses **cumulative boundary rounding**; three1-tick holds at60fps produce17,16,17ms, totaling50ms, rather than individually rounded17,17,17ms. Quantization error must be explicit. Floating overflow/collapsed or out-of-range millisecond holds reject, while original project data remains preserved. Repeated selected frame IDs require consistent external pixel edits; changed shared-cel occurrences fork according to the declared exchange policy.

The official ASE format link is inherited from the toolkit contract, not refreshed remotely by this pass. Imported file/sidecar bounds and schemas must still be independently checked. An ASE hash normally changes after legitimate external editing; that fact does not permit stale or arbitrary sidecar project/sequence/timing assertions. Original export identity and imported edit identity remain separate.

A real LibreSprite save/reopen gate must bind the exact binary/version, input/sidecar hashes, generated file presence, layer/frame order, quantized clocks, actual rawRGBA/partial alpha and complete imported project. Exit0 alone is insufficient. If the external tool normalizes hiddenRGB, record the actual loss and preserve the original indexed source; do not quietly award fullRGBA fidelity. Native8/16-bit indexed ASE semantics and full Aseprite host/raw-draw history remain unsupported unless separately implemented and tested.

## Frozen independent acceptance cases

The JSON specification contains a3×1 source with duplicate opaque palette aliases, partial alpha and a nonzero transparent alias, two frames sharing one cel, distinct tick holds, pivots and a contact event. Its18 cases cover unchanged aliases, shared edits, global palette history, locks, invisible-index clipping, candidate locality, branch/snapshot isolation, finite portable input, aggregate admission, partial-alpha math, cumulative clocks, cropped/linked placement, per-occurrence forks, ambiguous layer identity, bounded decompression, hostile sidecars, path preservation and actual tool exchange.

Expected values are deliberately independent of the producer's serialized receipts. Original indexed values must be compared even when decoded colors match. Sparse metadata, unchanged composites, successful exports and regenerated receipts cannot substitute for whole-project equality or actual tool artifacts. Failed transactions/imports must leave accepted heads/history/master inputs unchanged while reporting any retained candidate artifacts.

Producer-ready tests will be written in `tests/test_construction_adversarial.py` in this isolated worktree. The future case list is a specification, not18 passed tests. GUI editing/history, source/native affinity, broader archive variants and aesthetic/motion approval remain separately unverified. No provider, account, profile, private capture, new art or external call is required for this local source/acceptance pass.
