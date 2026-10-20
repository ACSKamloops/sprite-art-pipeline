Current successful comparison route: [model-walk-audition](../model-walk-audition/README.md). The AI pose sheets and painted-part rig below remain rejected; the new rigged-model walk has separate current source-bound reviews.

# Visual quality correction

The previous Copper Scout contour rig is rejected as sprite artwork and animation. Passing pixel/resource/contact checks did not make its drawings, directions or movement convincing. The user rejection supersedes current visual acceptance; earlier receipts remain unchanged as history.

Open [the local comparison](http://127.0.0.1:8144/pilot/visual-quality-reset/) and press Play. It shows the rejected rig beside an **unapproved** eight-pose right-facing art experiment. This experiment improves shading, clothing masses and pose silhouettes, but it is also rejected as a usable animation. It is not a replacement four-direction pack.

`generation-receipt.json` binds both built-in image generation calls, complete prompts and ordered references. `authored-walk-v1` retains the initial 32-pose sheet: richer artwork, but repeated stride silhouettes. Its explicit eight-pose guide provided composition inputs for `guided-walk-v2`. The latter contains the actual master, source-cell inspection, fixed-canvas nearest exports and raw GIF. There is no per-frame fitting or automatic anchor repair.

Two independent reviewers identify blocking defects: a 5–6 native-pixel ground shift between halves, unequal compression rhythms, changing boot/coat/scarf masses, and similar arm configurations where the gait role pair should reverse. The guide distinguishes those role pairs; which anatomical limb is wrong requires explicit near/far tagging rather than guesswork. The drawing improvement is recognized separately from the failed animation.

Reviews are under `../../qc/temporal/guided-walk-v2-static-review`, `../../qc/temporal/guided-walk-v2-timed-rejection`, and `../rigged-character/qc/art-direction/guided-walk-v2-review.json`. Actual local Chromium captured every paused pose and twelve chronological playback samples at `/home/astra/artifacts/copper-scout-quality-audition-v1`. Capture clock ranges bracket screenshots rather than pretending asynchronous screenshots establish exact ticks. Root viewed the full-canvas 2× chronological sheet; no continuous video ingestion is claimed.

The corrected authoring requirement is an editable, coherent character turnaround and carefully authored contact/down/passing/up keys. Use shared painted parts and view-specific replacements, or an actual textured model, to preserve anatomy/material ownership. Let an explicit rig/pose source control motion; repair joint and perspective poses deliberately. Do not repeatedly ask an image model to redraw entire sprites and assume the identities will stay fixed. An explicit sheet-layout offset may isolate registration errors, but cannot fix anatomy or role mistakes. No other directions or broad action library should be expanded until the representative cycle satisfies the visual benchmark in real playback.

The companion skill's `references/visual-quality-gates.md` records the tightened art criteria and these demonstrated failures. Mechanical validation, independent visual approval and user acceptance stay separate.
