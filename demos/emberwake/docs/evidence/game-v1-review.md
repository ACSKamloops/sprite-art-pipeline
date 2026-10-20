# Independent browser game review — Emberwake v1

Reviewed 2026-10-15 Pacific / 2026-10-16 UTC. This is an independent play review of the small prototype, with no prior producer reports or scores opened. The source project was not edited. All evidence is in this directory.

**Verdict: 6.0/10 as a small playable prototype, with moderate confidence.** There is a complete, coherent adventure loop and a readable opening, not merely a technical scene. The main defensive control has a reproducible menu conflict, combat can disappear under trees, and the encounter presentation and quest closure need work. This is not a polished game-quality 9/10.

## Build and method

- URL: `http://127.0.0.1:8896/`; fresh Playwright CLI session `emberwake-review`, fresh browser context/profile, no reload during the entire run.
- Start PCK SHA-256: `c1310fa00e5028c38a7f20f2df8e52e713bdc83165fbe93d3ad7e1114f9eaada`, 11,326,640 bytes. Start receipt: `build-start.json`. End receipt: `build-end.json`.
- Chromium 1243 executable, headless, SwiftShader software GL, 1280×720 browser viewport / 960×540 game viewport, device scale 1. See `cli.config.json` and `browser-console.log`.
- Gameplay used real browser keyboard and mouse events. `window.emberwakeState` was read to inspect position, foes, health, progression, animation states and frame chronology. No teleports, health changes, test mode, save edits, debug invulnerability or progression manipulation were used; `test_mode=false` throughout.
- Some navigation and action sequences were timed programmatically, with pauses between sequences to inspect screenshots. Thus this was actual input-driven browser play, but not a human experiencing uninterrupted real-time animation. I cannot certify normal-speed perceptual smoothness, input feel on a user's GPU, sound quality, or a natural first-player completion time.
- No audio was heard in this review. Effects and music buttons changed their displayed on/off states and were restored, but that is not auditory validation.

## Exact coverage

Played the title and controls/map, both introduction texts, Aster's four opening pages, Moss fight and kindle, Tide fight and kindle, Crown fight and kindle, shrine Warden, bell interaction and ending, continued free roaming, returned to Aster for both post-ending pages, and saved/continued the completed game.

Verified death and lantern retry in the first encounter, a Tide retry after the menu/input problem, and a boss retry. Wards survived death. The first death occurred while I left the character standing during screenshot inspection; it is not evidence that the first fight is unfair. The boss's close-combat death also includes my deliberately stationary attacks and poor facing after knockback, so it is not a player difficulty benchmark.

The successful boss attempt used firebolts and two healing flasks, without Space because of the defect below. The successful ending had `won=true`, `boss_defeated=true`, all three wards true, no foes, and normal mode. `ending-state.log` binds the result; `completion-continue.log` confirms saved completion survived the title/Continue flow.

Input coverage included WASD, opening arrow movement, J and left mouse strike, K and right mouse firebolt, Q and L nova, H heal, E/Enter interaction, Esc pause, and attempted Space dodge. Save/Continue was tested within the same loaded page. Browser reload, browser restart persistence, new-journey overwrite confirmation, all alternate routes, every collision edge, other viewport sizes and devices were not tested.

## Findings

| Priority | Finding and observed consequence | Evidence |
|---|---|---|
| High | **Space reopens the journal after journal use.** Repro: pause with Esc → resume with Esc → press Space. State changes from play to pause; the initial isolated attempt had hero state `dodge` and dodge cooldown ~0.817, so the same press both initiated dodge and paused. Subsequent combat keys did nothing until resumed. Right mouse was initially suspected, but a second repro omitted it and still failed. This breaks an advertised combat control and interrupted the Tide fight. | `input-space-repro.log`, `21-input-isolation.png`, `22-space-only-repro.png`. The latter log explicitly records play → pause after Space. |
| High | **Dense canopy can completely hide the hero and enemies while combat continues.** Walking north from Aster into the Moss approach puts the hero beneath tree artwork rather than keeping the moving character legible. The Moss fight was possible while the hero was absent from the visible scene; visible diamonds and UI carried more information than the character. This also makes walkable terrain ambiguous. | `07-village-north.png` (hero at CSS ~590,315 partially hidden); `12-moss-combat.png` (hero world ~425,1023, expected screen center, completely covered by trees). |
| Medium | **Boss HP panel overlaps the objective panel.** At 1280×720, boss HP panel ~x376–904,y86–134 intersects objective panel ~x855–1248,y27–130. The word “Warden.” is visibly behind/through the HP panel. The initial toast also runs across the boss's upper body while combat is live. | `32-boss-intro.png`, `36-boss-ranged.png`, `37-boss-phase-two.png`. |
| Medium | **Post-ending objective does not acknowledge the completed return conversation.** Aster's two post-ending pages end in a welcome home, but after closing them the HUD still says “The bell is singing. Return to Aster.” Saving and continuing retains that request. | `42-aster-return.png`, `43-aster-return-two.png`, `44-return-objective.png`, `completion-continue.log`. |
| Low–medium | **Compass label is stale after ending.** Its arrow appears to point toward Aster, including downward beside the village NPC and southwest from the shrine, but the text remains “BELL.” This contradicts the “Return to Aster” objective and the apparent arrow target. | `44-return-objective.png`, `45-completed-continue.png`, `47-nova-render.png`; label at CSS ~1207,243. |
| Low | **The shrine floor has a conspicuous rectangular cut edge.** The broad tan arena meets grass in straight vertical and horizontal lines, unlike the softer forest paths. This gives the encounter a placed-patch look. | `31-shrine-approach.png`, `32-boss-intro.png`, `45-completed-continue.png`; e.g. `31` floor left edge ~x476, bottom edge ~y240. |
| Low | **The final named Bell is visually an altar with a blue flame and no visible bronze bell.** The interaction text explicitly refers to touching old bronze and the bell, and the title art shows a hanging bell, but the in-game focal asset communicates a magical shrine. This weakens the final narrative payoff rather than blocking play. | `01-title.png` compared with `39-bell-interact.png`, shrine CSS ~575–909,y0–320. |

