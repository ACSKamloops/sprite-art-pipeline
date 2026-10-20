# Independent browser game review — Emberwake v2

Reviewed 2026-10-16. **Overall: 7.5/10 as the same compact playable-prototype rubric used for v1, with moderate confidence.** The main control and navigation failures from v1 are fixed in actual play. The full adventure, ending and persisted epilogue work. The result is a much more usable, coherent small action adventure; its remaining quality gap is mainly combat presentation, animation transitions and encounter depth.

No producer hero-expert reports or scores were opened. No source or asset files were edited. Reported build claims were retested through browser inputs rather than counted as passes from producer checks.

## Build, environment and boundaries

- URL: `http://127.0.0.1:8896/index.html`.
- Fresh isolated Playwright CLI browser session: `emberwake-review-v2`; separate output directory and browser context from v1.
- PCK SHA-256 at start: `ee0259bb9edc95659880b648c7ee0aad8fc816419bc18a3674c98038f5389a08`, 9,415,028 bytes. Receipts: `build-start.json`, `build-end.json`.
- Chromium executable from `chromium-1243`, headless, SwiftShader software GL, 1280×720 browser viewport, 960×540 game viewport, device scale 1. The v1 review used the same rendering configuration, but the machine's load and browser session mix were not controlled for a performance comparison.
- The server initially refused the connection. It was restored before gameplay; the supplied PCK hash matched. Actual page reloads during the run were deliberate save-persistence tests on this frozen build.
- All game actions used ordinary keyboard and mouse events. Read-only `window.emberwakeState` supplied position, health, foes, animation-state chronology and progression observations. No teleport, save injection, damage bypass, test mode or debug state changes were used. `test_mode=false` throughout.
- Timed input sequences and screenshot/state sampling are not uninterrupted human perception. This review cannot establish normal-speed smoothness, human reaction difficulty, natural completion duration, audio quality or performance on a user's GPU. The scores for animation/feel have lower confidence for that reason.

## Played coverage

Played the introduction and Aster, all three ward fights and kindling dialogues, Warden encounter and retries, actual bell interaction and ending, free roaming back to Aster, both epilogue pages, completed objective, and Continue after an actual reload.

Verified the new-journey confirmation's two paths early in the run: Keep preserved the already-accepted Aster quest; Begin and replace reset elapsed/progression to the introduction and original Aster objective. The confirmation clearly states that the existing checkpoint remains safe until a choice is made (`04-new-journey-confirm.png`, `new-journey-and-canopy.log`).

Moss progress survived Save & title → page reload → Continue (`moss-reload-persistence.log`). The completed epilogue later survived another Save & title → page reload → Continue with `won=true`, `boss_defeated=true`, all wards true, `epilogue_seen=true`, and the completed objective (`epilogue-and-reload-persistence.log`).

Two boss deaths and shrine retries were observed. The first followed idle pose capture and an explicit wait to verify retry. The second included missed shots from poor cardinal alignment and my premature movement toward a boss still at 31 HP. These are not evidence of an unfair difficulty curve. The successful attempt used normal ranged attacks, healing and dodge, with timed button presses. Screenshots and logs from failed attempts are preserved separately from actual success. In particular, `28-boss-shot-attempt.png` and `29-premature-approach-death.png` are not completion evidence; `30-boss-result.png` and `boss-retry-three-two.log` confirm the later real defeat.

Not covered: corrupt-save injection, storage denial, browser-process restart, a second physical device, other resolutions, every collision boundary/route, natural first-time-player timing, or listening to audio. No broad platform certification is implied.

## V1 failure retests

