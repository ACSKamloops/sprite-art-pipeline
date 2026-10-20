# Browser controls and supplied-art verification

The local interface is an operational surface for the implemented methods and
precise artwork refinement. Choose a local method and its parameters, execute
it, inspect its retained result, edit supplied pixels/palettes/timing, and repeat
with immutable history or a saved plan. Captured vendor methods remain visible
and unavailable until a local implementation exists.

Actual Playwright Chromium interaction exercised project upload/open, unlocked
layer selection, one pixel stroke, undo, redo, authoritative rendering, plan
save, job submission and completion, catalog selection, local method invocation,
vendor method refusal, and asynchronous setup verification. These actions used
the supplied 8×4, three-frame diagnostic. They did not create or assess original
character art.

The first browser pass found an empty Methods list despite 245 returned
descriptors. The client read inherited `Array.entries` as a wrapper field.
The [retained failure](evidence/browser/method-diagnostic.log) is preserved;
`846e391` corrected array handling. The repeated browser action successfully
invoked `local.library.list` and showed the captured generation contract with
its invocation button disabled. Setup completion now refreshes automatically,
with a disabled submit button while the job is active and bounded polling.

A 390-pixel layout initially overflowed by 12 pixels. `ca74489` corrected the
navigation minimum width; the [final observation](evidence/browser/mobile-fixed-dom.log)
records document and viewport widths of 390. This stylesheet-only change follows
the method/edit/job browser actions at `846e391`. Final setup was repeated on
`488b696` after refreshing the packaged catalog's coverage-document hashes.
That refresh changed no runtime code, UI assets, catalog identities or statuses.
The separately installed package proves the final packaged bytes.

[Ten artifact checks](evidence/browser/BROWSER-PROOF.json) passed. They bind the
actual browser observations to the local Store: pixel `(4,1)` changed from index
0 to 1 in `marker-a`; shared-cel frames `first` and `third` changed and `second`
remained unchanged; exact history and rendered raster hashes survived undo/redo;
the saved plan completed as a real pipeline job; grammar, transport and interface
rows were exposed;
setup matches the final runtime fingerprint and comparisons remain blocked.
The browser console recorded zero errors and warnings on the corrected session.
The checker validates retained observations and artifacts; it does not replay
the interactive actions.

The assistant visually inspected the desktop readiness, grammar, jobs, methods,
editor and narrow readiness screenshots. Readable controls and the diagnostic
canvas are confirmed. The animation preview selects supplied frames using their
recorded clock; remote image decode/preload and continuous motion quality have
not been established by these screenshots. No humanoid quality rating, private
handler parity, animation-generation ability or original-art comparison is
claimed.

| View | Evidence |
|---|---|
| Readiness | [Desktop](evidence/browser/readiness-final.png), [390 px](evidence/browser/readiness-mobile.png) |
| Editable diagnostic | [Editor](evidence/browser/editor-final.png) |
| Recovered primitive fields | [Grammar](evidence/browser/grammar.png) |
| Actual saved plan job | [Jobs](evidence/browser/jobs.png) |
| Explicit local request/response | [Methods](evidence/browser/methods.png) |

Retained setup is [SETUP-VERIFICATION.json](evidence/browser/SETUP-VERIFICATION.json).
Installed delivery is covered separately by [PACKAGE-PROOF.md](PACKAGE-PROOF.md).
No provider credentials, account requests or generation credits were used.

Recheck the retained observations against this Store while its server is running:

```bash
.venv/bin/python docs/readiness/BROWSER-check.py \
  --browser-output output/playwright \
  --store workspaces/web-control/store \
  --output docs/readiness/evidence/browser --runtime-commit 488b696
```

The project/plan hashes are content-addressed diagnostic evidence. New interactive
actions should receive a new retained observation folder and explicit review;
do not relabel these small fixtures as a production art test.
