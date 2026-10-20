# Claims, stages and temporal review

Initialize jobs: [{"id":"robot/walk/right/v1","clip_id":"robot/walk_right","source_fingerprint":"...","source_paths":["..."]}]. For existing-art inputs, the validator fingerprint can bind the source manifest/images. For new authoring, hash the frozen brief and reference-file hashes instead: output atlases don't exist yet. Keep this source fingerprint fixed across attempts. The exported asset's input_fingerprint is a separate review snapshot and changes when outputs change. Version job IDs when sources change; init rejects changed payloads.

```sh
python3 scripts/animation_queue.py --db /work/jobs.sqlite init /work/jobs.json
python3 scripts/animation_queue.py --db /work/jobs.sqlite claim-next --owner worker-a --lease-seconds 1800
python3 scripts/animation_queue.py --db /work/jobs.sqlite status
```

Claims return exclusive random tokens and leases. Updates require a live token; heartbeat renews, release hands off, expired claims get fresh tokens. Workers own separate output directories/worktrees. SQLite immediate transactions provide atomic claims; WAL and bounded busy timeout handle processes.

Stages: queued → authored → artifact_validated → engine_tested → visual_review → approved. authored includes decoded poses. advance moves one stage and stores a receipt. Keep errors/rejected attempts, then revise with a concrete reason to reset a leased job to queued and invalidate ownership. Approved jobs aren't reclaimed; create a new version.

```json
{"source_fingerprint":"validator fingerprint",
 "output_hashes":{"../assets/atlas.png":"actual SHA256"},
 "evidence_paths":["artifact-validation.json","engine-test.json"]}
```

Paths are relative to the receipt or absolute. Files/hashes are checked. Receipts record agent evidence; inspect contents and executed commands rather than treating a stage name as proof.

Approval also needs decision=approved, reviewer, observations, review_manifest and review_receipt. The separate visual receipt has input_fingerprint, decision, reviewer, observations and explicit clip_ids. check-review revalidates files and reports unreviewed clips. Queue approval requires this job's clip_id in the current approved receipt. A metric never automatically produces approval.

Review sources/contact sheets at native/game scale, then inspect timed playback and real moving/interrupted gameplay. Check identity, attachments, foot contact, seams, alpha and palettes. Record exact frames and evidence hashes. Geometry, palette changes and upload latency need different repairs. Regenerate and review the new fingerprint; keep rejected exports.

Alpha IoU, centroid/area changes and RGBA differences flag suspicious transitions. Attacks, airborne poses and flashes may legitimately score poorly. Centroid changes don't prove foot sliding; that needs foot landmarks and world-motion information.
