# Quality record

The canonical source and local Web export are `/home/astra/projects/emberwake-demo`. The game is a compact, original top-down action adventure. Reviews apply to exact frozen inputs and their stated scope; passing assertions do not assign an art or gameplay rating.

## Frozen history

| Review | Input | Result | Scope |
|---|---|---|---|
| Game v1 | PCK `c1310fa00e5028c38a7f20f2df8e52e713bdc83165fbe93d3ad7e1114f9eaada` | 6.0/10 | Full ordinary-input browser play; identified dodge/menu, canopy, quest closure and presentation failures. |
| Game v2 | PCK `ee0259bb9edc95659880b648c7ee0aad8fc816419bc18a3674c98038f5389a08` | 7.5/10 | Full quest, retries, overwrite confirmation, reload/Continue and epilogue; remaining group overlap, sparse enemy transitions and boss-bar occlusion. |
| Hero v3 | Atlas `1dc65d4eb637ef35e5be3d3345b1a56d18af6ce041f7ce000c924848d569cb68` | 7.7/10 ±0.7 | All 24 declared clips and their joins through decoded chronology; drawing 8.0, consistency 8.0, motion 6.9. Front/back gait stiffness and side-state angle shifts remain. No continuous human-perception claim. |
| Warden rear release | PNG `16d27574bd7c726ef91f3473bd947048988f47a9a8a9f4ab21319e5832fa0f24` | Narrow art acceptance | Same arm/weapon, coherent body/materials and footing, clearer release than prior neutral fallback. Sharp recovery needed runtime checking. Not a whole-game score. |

The prior single-character v3 game is frozen at PCK `2b93baf201f84fea1c64597ad4cb485cc1617e75740148956732fcccd27c7213`. Its independent compact-prototype reassessment is **8.0/10, moderate confidence**. It replayed all three ward fights, normal save/reload/dodge, boss HUD, rear strike/recovery and live-boss Bell gating. V3 intentionally left the Warden alive; v2 supplies the unchanged full ending/epilogue browser evidence. Current native progression tests also pass. The report is `docs/evidence/game-v3-review.md`.

Separate v3 scores remain visible: art8.0, animation/feel7.0, navigation8.0, combat7.5 and robustness8.0. The overall8.0 is a scoped judgment, not an arithmetic test score or a claim that every animation is 8/10. Small enemy HP bars can still cross the hero in close combat; the report records exact screenshot coordinates. Front/back hero gait stiffness and side-state angle shifts remain as documented in the hero review.

## Selectable-character expansion v6

The current local export is PCK `382a06f7aa84d9532b5a4c1f3c901a004128161afabe30cb71a82ac97b8ed2ce` (12,245,640 bytes). It adds Lyra and Brann alongside preserved Rowan. All three have 24 body clips in four cardinal directions. The new selected assets match the frozen v6 review inputs exactly; source/runtime changes are committed at `1dbfb0554151ffed2780ed180c700dd97f17ca64`.

| Independent current-bank judgment | Lyra | Brann | Scope |
|---|---:|---:|---|
| Fresh reviewer, without earlier scores | **8.2/10** | **8.1/10** | All 48 clips, chronological pairs, wraps and terminal state joins; native/2×/0.66 proxy on light/dark. |
| History-informed follow-up reviewer | **7.8/10** | **7.6/10** | All 24 each, exact unchanged transfers and fresh inspection of all affected repairs/joins. |

Both reviewers froze their judgments before seeing the other's findings. Both prefer all 13 selected repairs and found no demonstrated new anatomy, attachment or patch-seam failure. The 8/10 target is met by the fresh review; it is **not unanimous**. Preserve that disagreement rather than averaging it away or claiming every animation is 8/10. Both reconstruct motion from decoded still chronology and known holds; neither certifies uninterrupted human playback or controller feel. Motion scores range 7.0–7.6. Incidental manifest/skill exposure is disclosed separately in each report.

