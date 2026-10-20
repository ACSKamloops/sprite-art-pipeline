# Toolchain and execution boundaries

## Offline and provider operations

The saved H3 return decodes into124 frames at24Hz (31/6s), although the request asked for5s. The approved loop explicitly selects source0..29 and preserves1/24s each. `tools/bake_native_sprites.py` implements the audited source-bound recipe; it has no provider client, credentials or network operations. Recipe matte thresholds are appropriate to this blue/brown hero and must be reconsidered for a green costume. It preserves all source RGB even beneath zero alpha.

`providers/minimax_h3/runner.py` and its relative transport/docs are exact copies of the source used for the successful call. Commands `prepare`, `validate` and `status` are offline. A new local preparation was actually run at `providers/minimax_h3/jobs/offline-walk-example`; its request file/wire hashes equal the historical request, with0 submission attempts and no generation gate. It is a historical-walk preparation example, not a new-action job.

```bash
python3 providers/minimax_h3/runner.py validate --run providers/minimax_h3/jobs/offline-walk-example
```

For a new job use a fresh child directory of that runner and action-specific image/video/prompt/provenance. Always specify duration explicitly: the successful case used `--duration 5 --ratio 1:1`; the runner default is4. The provider transport exposes `MiniMax-H3`, one reference image and one reference video in ordered content. It does not expose a seed, first/last-frame controls or control strength. Input body, camera and motion need visual review before a paid submission. The request-hash-bound local gate is an orchestrator record for the authorized one-call scope; it is not a reason to ask again for permission already provided. Submission is one durable attempt, with ambiguous failures retained instead of automatically resubmitted.

Runtime credentials are loaded when needed from MINIMAX_PAYG_KEY/MINIMAX_API_KEY or the existing Hermes loader. No credentials, profiles, auth files or environment files are included here. The optional Hermes fallback remains platform-specific. Provider API behavior may change; the staged source and schema record the actual successful case, not a claim of permanent availability.

Built-in ImageGen remains the alternative for new designs, key poses and bounded semantic edits. That is an agent tool, not Google Imagen and not a claimed local image model. Preserve its native output, prompt/references and masks, then run the same identity/pose/clock/edit/export reviews. No local ML model is part of this workspace.

## Editing and Godot

The bundled toolkit supplies source construction, masks, literal pixel edits, journals/replay, local browser editing and layered exchange. Keep the exact native clock sidecar with LibreSprite output;41/42ms editor holds approximate1/24s. RGB beneath alpha0 can be normalized by editors; compare alpha plus every nonzero-alpha RGBA separately from original file-byte preservation.

The project-delivery helper preserves the selected editable animation and emits a fresh Godot resource-test project. Its checked generic driver covers a limited state set; jump/landing, collision and modular equipment need their own implementation and tests. Existing ER source-bound Godot mechanics/GPU evidence is retained in `evidence/original-engine-receipt.json`, with software-renderer and contact limits stated.

Godot4.7.2 native AnimatedSprite2D variable-hold playback failed on a separately tested short/long hold fixture in the research archive. The tested workaround uses one explicit cumulative phase/world clock. Do not use per-frame delta subtraction that loses a short interval, or assume an importer count pass proves live playback. The approved H3 equal1/24 clock has its own actual engine tests. No engine binary was patched.

## Claim-next work

`tools/animation/scripts/animation_queue.py` provides atomic SQLite claims, exclusive lease tokens, heartbeat, stage receipts, revision and fingerprint-bound approval. The queue does not schedule dependency DAGs: satisfy the neutral/ready dependency before authoring attack/jump, and keep per-worker outputs separate.

```bash
python3 tools/animation/scripts/animation_queue.py --db work/jobs.sqlite init actions/jobs.json
python3 tools/animation/scripts/animation_queue.py --db work/jobs.sqlite claim-next --owner artist-one --lease-seconds 1800
python3 tools/animation/scripts/animation_queue.py --db work/jobs.sqlite status
```

Advance authored→artifact_validated→engine_tested→visual_review→approved only with real source/output/evidence receipts. A lease token is local workflow ownership, not a provider credential. Do not mark planned art as authored or use a renderer's math pass as aesthetic approval. Before changing a frozen brief, version its job ID/fingerprint. Preserve rejected attempts and user-approved walk assets.

The staged job fingerprint is reproducible: build the path→SHA256 `source_hashes` map from `source_paths`; serialize with Python `json.dumps(pins, sort_keys=True, separators=(',', ':'))`; let `base` be that UTF-8 serialization's SHA256 hex. The job `source_fingerprint` is SHA256 of UTF-8 `base + ':' + action`. Current v2 payloads and the active DB match these values. The initial never-claimed draft DB is preserved at `work/history/initial-draft-jobs.sqlite`; it is not the active queue.