| Earlier issue | V2 observed result | Evidence |
|---|---|---|
| Space both dodged and opened journal after menu use | **Fixed in tested paths.** Space stayed in play, changed hero state to dodge and set its cooldown after Esc resume and after P resume. It also worked repeatedly during Tide, Crown and boss combat. | `dodge-and-new-journey.log`, `03-space-dodge-after-menu.png`, `14-tide-dodge-in-combat.png`, combat logs. |
| Trees hid the hero and nearby foes during Moss combat | **Fixed in the reproduced approach/fight.** Upper canopies faded, leaving trunks readable while the hero and scout cluster remained visible. The roof also faded when the village dodge crossed its occluding upper artwork. | `03-space-dodge-after-menu.png`, `06-canopy-contact.png`, `07-scout-strike.png`. |
| Boss HP panel collided with objective, entry toast covered central combat | **Original collision fixed; another boss-visibility issue remains below.** The objective is unobstructed, and the toast sits on the left. | `23-boss-layout.png`. |
| Aster return objective persisted after finishing the conversation | **Fixed.** Closing page two set `epilogue_seen=true` and changed the objective to “Bellwether is safe. The waking woods are yours to explore.” That state survived reload/Continue. | `35-epilogue-closure.png`, `36-epilogue-reload-persistence.png`, `epilogue-and-reload-persistence.log`. |
| Post-ending compass still labelled BELL | **Fixed in completed epilogue.** Compass disappears after closure; the pre-boss sampled label now reads SHRINE. The travelling Aster label was not separately captured. | `22-rounded-shrine-approach.png`, `35-epilogue-closure.png`, `36-epilogue-reload-persistence.png`. |
| Rectangular arena floor patch | **Visibly improved.** Rounded, feathered edges join the forest paths more naturally. | `22-rounded-shrine-approach.png`, `23-boss-layout.png`. |
| Altar asset did not show the named bronze Bell | **Fixed visually.** An actual hanging bronze bell is visible above the blue flame at the interaction point. | `31-bell-interact.png`. |
| Flat dot-and-stick village lantern | **Visibly improved.** Painted lantern with supports, glow and readable fixture fits the surrounding village. | `02-aster-and-lantern.png`, `35-epilogue-closure.png`. |

## New render and action observations

Scout approach and raised attack silhouettes visibly change across the `07-scout-*.png` captures. `moss-animation-combat.log` records the corresponding step/windup/strike/recover chronology. Pose filenames reflect the state that triggered a capture; screenshot latency can advance the game, so they do not certify an exact pose at every pixel-capture instant. Brute front and back poses were also observed changing through chase, windup and strike during Tide/Crown (`tide-combat-one.log`, `crown-combat-one.log`, `18-crown-contact.png`, `19-crown-combat.png`).

The Warden changed to a clear back windup when the hero moved north of it, then used the neutral back release during its strike state (`24-warden-back_windup.png`, `24-warden-back_neutral.png`, `boss-back-poses.log`). This is more informative than the earlier nearly static presentation, while the release remains a sparse fallback rather than a fully articulated back attack.

East walk sampling observed the art clip cycle across frames 96–103 while world position advanced (`walk-and-tide-route.log`); north/south/west movement and attack/cast/hurt/dodge states also occurred through play. This supports real changing render states, not a claim that every walk frame is clean or continuous motion feels polished. No expert atlas/frame-quality findings were inherited into this score.

The painted firebolt is visibly rendered (`15-firebolt-render.png`). Nova affected mana and combat outcomes, and successful nova use helped clear the scout groups, but my frost captures do not clearly isolate the claimed painted frost artwork. I do not count that specific visual as independently validated. Static screenshot names containing “frost” describe the attempted action capture, not proof that every effect layer is visible.

Thicker inked telegraphs and larger outlined health bars are plainly easier to see on tan paths than v1's thin pale lines (`18-crown-contact.png`, `19-crown-combat.png`, `23-boss-layout.png`). The defensive input now works, so those warnings have a reliable response. Facing and cardinal projectile alignment matter: shots visibly missed when I fired south while the boss was offset east, and landed after alignment on a later retry. I do not treat that aiming mechanic itself as a bug.

## Exact remaining concerns