Full frozen packets, copied with their ledgers, are `docs/evidence/character-expansion/reviews/cold-v6/` and `followup-v6/`. Their ledgers verify 46 and 449 files respectively. Earlier v1/v3/v5 lower judgments remain in the neighboring history folders and original external packets. Changed pixels/holds invalidate affected scope.

The new banks preserve all 128 earlier cels and append 13 selected replacements: separate Lyra dodge head layers, Brann's south chest trim and eight passing boots. Gait source maps, cloth repairs and attack settles remain independently reconstructible. No further pixel surgery was supported by the final findings. The remaining useful visual checks concern dodge recovery weight transfer, Brann's south swing-foot clearance at normal speed, north strike readability behind the head and conditional rear-hair contrast on dark ground. Small costume rendering variations remain. None is hidden by a mechanical pass.

Current integrated verification passes **400 assertions plus 378 route collision samples** across nine engine cases. These comprise 280 baseline, 40 selector-fixture checks and 80 production spell/catalog checks. The separately rendered probe passes **109 assertions**, reproducing old frost invisibility and checking visible corrected frost, foreground depth, all 12 release hands, pause and swept collision. The selector fixture alone does not establish actual new artwork loading.

The real non-test browser build separately passes **21 ordinary-input assertions and 8 cast samples**: both new characters' selection/new journeys, four facings/strikes/fireballs, visible frost, dodge, safe swaps, save/title/reload/Continue. No save injection, teleportation or invulnerability override was used. Normal spawn grace remains normal gameplay. Captures are asynchronous; native frozen-release images establish exact origin alignment. The only browser resource error is a retained harmless missing favicon 404. The browser used a separate QA origin/profile, preserving the user's existing local game save.

Two fresh offline bakes reproduce all 14 selected bake files byte for byte, including manifests and receipts, and match runtime atlases/manifests/portraits. All 13 manually refined PNGs also replay exactly. Actual HTTP responses on 8896 match the exported HTML/JS/PCK/WASM. Evidence is in `rebake-verification.json`, `manual-replay.json`, `browser-v6.json`, `live-http-v6.json` and `COVERAGE.json` under `docs/evidence/character-expansion/`.

The expansion did not repeat a full ordinary-input quest ending with each cosmetic identity. The unchanged earlier full-ending evidence and current progression/route tests remain separate. This is a tested compact demo with cosmetic character choice, not a class/party system or a complete modular-equipment/jump/death-animation library.

## Verification boundaries

The prior v3 integrated engine suite passes 280 assertions and 378 physical route samples. Its seven cases cover resources, combat, progression, pause, actual input dispatch, canopy, epilogue, invalid saves/HUD layout and crowd behavior. The fresh-output hero rebake reproduces all five selected hashes exactly. No generation call is required to reconstruct those saved pixels.

The first polish worktree suite encountered Ogg resource shutdown references after a 0.15s teardown grace. Those failed receipts remain under `/home/astra/projects/emberwake-review/world-final-polish/first-suite/`. Affected clean reruns used 0.35s after stopping/releasing music; the final integrated suite is clean. Errors were not suppressed or converted to passes.

Independent browser checks use normal keyboard/mouse actions and read-only observations. Native arranged fixtures deliberately bypass journey setup and sometimes use an invulnerable stationary target; they are named as fixtures and supply no ordinary-player or difficulty evidence. Browser gameplay uses `test_mode=false` and no injected saves, teleportation or invulnerability.

CDP confirms that a real Begin click resumes the browser audio context and that its render clock advances. No reviewer heard the score or assessed auditory quality. Browser reviews use headless SwiftShader on a shared machine, so their FPS samples are not a user's GPU benchmark. Natural first-player timing, human-perceived continuous animation/feel, other physical devices and broad browser/storage-failure certification remain outside this evidence.

The complete review packets live under `/home/astra/projects/emberwake-review/`; frozen report copies and machine receipts are in `docs/evidence/`. The copied `game-v3-packet-SHA256SUMS.txt` applies to the original `game-v3/` packet directory, not to `docs/evidence/`. The installed ImageGen skill has been updated and its 45-file ledger/structure validated, as recorded in `docs/evidence/skill-update-validation.json`.
