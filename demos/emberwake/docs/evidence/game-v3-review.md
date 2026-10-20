# Independent targeted browser reassessment — Emberwake v3

Reviewed 2026-10-16. **Overall compact-prototype judgment: 8.0/10, moderate confidence.** The changed combat is easier to parse, and the boss HUD obstruction is fixed in actual browser framing. The new Warden rear strike appears in the running game and has a distinct release pose. No blocking issue was found in the targeted paths.

This is a targeted reassessment, not a new full-ending certification. All three ward fights were cleared and kindled; the Warden was observed alive through front/rear attacks and interaction gating. The final state is all wards true, live Warden, `won=false`. The separate frozen v2 packet remains the full ending/epilogue playthrough evidence. No producer assertion count or expert art score contributes to the ratings here.

## Binding and method

- URL: `http://localhost:8896/index.html`; fresh session `emberwake-review-v3`, separate profile and output directory.
- Start/end PCK SHA-256: `2b93baf201f84fea1c64597ad4cb485cc1617e75740148956732fcccd27c7213`, **9,470,752 bytes**. See `build-start.json` and `build-end.json`.
- Same 1280×720 headless Chromium/SwiftShader configuration, 960×540 game viewport, device scale 1.
- Only real keyboard/mouse actions changed gameplay. `window.emberwakeState` was read for positions, HP, animation chronology and progression; no save injection, teleport, debug damage bypass or test-mode change was used. `test_mode=false` throughout.
- Timed input and screenshot/state sampling are not uninterrupted human perception. Animation/feel and fairness scores therefore have lower confidence than the observed control, layout and save results. Sound was not heard or re-instrumented on v3.
- Fresh-profile v3 save/reload was checked. Backward loading the retained v2 save, invalid/corrupt storage and denied writes were not independently tested.

## Actual changed-path results

**Crowd spacing and attack commitments:** Moss, Tide and Crown visibly separate their figures better than the earlier crowded presentation. The larger groups still approach and surround the hero, while fewer simultaneous attack warnings compete for attention. `02-moss-spacing-and-commitment.png`, `06-tide-spacing-4.png`, `06-tide-spacing-11.png` and `10-crown-spacing-4.png` show the resulting scenes.

Across **44 active-play state samples**, the number of foes within 220 world units in `windup` or `strike` was always zero or one: 12 Moss, 16 Tide and 16 Crown samples. The raw sequences and `sample-summary.json` preserve that calculation. This supports the intended arbitration in the sampled encounters; it does not prove every frame, every location, or the exact brief-recovery commitment rule.

All three fights were subsequently cleared with ordinary dodge/reposition, firebolt, nova, facing changes, melee and healing. Long observation sequences deliberately left the hero standing in danger, causing Tide/Crown deaths and retries. Those deaths are not a normal-player balance measurement. The successful Tide retry ended at HP88 without spending either flask; Crown was cleared at HP72 and refilled on kindling. These receipts describe this timed review run, not controlled difficulty comparisons.

**Boss HUD:** The boss bar now occupies the reserved lower row and leaves the Warden's torso visible at the entry camera position (`13-boss-entry-hud.png`). At 1280×720 it spans approximately x409–871,y571–619, separated from the left toast ending around x384 and the action belt beginning around y638. It also clears the Bell interaction prompt at approximately x536–744,y501–550 (`16-rear-position-attempt.png`, `17-warden-back-strike.png`). This fixes the concrete obstruction reported in v2.

**Rear strike and recovery:** A first attempt to get behind the boss did not achieve the intended position; its log is retained and is not counted as rear-pose evidence. A later real dodge reached the north side. `warden-rear-strike-recovery-confirmed.log` then records:

1. `back_windup` at elapsed ~84.050, hero HP100.
2. `back_strike` with state `strike` at ~84.830, hero HP76.
3. `back_neutral` with state `recover` at ~85.168.

The corresponding `17-warden-back-windup.png`, `17-warden-back-strike.png` and `17-warden-back-recovery.png` visibly show different poses. The strike extends the club arm and the recovery lowers it, replacing v2's neutral release fallback. Screenshot latency can advance a pose after its triggering state sample, but these captures do show the new release in the running game. They do not establish smoothness, weight, perfect handedness throughout motion or game-speed animation excellence.

