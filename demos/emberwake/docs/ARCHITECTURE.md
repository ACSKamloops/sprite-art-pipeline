# Game structure

`scenes/main.tscn` hosts the hand-authored valley and quest in `scripts/main.gd`. `actors` is a y-sorted **pausable** branch. The root, camera, HUD and quiet ambient layer remain active for menus. Projectiles/effects live under actors, so pause/dialogue freezes their real movement, lifetime and pending releases. A modal pauses the actor without cancelling an in-flight cast.

`hero.gd` owns collision, facing, action state, input buffering, invulnerability, cooldowns, mana and actual damage/release times. Rendering uses the same selected state with variable manifest holds. Firebolt and frost reuse the body casting animation and spawn separate effect/projectile tracks. Hits query live enemies and check walls; fast projectiles use swept segments. Basic strikes use facing rather than mouse-position aiming. Healing is requested by the hero but authorized by the world, which owns the two flask charges.

`enemy.gd` owns scout/brute/Warden behavior. Windups telegraph the actual attack space. The boss alternates a sweep, pulse and projectile fan and changes phase below55% health. Enemy art chooses front/back, step, windup or release; art does not drive collision or invent hit windows. Renderer/resource lookups use `ResourceLoader` before raw-file fallbacks, because exported PNG/WAV sources are remapped into PCK resources.

Nearby foes separate using elliptical visual space around their physics feet. Normal AI reserves one nearby attack commitment through windup, strike and the first0.2s of recovery; others still approach and make room. Reservations are derived from living actors, with waiting-time arbitration, so interruption/death releases a commitment without a persistent global queue. Direct forced attack calls remain available to isolated engine tests. Small whole-cel anticipation/contact/recovery offsets stage the existing painted keys; they do not create a new limb-animation rig. Hollow whiff cues differ from successful painted damage bursts, and projectile hits avoid spawning a duplicate damage effect.

`hud.gd` draws a fixed960×540 logical interface, scaled by Godot's canvas stretch. Controls and map are the journal; dialogue and menus have focusable buttons. The play-mode Journal button deliberately has **no keyboard focus**: otherwise Godot's `ui_accept` Space also opens the journal during a dodge. Real input-dispatch regression tests cover this failure.

`main.gd` owns three ward encounters, quest gates, final boss, pickups, checkpoint/rest, save/continue, retry, ending and epilogue. Normal play has no progression cheats. Test harnesses directly exercise setup/teardown in a separate test save. `browser_diagnostics.gd` publishes a **read-only** `window.emberwakeState` snapshot for local automated input testing; it grants no control or bypass.

`user://emberwake-save.json` stores validated versioned progress, checkpoint and audio preferences. Saves deliberately resume at a rest/checkpoint with renewed resources, rather than serializing every projectile and enemy frame. Current unkindled fights reset on retry/continue; kindled wards and completed quest state persist. New journey uses an explicit overwrite choice.

## Verification

-280 behavior/resource assertions: combat costs and damage, line of sight and high-speed projectile collision, death/retry, all24 hero bindings, quest flow and ending, valid/invalid save handling, actual pause clocks, real key/GUI dispatch, canopy and epilogue regressions, HUD overlap, live group spacing and bounded attack commitments.
-378 physical route samples along the authored routes, excluding intentional ward/gate contacts.
-Actual imported-resource PCK verification and real WebGL browser play; independent reports bind the actual PCK hash. A passing SceneTree test does not establish perceptual smoothness or controller feel.
-The test runner rejects script/runtime errors and insufficient receipts even if Godot exits zero. Audio is given a short teardown grace so engine mixer references are released before test exit.

The project targets desktop keyboard/mouse play. No mobile touch controls, party system, inventory/equipment progression or commercial-length content is claimed. The game uses original raster art, real-time combat and an original compact quest; it does not emulate Chrono Trigger's battle engine. Browser CDP evidence separately confirms audio context resume and an advancing render clock after a real click; no auditory quality judgment is implied.
