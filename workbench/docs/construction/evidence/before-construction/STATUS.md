# Local replication status

The operational local channel stage is verified for the declared supplied-art and deterministic diagnostic subsets. **Full PixelLab replication and the requested high-quality humanoid animation are not complete.** There is no defensible single “100%” figure covering those different requirements.

Use [LOCAL-CHANNELS.md](LOCAL-CHANNELS.md) to operate the tools. [LATEST-VERIFICATION.json](../LATEST-VERIFICATION.json) binds the tested commit, environment, wheel and retained runs. The canonical installed command is `/home/astra/projects/pixellab-local-workbench/.venv/bin/sprite-workbench`.

| Requirement | Verified result | Boundary |
|---|---|---|
| Repeatable environment | Dedicated Python3.14 venv, hashed dependency lock, setup script and dependency probes | Node and Godot are explicit host dependencies; no self-contained binary claim |
| Runnable recipes | All11 local recipes completed137 checks total per replay, in both checkout and installed package | Frozen diagnostic subsets, not complete original F01–F11 suites |
| Local AI control | Persistent JSON Lines channel with jobs, cancellation, revision guards, candidate review/selection and library operations | Trusted local process, cooperative cancellation; not an HTTP/MCP server or sandbox |
| Own supplied artwork | Import/edit/plan/crop/paste/export/review CLI, Python APIs and complete channel caller example | Missing poses, surfaces, directions and generated art require actual supplied/created assets |
| Repeatability | All11 primary sequences, declared recipe inputs and package source hashes matched between fresh executions | State UUIDs/timestamps and measured engine wall time may differ |
| Mechanical regression |214tests passed,0failures/errors/skips; declared example completed at `da13c69c4bb640bf35ba899306aa705855adce29` | Test counts do not certify all vendor semantics or art quality |
| Artifact preservation | File manifests verified before and after pair comparison; full RGBA/clock/registration comparison | Manifest integrity does not authenticate a replaced manifest or supply aesthetic judgment |
| Review | Independent completeness, channel adversarial and geometry cross-reviews; reproduced defects corrected | Each review retains its selected scope; no exhaustive all-input correctness guarantee |

The supplied comparison reports raw RGBA changes, hidden/visible RGB domains, alpha, bounded visible palette counts, frame order/count, pivots, directions, rational holds and play count. It exports the original canvases without aligning/resizing away differences. An unsupported float-clock preview remains explicit and has no dead player link. Generation and artist ratings are not inferred from these measurements.

Current replay evidence and local viewer:

- [Checkout replay](/home/astra/projects/pixellab-local-workbench/runs/local-replication-20261012-release-replay/index.html)
- [Installed-package replay](/home/astra/artifacts/pixellab-replication-package-proof-20261012/replay-release/index.html)
- [Independent run comparison](evidence/pair/PAIR-VERIFICATION.json)
- [Package identity and77source-file comparison](evidence/PACKAGE.json)
- [Tracked verification receipts](evidence/verification/REPORT.json)

Review findings and corrections:

- [Completeness audit](COMPLETENESS-AUDIT.md): identified absent operational routes and defined the bounded stage.
- [Channel red team](review/REVIEW.md): preserved actual failures for an overflowing wait, malformed manifest and unsupported-preview links; the corrected9control suite passed. Normal wait timeouts now have their own status.
- [Geometry cross-review](GEOMETRY-CROSS-REVIEW.md): corrected an ambiguous unknown-family negative, qualified translation-only anchor coverage and bound output/order corrections. [Resolution](GEOMETRY-CROSS-REVIEW-RESOLUTION.json).
- The original failed Godot timing receipt remains in `tests/evidence/replay-geometry/`. Final checks use a documented warm start and unchanged40ms tolerance; the cause of the initial lead was not isolated. Headless timing is not continuous visual review.

Remaining work is substantive: private model/checkpoint/training/temporal internals, a chosen working generative backend, full native editor/indexed history/host behavior, browser Worker/GPU/CSP and videoPTS coverage, broader tile/map/glyph/runtime suites, and accepted humanoid directional parts/action/contact/animation quality. The original63-obligation ledger and [whole-flow comparison specifications](../WHOLE-FLOW-COMPARISONS.md) remain the broader requirements; eleven runnable recipe IDs do not close them.

For a useful art comparison, the next gate is a frozen input/pose/action/clock/quality specification with approved supplied parts, followed by the appropriate implementation and complete normal-speed body-only/effects-on viewing plus two independent reviews. H3 remains after its earlier prerequisites. No provider calls, credentials, new character generation or external publication occurred in this local channel audit.