| Priority | Concern | Evidence and coordinates at 1280×720 |
|---|---|---|
| Medium | **The relocated boss HP panel obscures the Warden's torso at entry.** It no longer hits the objective, but a large portion of the enemy pose is behind UI at the initial camera framing. | `23-boss-layout.png`: panel approximately CSS x376–904,y142–191; Warden approximately x660–820,y55–250. |
| Quality limitation | **Groups still compress into overlapping dark silhouettes and overlapping telegraphs.** The improvements help, but reading which nearby foe is committing an attack remains less immediate than in a polished action game. Larger HP bars do not resolve overlapping bodies. | `07-scout-strike.png`: cluster about x530–680,y180–290; `19-crown-combat.png`: cluster about x455–600,y255–410. |
| Quality limitation | **Animation remains driven by a small set of visibly distinct poses.** The new enemy windups and strikes communicate intent, but this sampled review does not establish fluid transitions, strong weight or excellent human-perceived input feel. The Warden back release is particularly limited. | `24-warden-back_windup.png`, `24-warden-back_neutral.png`; sampled hero/enemy chronology logs. |
| Scope/variety limitation | **The small adventure mainly repeats approach → clear cluster → kindle/refill.** The growing scout/brute groups and Warden provide a complete arc, but there is limited demonstrated encounter variation or player decision depth. This is appropriate prototype scope and is not a request for inventory or additional systems. | Full normal playthrough; three ward/combat logs and ending evidence. |

No new progression blocker was found. Later changes to the health panel or save handling are outside this frozen report and need their own targeted verification.

## Separate scores

Same compact-demo standard as v1; these are judgments, not averages of build/test passes. Confidence is reduced where the review method cannot represent continuous human experience.

| Dimension | V1 | V2 /10 | Confidence | Reason for current judgment |
|---|---:|---:|---|---|
| Art cohesion | 7.0 | **8.0** | Moderate | Strong forest/village mood, better lantern and actual Bell, softened arena edge, matching projectile art. Hero/enemy finish still differs somewhat; body overlap persists. |
| Animation / feel | 5.0 | **6.5** | Low–moderate | Real changing walks/actions and substantially better enemy intent poses. Sparse transitions and sampled software-rendered perception limit the claim. No audio judgment. |
| Navigation / onboarding | 6.5 | **8.0** | Moderate–high | Clear objective, map, prompts and checkpoint teaching; canopy visibility and epilogue closure now work. State-assisted navigation prevents a pure first-time usability claim. |
| Combat readability / fairness | 5.0 | **7.0** | Moderate | Reliable dodge, stronger warnings/bars, distinct tools and usable recovery. Group overlap, sparse attack presentation and boss UI obstruction still hold it back. Difficulty was not measured under natural human play. |
| Robustness | 6.5 | **8.0** | Moderate | Full progression, retries, confirmation, two real reload/Continue checks and persisted epilogue worked. Storage failures, corruption, cross-device/platform behavior and exhaustive routes remain untested. |
| Overall compact prototype / game quality | 6.0 | **7.5** | Moderate | Complete and appreciably improved small adventure; the next gains are combat presentation and feel rather than more engine checks. |

## Runtime and audio qualifications

Runtime FPS samples were approximately **22–42** during this run. A separate safe, unpaused completed-shrine idle sample at world `[1900,570]` advanced 177 rendered frames in 5.0379 seconds: **35.13 rendered FPS** (`performance-idle.log`). V1's separately recorded idle sample was 40.16 FPS. This is not evidence of a controlled regression or improvement: shared load, capture timing and session mix varied, and all rendering used headless software GL. No GPU performance claim is made.

The final document's console capture had **zero errors and one AudioContext autoplay warning** (`browser-console.log`). The warning says audio must resume after a user gesture. Gameplay began through actual clicks, but I did not hear or independently prove resumed playback, so sound quality and audibility remain unverified. The cumulative browser console artifact contains startup messages from the deliberate reloads as well.

The runtime reached the ending at elapsed ~116.34 seconds in the accepted playthrough, with substantial pauses and timed/state-assisted navigation. This cannot substantiate a normal player's completion time; the title now avoids the earlier duration promise. All functional and visual conclusions above are bound to the hash receipts, screenshots, logs and final `SHA256SUMS` in this folder.
