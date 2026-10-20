# Additional characters, bounded repairs and spell sockets

Use this when extending an accepted sprite game with selectable identities. The worked case is `/home/astra/projects/emberwake-demo`, branch `codex/character-expansion`; the prior single-character demo is retained at commit `faf4362`. Read the current `docs/CHARACTERS-AND-SPELLS.md`, `docs/QUALITY.md` and `DELIVERY-INDEX.json` for the selected version and exact review scopes. This reference describes methods, not an inherited quality rating.

## Separate identity from motion authority

The original hero's layout/poses can guide a new character without supplying that character's face or costume. The expansion freezes two new identity briefs. Each initial south sheet establishes that identity; the other views receive it as appearance context and the original corresponding view as pose/layout context. Retain all actual input images, role labels, prompts, raw returns and their hashes.

The expansion's initial returns are1774×887, registered once to2048×1024 for an8×4 grid. Requested dimensions are not guaranteed output dimensions. Walk8, strike6, idle2, cast6, hurt2 and dodge4 give28 nonblank base cels per view. Each sheet has fixed measured scale/origin and explicit row corrections; never silently fit each pose by its silhouette. Stage128×128, pivot[64,112] and runtime scale0.66 are this game's contract, not universal defaults.

Reject a sheet whose actual row boundaries cut through limbs. The Brann west sheet failed that test; symmetric unarmed east paint is conditionally mirrored with a declared one-pixel origin correction. The rejected sheet remains in provenance. This does not justify mirroring an asymmetric character.

## Choose the repair layer from the actual defect

Keep raw paint, registered base, candidate repairs and selected runtime bank separate. In this case:

- A full walk redraw continued repeating contact silhouettes. A focused leg edit plus exact restoration of the old upper body supplied useful passing keys. Literal ROI ownership includes transparency to remove old legs. Gait phase and support roles were chosen by the compositor and disclosed separately from the request's intended phase.
- Integer source-coordinate maps add small leg bridges while keeping a boot on a rigid plateau. Freeze the integer map: recomputing floating triangulation at boundary ties can choose different texels. Mechanical replay does not approve the resulting anatomy.
- A waist cloth feature that changed into gold ornament was corrected from same-view cloth donor pixels. Target/donor cel hashes, literal masks, offsets and per-pixel source witnesses make the edit replayable. Preserve hands crossing the cloth and legitimate interleg negative space.
- Attack recovery used four new settle keys and a return to an existing idle pose, preserving the hit time and full action duration. Reusing that settle for dodge is explicit reuse. It still needed separate review: a useful attack settle did not place a crouched head at an intermediate height.
- The dodge-only head repair clears its old literal head owner, then copies translated **nonzero-alpha** head texels. Transparent shifted background preserves underlying body outside the old owner. Copying the whole shifted rectangular background had erased shoulder pixels and was rejected. Keep original attack settles and planted feet unchanged. Check neck seams, old-head ghosts, collar occlusion and every affected direction.
- A settle's brighter neckline was repaired with same-view idle **RGB**, retaining target alpha exactly. Its interior alpha253 made a fullyopaque-only mask a zero-edit operation. Record RGB and alpha ownership separately; do not claim exact RGBA donor copying or credit zero edits.

These are bounded raster components, not a general anatomical rig or recovered hidden anatomy. Cuff/boot texture and volume need visual judgment even when source pixels are exact. Append selected replacement cels and retarget only affected clips, preserving prior alternatives and unrelated timings.

The case's `scripts/bake_characters.py --output <fresh-directory>` reconstructs from saved paint, frozen maps and hash-bound selected refinements. `--stage base` reconstructs the retained earlier base; `--stage gait` isolates source-map changes. It makes no model request. Stable project-relative lineage must replace temporary absolute helper paths before claiming byte-identical manifest replay.

## Keep spell projection and collision distinct

Measure the actual painted release glove separately in all views and characters. In the case manifest, `cast_hand` contains native coordinates and `cast_release_index` names the release exposure. Compute world visual position from `(hand-pivot)*draw_scale` through the actor transform. Match the release art to the gameplay event clock; do not merely shift an old foot-level projectile upward by a guessed constant.

For this top-down ground-plane simulation, physics starts at the actor feet and uses swept collision; the painted projectile has a full x/y visual offset from that physical point. A glove projected beyond a nearby wall must not let the projectile skip collision. Trail and impact presentation use the same visual projection. Actor-owned hit feedback is separate and must not double-decorate a rejected hit.

An invisible frost ring was a depth defect: negative z placed it under opaque terrain. The fix kept it at zero in the existing actor y-sort branch, allowing foreground actors to cover it. Verify actual pixels against the old invisible negative control and a foreground marker, not just a property assertion. A visible effect must still preserve damage, costs, slow, lifetime, pause and release time.

## Character selection and evidence

Validate the complete atlas/manifest before swapping. Unknown identities and invalid resources should leave the working character intact. Keep health, mana, cooldowns, committed actions and progress separate from appearance. The title's new-journey selection and Continue's saved identity have different meanings; test both and older saves without the new field. In-game switching should follow the game's chosen quiet-state rules and preserve stats/location rather than becoming an unintentional heal or action cancel.

Keep three verification layers distinct:

1. A selector fixture may stub the art setter; label it. It proves menu/save logic, not new artwork loading.
2. Production engine tests load every actual catalog bank. Arranged renderer fixtures check exact release hands, frost depth, thin-wall collision and pause. They do not prove ordinary-player difficulty or continuous animation quality.
3. A real Web export needs ordinary mouse/keyboard selection, movement, attacks, spells, swap and reload/Continue. Read-only diagnostics can identify actual clip/frame/state; don't inject saves, teleport or call gameplay setters and call it normal play. Asynchronous screenshots are not exact release samples.

Review the complete requested action/view matrix, changed adjacent pairs, wraps and state joins. Transfer untouched scope only by exact selected RGBA plus timing equality. Keep drawing, consistency, motion, usefulness, confidence and perception limits separate. Repeatedly regrading unchanged art until a desired number appears is not refinement; fix a demonstrated defect, freeze the changed bank and retain earlier lower judgments.

The final frozen example is `art-source/characters-v2/bake-v6/`: Lyra atlas `f177d69482bac4c4a6c1c171e5679e5da1c1c45fa11fbf6b56a0fbf4f5fae901`, Brann `69dd1bf4061ee0f7c740bb6f2f9ec44166f13ca8d651293aa5e23b003d6451f4`. A fresh independent full-bank review rated8.2/8.1; the history-informed follow-up rated7.8/7.6. Both preferred the selected repairs. That is mixed evidence, not unanimous8/10 or per-animation approval. Full reports/ledgers are under the project's `docs/evidence/character-expansion/reviews/`. The actual integrated checks pass400 assertions plus378 routes, a separate109-assertion renderer probe and21 ordinary-input browser assertions with8 cast samples. These numbers are point-in-time evidence for this frozen example, not quality scores or reusable expected counts. Two fresh bakes reproduce all14 selected files, and all13 manual candidate PNGs replay exactly. User normal-speed judgment remains a separate source of evidence.
