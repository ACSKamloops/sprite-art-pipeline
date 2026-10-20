# Independent real-browser QA

Observed 2026-10-14 UTC against `http://127.0.0.1:8876/#studio` in a separate Chromium context. The served Studio JavaScript exactly matched canonical source at HEAD `85ed4e3e3675c6b0a0ca35a075cb7d70d1d4fe66`; its hash and retained artifact hashes are recorded in INDEPENDENT-BROWSER-PROOF.json. No runtime source was edited.

Five scoped checks passed:

1. A locally constructed 8×8 PNG with hidden RGB `[33,55,77,0]` uploaded through the actual file input. Import without normalization was rejected visibly, leaving the checkbox unchecked and no editable preview.
2. Checking explicit normalization and importing succeeded. The retained raw identity remained the uploaded source, and the receipt declared one changed hidden-RGB pixel. Independent decoded HTTP readback matched the uploaded PNG exactly; the editable result differed only by zeroing RGB beneath alpha zero.
3. A locally constructed two-frame APNG uploaded/imported through the UI. Raw and working sequence holds both remained exactly `1/7` and `2/9` seconds with one play. The normalization receipt declared two changed hidden-RGB pixels.
4. Open fine editor, choose Erase, and perform an actual pointer click on opaque pixel `(2,2)`. The immutable project/history IDs changed, Studio adopted those new IDs, and its actual canvas pixel readback showed alpha zero. The raw source sequence document stayed identical.
5. Set viewport to 390×844 on the edited own-asset Studio. Document and body widths were exactly 390; no visible Studio element extended beyond the viewport. The retained full-page screenshot was inspected.

There were **zero page errors** and **one expected console error**: the browser’s resource400 message for the deliberately rejected non-opt-in import. This is not a zero-console-error claim. These five checks are separate from root’s primary browser flow and do not duplicate or increase its reported eighteen checks.

Evidence directory: `/home/astra/artifacts/pixellab-reliable-acceptance-20261014/browser-independent/output/playwright/`. It contains the standalone Playwright-core replay (`qa.cjs`), BROWSER-RESULT.json, initial/final DOM text, trace.zip, diagnostic source PNG/APNG, raw/editable readbacks, and normalization-required/desktop-edited/mobile390 screenshots. The declared Playwright core and cached Chromium paths were used without installing packages.

This covers real local browser transport, input actions, decoding and UI behavior. It does not certify sprite art, broader game readiness, provider generation, GPU Godot rendering, or wheel installation. No provider or credential calls were made. The test created only diagnostic local artifacts and immutable supplied-art server records.