## Presentation and game judgments

The title composition, forest palette, buildings, rocks and ward stones belong to a recognisable fantasy world. The hero is easy to distinguish on open ground, though the brighter character style is a little cleaner and more cartoon-like than the dark enemies. The village lantern looks like a flat gold dot on a stick beside much richer scenery (`05-village-approach.png`). Repeated tree and rock placement is visible but acceptable for this prototype's scope.

The opening text is short and useful. The nearby interaction prompt, persistent objective, field journal, region labels, and tiny map make the intended loop understandable. Aster explains facing/actions, telegraphs, healing and checkpoints. The three ward fights grow from scouts to groups with brutes, then lead to a boss. The loop is coherent but mainly repeats move → defeat a cluster → press E → refill. I did not encounter choices, inventory, equipment progression, side quests or NPC systems; the demonstrated experience is closer to a compact action adventure than a developed RPG.

Hero movement, attack and cast clips did change at runtime, rather than being only static state names. `input-and-animation-samples.log` records left-click attack frames 7→9→11 and L cast frames 13→14→15; directional movement, hurt and dodge states also appeared during the run. This verifies some render chronology, not smoothness. Enemy screenshots largely retain the same posed silhouettes across approaches and attacks in this v1; the pale geometric telegraphs and positional changes do much of the combat communication. I do not claim frame-by-frame continuous enemy-animation perception from these samples.

On open paths, amber arcs and rings can be seen (`19-tide-contact.png`, `26-crown-route.png`, `36-boss-ranged.png`). In groups they overlap, and their pale thin lines compete with bright tan ground and tree detail. Tiny enemy health bars are difficult to read at a glance (`23-tide-fight-3.png`). Knockback, enemy HP changes and clear-state messages give useful feedback. Facing matters: repeated east-facing strikes left the scout behind the hero alive until a nova; repeated boss strikes outside reach did no damage. Those are observed mechanics, not automatically defects. The missing reliable dodge sharply reduces fairness confidence in this build.

## Scores, separately judged

These are subjective prototype scores, not an average of engine checks or a certification of a finished game. Confidence reflects this sampled-browser method.

| Dimension | Score /10 | Confidence | Basis |
|---|---:|---|---|
| Art cohesion | 7.0 | Moderate | Consistent forest mood and readable UI; weaker character/enemy match, placeholder-like lantern, hard arena edge and Bell/altar mismatch. |
| Animation / feel | 5.0 | Low–moderate | Hero clips have actual changing frames and distinct action states. Sampled enemy posing, coarse combat presentation and software rendering limit the impression; no continuous human or audio judgment. |
| Navigation / onboarding | 6.5 | Moderate–high | Good first objective, prompts, usable map and clear ward instructions. Canopy ambiguity and stale completion guidance reduce clarity. |
| Combat readability / fairness | 5.0 | Moderate | Distinct tools, facing, costs, telegraphs and recoverable checkpoints. Dodge/menu conflict and obstructed/overlapping threats are substantial. Boss was beatable with resource-managed ranged attacks. |
| Robustness | 6.5 | Moderate | Full normal progression, ending, retry, state preservation and same-page Continue worked. Main control conflict and quest closure errors remain. Limited routes/devices/storage scenarios tested. |
| Overall small prototype / game quality | **6.0** | Moderate | A complete coherent mini-adventure that needs another quality pass before describing it as polished. |

## Runtime observations and limits

Runtime-reported FPS samples ranged approximately **21–42** across menu, movement and combat captures. A separate safe, unpaused shrine idle sample advanced 202 rendered frames in 5.0293 seconds: **40.16 rendered FPS** (`performance-and-settings.log`). This is headless SwiftShader on a shared environment; it must not be presented as GPU performance, a controlled benchmark, or the user's expected frame rate. Different capture points and shared load varied materially.

The browser console contained three informational engine/renderer messages, zero warnings and zero errors at collection time (`browser-console.log`). That does not negate the gameplay defects. The game advertised 10–15 minutes, but this timed-input and state-assisted review cannot validate a natural player completion duration. The first ending occurred at runtime elapsed ~136.74 seconds; pauses, reading and tool time were excluded by the game, and timed navigation substantially changes how that should be interpreted.

No project files or saves were changed through filesystem/debug operations. Only the game's own interaction flows wrote its browser save. Any later build fixes require separate verification; none are counted as fixed in this v1 report.