**Hit/miss presentation:** The captures show clear attack rings, changed enemy poses, HP/hurt response on a rear hit, and a small pale ground cue after an evaded front swing (`16-rear-position-attempt.png`, `17-warden-back-strike.png`). I did not perform a frame-exhaustive check of the duplicate-impact removal and do not certify every effect layer from these samples.

**Bell gate:** Pressing E at the Bell while the Warden lived displayed “The Warden still binds the bell. Give the guardian its rest.” Gameplay remained active, `boss_defeated=false`, and `won=false` (`18-bell-with-live-warden.png`, `bell-live-warden-gate.log`). No premature ending occurred.

**Save and dodge:** Normal Moss Save & title → page reload → Continue retained the kindled ward and quest. Following pause/resume, Space remained in play and produced a real dodge state/cooldown and position change (`save-reload-dodge-tide.log`). This validates the ordinary flow, not the internal cache implementation or negative-save behavior.

## Corrected input observation

An H attempt during dangerous Tide sampling did not heal. The initial idea that attack state might reject healing was tested and contradicted: in a safe scene, J produced an attack state with cooldown ~0.343; H then changed HP88→100, mana36→60 and flasks2→1 while the hero was still attacking (`heal-input-and-crown-route.log`). The earlier failed attempt remains timing-limited and is not classified as an attack-lock defect. No independent causal guard test was performed during hurt/dodge.

## Remaining concrete issue and quality limits

**Low-priority visual issue:** dynamic enemy health bars can still cross the hero during close combat. In `10-crown-spacing-4.png`, a bar around CSS x583–665,y333–344 crosses the hero's lower body around x640,y339. This is much smaller than the fixed boss obstruction, but it is a concrete next readability adjustment: keep nearby enemy bars from obscuring the player silhouette.

The next meaningful validation should be uninterrupted human play with sound, focusing on attack anticipation, release, recovery, impact timing and aiming feedback. This sampled browser review cannot certify excellent continuous feel. Distinct phase poses and disciplined attack timing improve communication, but they alone are not proof of fluid motion. The compact adventure also continues to use a repeated clear-and-kindle loop; the changed combat improves that loop without adding demonstrated encounter variety or decision depth. Additional systems are not required to address these presentation limits.

## Updated separate scores

Same compact-demo rubric as earlier packets. Unchanged world/onboarding and broad progression judgments retain their qualified v2 basis; changed combat and HUD were replayed here. No target score was assumed.

| Dimension | V2 | V3 /10 | Confidence | Current basis |
|---|---:|---:|---|---|
| Art cohesion | 8.0 | **8.0** | Moderate | Coherent forest/village art retained, new rear strike fits its character, clean HUD placement. |
| Animation / feel | 6.5 | **7.0** | Low–moderate | Clearer commitments and distinct rear release/recovery improve communication; continuous fluidity, sound and human-perceived weight remain unverified. |
| Navigation / onboarding | 8.0 | **8.0** | Moderate | Prompts, map and canopy behavior remain useful; no full onboarding or epilogue replay was required here. |
| Combat readability / fairness | 7.0 | **7.5** | Moderate | Better separation, one-at-a-time sampled commitments, reliable dodge and readable boss. Dynamic bars and sampled rather than natural play limit the judgment. |
| Robustness | 8.0 | **8.0** | Moderate | Three ward clears, retries, normal reload/Continue, dodge and live-boss Bell gate passed. Corrupt storage/platform breadth and a new v3 ending pass remain outside scope. |
| Overall compact prototype / game quality | 7.5 | **8.0** | Moderate | Targeted changes resolve the major remaining visual obstruction and make group combat more legible. |

## Runtime conditions and cleanup

Before cleanup, runtime FPS samples were roughly 19–31. At 08:00:46 UTC I closed only my inactive v1/v2 QA sessions; the audio QA session was already closed. Later samples reached roughly 34–40. This changed concurrent software-GL load and is **not** a controlled build performance comparison or evidence of an asset-performance gain. No new scientific FPS benchmark was collected.

The v3 console capture had zero errors and one AudioContext autoplay warning. The separate audio-runtime packet verified context resumption on the v2 hash; it is not a new v3 auditory or audio-engine certification.

After session cleanup, prior evidence hashes remained unchanged: v1 82/82, v2 73/73 and audio-runtime 9/9. Logs and `session-cleanup.json` preserve that check. The remaining v3 QA browser is closed after these captures/reporting to free resources; no user browser or unrelated session is touched. Final files are bound by this folder's `SHA256SUMS`.
