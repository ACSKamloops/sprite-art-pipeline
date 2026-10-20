# Character expansion and spell repair

This expansion keeps Rowan and adds two original unarmed emberkeepers: silver-haired, teal-clad Lyra and bronze-armoured Brann. Selection changes appearance and voice-free presentation, not stats, costs, damage or encounter balance. Each character has south/east/north/west idle, walk, strike, cast, hurt and dodge bindings. Diagonal movement selects one cardinal view; no diagonal art, weapon rig, jump set or new death-collapse is claimed.

## Generation and reconstruction

Actual art creation uses built-in OpenAI ImageGen, not Google Imagen, H3, a local generative model or a 3D character. `art-source/characters-v2/` retains literal prompts, raw returns, input roles, pose-only diagrams, per-request receipts and selected/rejected bakes. Eight initial direction calls use the existing hero only as pose/layout/style authority; Lyra/Brann identity comes from their separate south appearance banks. The returned sheets are 1774×887, not the requested 2048×1024. One declared whole-sheet nearest conversion produces the eight-column/four-row extraction grid.

`scripts/bake_characters.py --output /ABSOLUTE/FRESH/OUTPUT` requires a nonexistent destination. It supplies fixed view/row registration, 128px stages, pivot `[64,112]`, draw scale 0.66 and 24 explicit timed clips per character. It consumes saved paint and makes no provider calls. Scale/origins are authored for these sheets; do not copy them onto unrelated art or fit each frame by its silhouette.

Brann's original west sheet crosses its nominal row boundaries and is rejected. His selected west bank mirrors the valid east paint with a one-native-pixel x correction. This is disclosed reuse of a symmetric unarmed design; an asymmetric outfit/weapon would require new west paint. Lyra has separately generated cardinal banks.

The full front/back walk regeneration experiment still repeated extended-contact poses and remains unselected. Focused four-cell leg edits supplied compact passing paint. The selected compositor restores every original RGBA pixel outside `[42,83,91,123)`, including transparency; mirrored lower-leg reuse is explicit. It rebases leg paint from the request's phases 2/6 onto existing phases 3/7 at the actual half-cycle boundaries, leaving the existing heads, bodies and arms intact. This is a measured compositor decision, not a claim that the generator preserved them. Brann's contradictory north step is removed through an explicit repeated valid cel; repeated exposure is not another drawing. Eight holds still total 0.45s.

`art-source/tab-repair-v1/` supplies the bounded same-view donor pixel plan for Brann's changing waist tab. Donor and target cel hashes reject upstream changes. Literal per-row masks, source maps and journals preserve everything outside the authorised feature. The first side-donor draft is retained as rejected. These are raster repairs, not a hidden cloth rig. Additional candidate changes and review scopes remain versioned rather than overwriting earlier evidence.

`art-source/gait-bridge-v1/` retains source-coordinate maps for eight intermediate leg cels per character. Only south/north walk phase selections change. Boot plateaus, support regions and upper bodies are explicitly protected; integer maps are authoritative instead of floating triangulation ties. The independent review found the flagged small alpha spaces read as interleg openings rather than punctured anatomy. Hole counts alone do not establish either result.

`art-source/tab-repair-v2/` closes the two remaining exposed south-dodge cloth remnants while preserving the crossing glove. `art-source/attack-settle-v1/` retains four new guard-to-idle settle drawings per character. Attack keeps its first 0.305 seconds, authored 0.16-second hit and total 0.41 seconds. Dodge keeps its 0.26-second duration. Separate dodge-only head layers and bounded torso/boot refinements are retained with their own source witnesses; `selected-refinements.json` specifies exactly which clips may select each appended cel. Old cels remain stored. Selected version and scores are frozen separately in the final quality record.

The baker's `--stage base` reproduces the frozen v4 intermediate. `--stage gait` isolates the frozen source-map stage. The default also applies hash-bound selected follow-ups. Temporary helper source/package paths are rebound to hash-identical project-relative authorities, so scratch-directory names do not change selected manifest bytes. Reproduction checks compare actual fresh files, not merely these declared source hashes.

Runtime consumes `assets/characters/catalog.json`, schema `emberwake-characters/v1`; each entry points to its atlas, custom `emberwake-animation/v1` manifest and optional portrait. The catalog includes original Rowan paths. The custom manifests are not the generic sprite-pipeline schema without an adapter.

## Selection, saves and input

The title's **Choose emberkeeper** gallery uses actual selected sprite pixels. Click, Tab, Enter, Back and Esc work. Title choices apply to a new journey; **Continue restores the saved character**. New-journey overwrite confirmation remains required when a valid save exists. Existing version-one saves without a character ID fall back to Rowan.

The paused journal can change character in a quiet clearing. The swap preserves health, mana, location, cooldowns and progress and writes the selected ID into the checkpoint save. Committed actions, nearby living foes and in-flight projectiles block switching. A failed art load retains the working hero. This avoids using appearance selection to heal, refill or cancel an attack.

## Frost and casting hands

Frost previously used `z_index=-1`, placing the entire painted ice/ring below opaque ground. It now remains at zero in the actor branch's y sorting. It is visible above the floor while foreground actors retain depth. The existing nova radius, damage, slow, costs, cooldown and 0.24s release are unchanged. The blue field is an area effect, not a directional projectile.

Each character manifest declares four native `cast_hand` points on release index 3. `get_cast_hand_global()` maps `(hand-pivot)*draw_scale` into the world. The visible firebolt core/paint and its release flash use this position. Its physics position still starts on the foot plane and follows a swept segment: a glove that projects beyond a thin wall cannot bypass that wall. Visual trajectory/impact placement is distinct from ground-plane collision and actor-owned damage feedback. Physics and paint share the selected release phase; pending and released effects remain pausable.

See `docs/evidence/spells-v2/README.md` for socket coordinates, the reproduced invisible-frost negative control and render receipts. New-character coordinates are in their current manifests; Rowan defaults remain available for old assets. A numeric socket comparison alone cannot establish that the selected texel is the actual painted palm, so enlarged plain/release captures are reviewed too.

## Evidence boundaries

The integrated suite passes 400 assertions plus 378 route samples: 280 baseline, 40 selector-fixture checks and 80 production spell/catalog checks. The selector fixture deliberately uses a stub and repeated Rowan artwork, so it is not production-character proof. The integrated real renderer separately passes 109 spell/catalog/socket/visibility/collision/pause assertions across the actual three banks. The native render fixture includes old frost invisibility, corrected pixels, foreground depth and all 12 release hands.

`tests/browser_characters_v2.js` drives only real menu clicks/keys and reads diagnostics. It uses `test_mode=false`, a separate browser profile/origin, no teleportation, injected saves or invulnerability. It checks new journeys, both characters' four facings/strikes/fireballs, frost resource use, dodge, safe swaps with invariant health/mana/location and reload/Continue. Asynchronous screenshots can arrive after a state sample and do not certify an exact release frame. The native frozen-release fixture supplies the precise origin check.

Frozen initial character reviews are retained under `/home/astra/artifacts/emberwake-character-review/v1/`; subsequent versions have separate folders. They inspect all clips, predecessor/successor poses, wraps and idle joins. Chronology inspection is distinct from uninterrupted human motion perception. Mechanical checks and the old demo's overall rating do not transfer to the new characters. Current selection and final review evidence are recorded in `docs/QUALITY.md` and `DELIVERY-INDEX.json` after the expansion is frozen.
