# Installed v0.6 handoff preparation proof

**Passed** for frozen runtime/source commit `f82b2f47a756e5b9d77263b991baf71a4c0c5af0`, fingerprint `bf8bd9c55ea0fdde471d57706b123bc94018f766b5d0c3d2e30cbeab94b1befc`. [Receipt](RECEIPT.json), [isolated result](RESULT.json), [commands](COMMANDS.json), [source inventory](SOURCE.json), [wheel inventory](WHEEL-FILES.json) and [installed files](INSTALLED-FILES.json) retain the exact reproduction inputs and identities.

Wheel: `/home/astra/artifacts/pixellab-model-handoff-v06-20261014-proof-final/wheel/sprite_workbench-0.6.0-py3-none-any.whl`, 778,103 bytes, SHA-256 `a8aff74e3819a551fa1441270786f3079b49964c96e1efa7fd2bbc946b75068f`.

All 105 runtime files matched source, wheel and isolated installation byte for byte, including `model_handoff.py`, `web/model-lab.js` and every current HTML/CSS/JavaScript asset. The wheel has 110 entries. All 97 earlier runtime paths remain present; the 46 original factory slices and their manifest are unchanged. A fresh Python 3.14 virtual environment outside the checkouts used the existing hash-pinned dependency lock and cached build tooling. Its runtime script ran with `-I` and imported the installed package, not a checkout.

The installed API proof exercised:

- one frozen edit brief with exact whitespace-preserving user prompt and two ordered supplied reference rasters;
- two held executor tasks sharing the same brief and prompt draft, with native pixels encoded losslessly into complete exported packet folders;
- explicit `supplied-diagnostic` ingestion of one native 5×4 RGBA marker, retaining original PNG bytes, hidden RGB and partial alpha, without resize or cleanup;
- both orchestrator and image-backend pair audits remaining ineligible, with `quality_score: null` and no artistic acceptance;
- editable exports for both diagnostic results, imported into separate fresh Stores with every exported artifact byte equal, including result/task/brief, original image bytes and both input PNGs;
- installed HTTP index/app/style/source-VFX/model-lab assets matching packaged bytes, exact model catalog dispatch, absent `local.models.execute`, and the comparison gate remaining closed.

[Packets](PACKETS.json), [frozen brief](FROZEN-BRIEF.json), [held tasks](HELD-TASKS.json), [diagnostic results](SUPPLIED-DIAGNOSTIC-RESULTS.json), [pair audits](PAIR-AUDITS.json), [portable closure](PORTABLE-CLOSURE.json) and [HTTP receipts](HTTP-MODEL-LAB.json) are retained. The native marker and complete packet/export directories remain under the artifact root above.

This proves local handoff preparation, raw admission and portable closure. **No generated art, model/agent/provider calls, authentication requests, credential reads or Hermes invocations occurred.** The model catalog correctly describes Hermes/MiniMax as the orchestrator with a proposed, unselected and untested image plugin. It does not claim an actual available image generator, recovered private PixelLab inference or visual quality.

A preliminary proof for `89827e5` completed before the final image-vendor casefold fix. Its [dated receipt](PRIOR-89827e5-RECEIPT.json) and artifact folder `/home/astra/artifacts/pixellab-model-handoff-v06-20261014-proof` remain preserved. The final proof above supersedes it. Earlier v0.5 proofs under `docs/source-faithful` remain dated evidence and were not overwritten.

Reproduce with an absent artifact folder from the frozen checkout:

```bash
/home/astra/projects/pixellab-local-workbench/.venv/bin/python \
  docs/provider-preparation/package/PACKAGE-proof.py \
  --output /home/astra/artifacts/pixellab-model-handoff-v06-REPRODUCTION-UNIQUE
```

The build refuses an existing output directory or dirty runtime. It checks the requested package version and all source/wheel/installed runtime hashes. The scripts are proof infrastructure only; they do not provide a generation executor or run the broad test suite.
