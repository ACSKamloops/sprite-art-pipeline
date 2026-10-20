# Final installed0.8.1 Motion QA

Observed2026-10-14UTC at `http://127.0.0.1:8874`. **Main10browser checks and exact postflight passed; the separate actual cached-download→decode→cold-export binding path also passed.** These are new observations from the final rebuilt0.8.1, not replacements for v0.8.0 or intermediate package evidence.

The installed interpreter independently reported version0.8.1 and fingerprint `fb6323b954708942c6b2cca849a9e979c7de118861b10b132d3bb34fe4cbc74b`. Final wheel SHA256 is `344a99661e5cbd89ea89c7a635ecbfef9711a0e621eedbb333287d8dd5e60061`, under `/home/astra/artifacts/pixellab-motion-pipeline-20261014/v081-final/`. Served motion/studio/app JavaScript and CSS exactly matched that installed package. Runtime revision45f261e and suite-record revision7399e7e were supplied by root; this review independently binds installed import/fingerprint, wheel bytes and served web bytes. Details are in `evidence/INSTALLED-V081-UI-QA.json`.

## Main functional replay

A fresh context repeated the retained real-service script: native example decode/video/index26PTS, explicit16pose selection/holds/roles, complete canvas preload/readback, actual0.8second playback, explicit256conditioning, Studio import, fine-editor pointer erase, exact project Undo, export/ZIP readback, offline completed-run Prepare/history resume and390px layout.

All16sample raster IDs exactly matched the chosen native indices, and all16rational holds matched their declarations. Both1/60-second strike poses6/7appeared during this timed run, with all subsequent indices1–15after initial0and no per-hold PNG requests. Native video completed;106callbacks were observed, so all107frames presented is not claimed. The candidate was compatible with normalizationoff and required0hidden-RGB changes. The complete browser ZIP contained390verified inventory files. There were no HTTP/page/console errors or forbidden network/provider attempts.

Additional cold ZIP inspection verified the actual bound packaged extraction, its unchanged parent extraction, and all packaged request/reference/manifest-descriptor bindings. This closes the packaged-source path that the earlier inventory-only v0.8proof did not certify.

## One actual local cached Download

Root authorized one explicit Download for already completed first/last packet `c3db9ed21c0906d42301a59e0dd4bb73805d93fbe6cdc0be056d7e0496e8e580`. Before the action, `download-result.json` and `native-video.mp4` existed. Read-only source review confirmed the installed cached branch validates them and returns before the HTTP download path or authorization branch.

In a separate fresh context, offline Prepare found the succeeded run and kept Submit disabled. One Download button action loaded the existing local result. The UI validated and persisted `{media,native_video,download_receipt}`; browser reload retained those IDs; actual Decode forwarded both producer references and returned an extraction with both source bindings and a parent extraction. Four explicitly authored diagnostic poses were sampled, conditioned to256, imported into Studio, exported and downloaded. These four neutral poses are a provenance test, not an accepted walk cycle or attack.

Independent inspection of this actual cold browser ZIP verified287inventory files and the following chain:

- Bound extraction→native-video/download receipts and unchanged parent extraction→native media.
- Both receipts→the same packet/media; every referenced CAS blob matched its SHA256 ID.
- Packet→exact request-wire bytes, identical to the retained submitted `request.json`.
- Both first/last PNG roles→exact PNG bytes embedded in that wire, with input hashes checked. The two roles deliberately share identical source PNG bytes.
- Native-video record→canonical completion JSON present in the cold ZIP. It semantically equals the retained producer completion JSON; the download receipt separately matches the exact raw completion-file hash and task ID. This is canonical JSON plus a raw-byte pin, not a claim that an arbitrary pretty-printed capture has identical serialization.

All17preexisting producer-run files remained byte-identical, including HAR, poll records, media, completion and paid/download attempt markers. Only the permitted new zero-byte `.provider-operation.lock` advisory lock was added, bringing the file count to18. No permanent attempt marker was removed or rewritten.

Accounting is explicit: **one local cached Download API invocation; zero Submit/Poll invocations; zero new producer HTTP operations.** The last conclusion follows the exercised validated cached-return branch and unchanged producer files, not an independent packet capture. Browser routes physically blocked Submit/Poll, unexpected/repeated Download and external hosts. There were no blocked attempts, page errors or console errors. No provider credentials, new generation or new paid job were used. Disk captures remain producer observations, not independent provider attestation.

## Evidence and boundaries

Fresh external evidence:

- `/home/astra/artifacts/pixellab-motion-ui-installed-20261014/v081-final-run-01/`: main trace, report, screenshots, ZIP, import probe and16frame/hold postflight.
- `/home/astra/artifacts/pixellab-motion-ui-installed-20261014/v081-producer-run-01/`: sealed-packet cached-download replay, before/after file hashes, trace, screenshot and producer-bound ZIP.
- `/home/astra/artifacts/pixellab-motion-ui-installed-20261014/audit-v081-closure.py` and `v081-closure-result.json`: read-only independent ZIP/wire/PNG/completion audit. Their hashes and all evidence-file hashes are recorded in the new proof JSON.

The producer Studio desktop screenshot and main390px screenshot were inspected. Main layout width remained390. All earlier v0.8.0proof and observations remain unchanged. Its pixel/hold/ZIP inventory acceptance did not prove producer provenance closure; this final0.8.1run directly exercises the repaired paths rather than retroactively upgrading that old claim.

No runtime/source changes were made by this QA. Root's full-suite/setup/installed proof counts are separate evidence, not added to these browser checks. Remaining limits: one successful browser scheduler run, tested fixtures/contexts only, no universal arbitrary-video or cross-browser guarantee, no private PixelLab cutout/sampling/deflicker recovery, no ground-contact measurement, and no art/edge/weapon-quality approval. Native sword cropping remains a visible candidate limitation.
