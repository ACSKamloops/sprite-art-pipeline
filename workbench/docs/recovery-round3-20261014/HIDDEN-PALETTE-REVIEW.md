# Hidden-only black: exact frame predictions, failed raw palette strips

Two adaptive follow-ups preserve the frozen constructor's exact frame predictions while **falsifying its raw palette-strip prediction**. Across all six calls, ignore-alpha construction predicts12,288 RGBA entries without disagreement, but the raw palette order/membership matches only **4/6 calls**. The fifth requests3 colors and reports2; the sixth requests2 and reports1. Those failures must remain visible.

[Machine audit](HIDDEN-PALETTE-REVIEW.json) contains both independent receipts, source/phase pins, per-policy counters and REA IDs. Artifacts are under `/home/astra/artifacts/pixellab-palette-round3-20261014/hidden-followup-audit`. The earlier [four-call audit](FROZEN-PREDICTION-REVIEW.md) remains separate; its success is not retroactively extended to these raw strips. This reviewer made no provider, network or credential calls and modified no original captures.

## Freeze, byte binding and replay

Both calls were adapted after earlier observations, then frozen before their own POST. They reuse earlier warm/green RGBs and, between these two calls, **exactly the same source PNG bytes**. They are not independent new-color holdouts.

| Follow-up | Source commit | Phase SHA | Result |
|---|---|---|---|
| Hidden black, K3 | `9d5e17d87246fad4e95a7fa641e61ce5ad1dc7c1` | `5fbb7df9e4a9c8dc90976df5018e7ebbfa84a167dd320ecd23c47f4511cbad90` | HTTP200;0.1 reported generations |
| Same inputs, K2 | `36ec93fd9ad1842e22efe1c2ddb1ab2e9c356cc3` | `02d1edba4e8cb6fe6c9b0b87ef7151c1d4b77a507405c37b4235d2d226d8ad09` | HTTP200;0.1 reported generations |

The exact archived preparer, unchanged generic constructor SHA `15bfb938f4050a3a35362cebc9633ec4288ae1b1a08cbf85216bdf3510d93807` and inferred mapper SHA `6272a72903dd4a7d330e7eeb5c8e7df321cbc84c6ba9f9485404a640857ba742` replay every frozen palette and predicted frame. K2's mapper pin is inherited through its hash-bound previous K3 plan. All prediction receipt/PNG/RGBA hashes, source inputs, requests and compact wire hashes match. Recorded preparation times precede producer starts; local pins/timestamps are not external notarization.

Independent final-verifier runs under Python `-O` bind each call's complete producer/REA record and3 returned PNGs, with no failures. REA decodes the retained producer HAR; it does not independently witness the live request or identify vendor code.

## Actual outcomes

Each case contains1024 fully transparent black pixels and1024 visible warm/green pixels across two frames. The calibrated mapper's alpha arrays are preserved exactly.

| Case | Frozen ignore-alpha raw palette | Actual returned strip | Ignore-policy frame errors |
|---|---|---|---:|
| K3 | Black + `[219,174,87]` + `[44,151,85]` | Warm + green only; `n_colors=2` | 0/2048 RGBA |
| K2 | Black + `[165,167,87]` | Merged visible color only; `n_colors=1` | 0/2048 RGBA |

Frozen predicted frame PNG bytes equal actual bytes in both cases. The two competing alpha-exclusion policies are identical on this binary-alpha source. They fail **832 pixels/frame for K3**, including320 visible errors, and **1024/frame for K2**, including512 visible errors. Thus the results are associated with hidden black affecting the available visible-color budget; simply excluding transparent pixels from the tested construction does not fit.

The returned strips equal the observed visible RGB unions, omitting hidden-only black. For K3, filtering the prediction to visible colors is a **post-hoc relationship**, not a frozen success. For K2, root explicitly added a visible-only presentation competitor to its new hash-frozen prediction receipt **before that call**. The audit independently reconstructs that strip from local predicted outputs without an observed palette and confirms its one-entry prediction exactly. This adaptive presentation success does not erase either raw-strip failure.

## Returned strip is insufficient for full RGBA replay here

Applying the previously calibrated quarter-lightness Oklab mapper using only each **actual returned strip** gives zero visible-pixel errors, but fails **512 transparent pixels in each frame** for both calls. It remaps hidden black to a visible palette color, whereas the returned PNG keeps transparent black. Therefore a returned strip cannot universally be treated as the complete latent mapping palette for full RGBA reconstruction. The earlier four cases' returned-palette agreement remains a finite success, not a general guarantee.

A pipeline that clusters all RGB, maps through a larger latent palette, then emits only visible palette entries is consistent with these results. No internal stage, order or implementation is recovered. Alternative algorithms could produce the same finite outputs. Nonblack hidden RGB, other alpha layouts, one-color/empty-visible cases, general clustering, automatic size detection and animation use remain outside these two fixtures. The older32-center counterexample also remains unresolved.

[Audit script](../../scripts/recovery_round3/audit_hidden_palette_predictions.py) replays only archived source and local evidence. Early incomplete audit artifacts are preserved separately; only completed `K3-final/AUDIT.json` and `K2-final/AUDIT.json` are cited. Counts are6 calls/0.6 reported generations for this round's prediction probes, with repeated source colors, AB/BA and reused follow-up images; they are not six independent algorithm validations.
