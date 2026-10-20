# Callable local geometry replay channels

`sprite_workbench.replay_geometry.FLOW_IDS == ('F02','F09','F10')` and `run_flow(flow_id, store, output)` execute actual local diagnostic operations. They are not pytest wrappers or complete original whole-flow comparisons. The output path must be absent; existing files are preserved. These fixtures contain explicit asymmetric marker pixels, not proposed character artwork.

```python
from pathlib import Path
from sprite_workbench.core import Store
from sprite_workbench.replay_geometry import run_flow
result = run_flow('F02', Store('workspaces/replay'), Path('runs/F02-new'))
assert result['status'] == 'completed'
```

The JSON-safe receipt binds named SHA artifacts (including sequence), inputs/parameters, checks, exports, review paths and limitations. Its `receipt_artifact` identifies the immutable payload before this self-ID is added; `replay-receipt.json` is the returned payload. Repeating a channel in independent Stores reproduces its fixture/sequence identities; runtime engine timestamps, absolute paths and the final receipt identity may differ.

- F02: disjoint ownership masks, parented translation with a declared anchor, explicit held position tracks, manual destination goldens including hidden RGB, a one-based expected-color pixel edit, overlap/frozen-reference/stale-color negative controls, portable editable import and exact original scene rerender. Three frames at10fps retain the last duplicate hold. This recipe uses unit scale and zero rotation, so it does not independently distinguish anchor-dependent rotation/scale behavior.
- F09: eight-frame64×64 body marker at12fps, pinned shipped renderer arc against retained case60 full-RGBA hashes, explicit body/back/front shared-clock composition, a fine edit after composition, unknown-family rejection and fresh Store composition replay. Body-only and effects-on exports/review pages stay separate. The retained hash oracle is adapter parity evidence, not private model identity or independent artistic approval.
- F10: explicit16×16 marker sequence with70/130/50ms holds, duplicate final pixels, pivots and two total plays; exact PNG/sheet/APNG, bounded GIF, portable import, ordered-pair review, unrepresentable hold/partial-alpha rejection and overwrite preservation. APNG/PNG retain hidden RGB; GIF checks visible RGBA and alpha separately.

F10 runs available Godot headlessly for one-shot, two-play and infinite-loop variants: actual SpriteFrames load/save/reload, rectangles/full-RGBA texture hashes, unequal weights, real AnimatedSprite2D ordering, completion counts, loop return, final hold/pivot and restart. Resource loading precedes100ms plus three process frames of warmup; the measured scene starts afterward. Wall-clock checks have a declared40ms tolerance (per cycle for completion); rational manifest timing and resource weights remain exact authorities. The cause of the initial recorded lead was not separately isolated. This is warm-start headless evidence, not cold-start guarantees, GPU pixel capture, continuous visual review or gameplay acceptance.

Godot absence yields an explicitly unsupported engine record, a false engine-verification check and `status='partial'`. File creation never counts as engine verification. Other failed checks still make the receipt failed, including when the engine is unavailable. Engine nonzero exit, timeout or missing receipt is failed, not skipped. Node is required for F09; its absence/rejection raises the existing local capability error, never synthesizing an effect result.

Each channel writes exact artifacts and review HTML but does not assert that the animation was watched. No provider, credentials, generation, live REA, hidden-surface inference or private vendor method is used. Private/full-vendor and artwork/motion quality remain unsupported/unreviewed. The batch CLI/callable channels are sufficient to repeat these diagnostics and inspect receipts; they do not supply an interactive part/rig/pose/pixel editor or a frozen artistic/model comparison protocol.

Selected test transcripts, the original startup timing failure and corrected engine receipts are retained under `tests/evidence/replay-geometry/`. The failed startup run was not retrospectively relabeled a pass or repaired by widening tolerance.
