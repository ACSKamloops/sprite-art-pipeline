# Rejected painted cutout route

An AI-generated sixteen-part master provides fixed clothing pixels. Two-bone IK articulates those parts in one side-view walk, without per-frame redrawing. It improves material identity but still has weak arms, rigid torso weight, joint seams and incomplete directional anatomy. This is preserved as a rejected experiment.

`generation-receipt.json` binds prompt, reference and master. `candidate-v3` and `candidate-v4` retain exact builders, authoritative48-frame manifests and separate reconstructed `source/parts` receipts. `reproduction.json` proves all96 RGBA frames reproduce from their corresponding source builders and immutable master. Reconstructed source archives restore the historical receipts after the original shared `parts/` was overwritten by the later build; the old manifests are unchanged.

Do not invoke the legacy `build.py` against this folder: it is an archived experiment which writes shared parts before refusing an existing candidate. Copy its master/builder to an isolated fresh temporary folder for reproduction. New production pipelines must create versioned parts and refuse an existing output before any mutation.

No full four-view, game-contact or artistic approval follows from fixed pixel identity.
