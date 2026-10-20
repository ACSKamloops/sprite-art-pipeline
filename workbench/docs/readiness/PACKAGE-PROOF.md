# Independently installed package proof

The final proof uses frozen runtime commit
`488b69611d6935ca83657d9572243eadd12fa520`, including the corrected capability-array
handling and mobile-width layout in the browser, plus the final regenerated
catalog's current coverage-guide evidence hashes. That last metadata update
changed thirteen repeated COVERAGE SHA references; runtime logic, assets,
inventory identities and status claims stayed unchanged. The reviewer built the
**0.4.0 wheel**, installed its
hash-pinned dependency lock and wheel using `uv` into a new virtual environment,
and ran a `python -I` process outside the source checkouts. No pip module,
provider credentials, PixelLab credits, art generation or model comparison was
used.

The [receipt](PACKAGE-RECEIPT.json), [source manifest](PACKAGE-SOURCE.json),
[installed file manifest](PACKAGE-INSTALLED-FILES.json),
[wheel file manifest](PACKAGE-WHEEL-FILES.json),
[dependency provenance](PACKAGE-REQUIREMENTS.json) and
[bounded command receipts](PACKAGE-COMMANDS.json) retain the exact evidence.

* Wheel: `sprite_workbench-0.4.0-py3-none-any.whl`, **749,884 bytes**, 102 files.
* SHA256: `d04b5f253e4c429ce1d5d25f25c7237ebf11a753a95b44bb5b128490af9fa892`.
* Runtime source fingerprint:
  `c8df6fa354cb0dc584d436dc55cb6115c5f88cbd5670495e8b739fb365463e1d`.
* All **97 runtime files** match source, including HTML, CSS and the fixed JS.
* Workbench imports resolve inside the fresh environment's installed package;
  the process records isolated mode and its external working directory.

The live installed HTTP server successfully served all three browser assets with
exact package/source hashes. It retained the original inventory identities:
**63 requirements, 28 commands, 23 build flows, 30 transport flows, 213 interface
records, 9 documented primitives and 42 recovered grammar claims**. These counts
are inventory coverage, not completed behavior or private algorithm recovery.

Real HTTP setup verification completed all **11 local diagnostic recipes and all
9 required setup checks**, including the host Node/Godot recipe dependencies,
actual LibreSprite resave and decoded re-import, exact undo/redo and portable
native/history data.
[HTTP setup report](PACKAGE-SETUP-REPORT.json) records the successful job.
The wrong-token control request returned **403**, and comparison returned **409**
both before and after successful setup. An additional independent three-edit v2
history export/import passed cold validation in a fresh Store and three exact
undos back to the original project.

[Final readiness](PACKAGE-HTTP-READINESS.json) correctly reports
**`setup_ready: true`, `comparison_ready: false`**, with **71 unresolved blocker
records**. The supplied-data runtime exercise took approximately 10.54 seconds.
It does not open the art/model comparison gate. Native tool binaries remain host
prerequisites; the wheel does not bundle Node, Godot or LibreSprite.

The final retained environment and wheel are at:

```
/home/astra/artifacts/pixellab-readiness-package-proof-20261013-release-catalog/
  venv/bin/python
  wheel/sprite_workbench-0.4.0-py3-none-any.whl
  RECEIPT.json
  runtime/RESULT.json
```

Three earlier siblings remain preserved as historical mechanical proofs:
`pixellab-readiness-package-proof-20261013` covers `cfdca5d` before the Methods
UI fix; `pixellab-readiness-package-proof-20261013-release` covers `846e391`
after that fix but before the mobile layout correction; and
`pixellab-readiness-package-proof-20261013-release-layout` covers `ca74489`
before the final catalog evidence-hash update. None is the final release-catalog
evidence. This installed-package exercise verifies exact delivered assets and
live backend behavior; actual browser interaction and mobile layout are covered
by the separate UI review. It cannot infer functional UI correctness from
matching static bytes alone.

Reproduce from the source checkout with an **absent** output directory:

```bash
.venv/bin/python docs/readiness/PACKAGE-proof.py --output /home/astra/artifacts/pixellab-package-new-proof
```

[PACKAGE-proof.py](PACKAGE-proof.py) builds, installs and records provenance.
[PACKAGE-runtime.py](PACKAGE-runtime.py) is copied outside the checkout and run
with the newly installed interpreter's `-I` flag. Existing proof directories are
rejected, and full workspaces, generated files and dependency blobs remain in
the artifact folder rather than in Git.
