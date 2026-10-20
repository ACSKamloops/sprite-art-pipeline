# Eight-direction systems evidence

Systems scope: `scripts/hero.gd` and `tests/eight_directions.gd`. The projectile and combat-effect implementation already accepts normalized diagonal vectors and keeps physical foot-plane travel separate from rendered hand projection, so those files did not need changes. No production artwork or catalog was changed here.

Later followup: the actual provisional candidate-v2 banks passed 1,163 production resource assertions, 272 rendered assertions with 24 release pairs and 192 ordinary-browser assertions (one incomplete asynchronous projectile sample). See [candidate-v2/README.md](candidate-v2/README.md) for hashes and qualification. The original results below remain the pre-integration legacy/synthetic receipts; final motion/art acceptance is separate.

## Runtime contract

- `directions` is optional. Missing means the legacy `south,east,north,west` bank. An explicit declaration must be that list or `south,southeast,east,northeast,north,northwest,west,southwest` in that order.
- Eight-view banks select the nearest of eight combat sectors, starting at south. Analog movement retains its continuous direction and magnitude. Keyboard diagonals remain normalized. Zero aim retains the last useful aim. Legacy four-view banks retain their previous cardinal presentation and free-angle combat vector.
- The existing punch/cast/recovery lock, pending hit, dodge cancellation, pause boundary and gameplay clocks remain in charge: melee release `.16`, spell release `.24`, attack `.41`, cast `.50`, dodge `.26` seconds.
- Facing changes within walking or idle preserve normalized loop phase. Entering a different action resets its clock. Art authors must align corresponding directional gait roles.
- Selection validates the entire bank before changing any live character fields. Every declared view needs all six actions; each clip needs nonempty integral in-range frame indices, matching finite positive holds and an explicit Boolean loop flag. Idle/walk loop; attack/cast/hurt/dodge do not. Positive holds are played literally, including durations shorter than 15 ms.
- Every declared view needs a finite, in-cell `cast_hand` point. Omitted legacy sockets use the existing four-view defaults. `cast_release_index` can be an integral scalar or a complete per-view dictionary; every index must select a valid cast frame. Missing scalar defaults to the existing index 3.
- Atlas columns, cell, pivot and scale come from the manifest. No eight-column atlas assumption is introduced.

## Executed checks

Godot `4.7.2.stable.official.ed1daf0bf` on this assigned Linux worktree:

- The new mechanics fixture passes **161 assertions**. `fixture-checks.json` and `eight_directions.gd.log` contain the result.
- The original nine cases pass **400 assertions**, plus **378 route samples**. `RESULTS.json` and the per-case logs record those runs. The spells case was run from a temporary copy with its report folder alone redirected into `baseline-spells/`, preserving earlier evidence; its assertions and gameplay were unchanged.
- `--production` was intentionally exercised before new art integration. It rejects all three current manifests for lacking an explicit eight-view declaration. `production-preintegration-checks.json` and `production-preintegration-expected-failure.log` record those three expected failures. This is evidence that production mode does not silently accept the synthetic fixture or legacy banks.

The default fixture writes clearly named `SYNTHETIC-*` files under a worktree-specific `user://eight-direction-logic-fixture-*` folder. It checks actual W+D input, sector centers/boundaries/zero, equal diagonal/cardinal travel, walk-turn phase, committed and buffered action facing, late recovery, one-time hits, diagonal cone exclusions, melee/projectile/dodge wall collision, swept high-speed diagonal impact, pause/resume, real legacy save restoration and atomic rejection during a pending cast. The fixture is not production hero art.

The first expanded fixture run sampled after recovery had already ended because independent physics timers accumulated an extra tick. Its six assertion failures are retained in `fixture-first-expanded-run-failed.log`. The fixture was corrected to sample against the actor's remaining action clock; the clean run passes. Earlier setup probes also corrected a typed local, flushed synthetic key events and used the actual `village` checkpoint name. No claim relies on those erroneous probes.

## Root integration checks still required

After integrating the actual banks and importing their textures:

```bash
godot --headless --path . --script tests/eight_directions.gd -- --test-mode --production
python3 tests/run_checks.py
```

Production mode requires all three real banks to declare eight views. It samples every actual action frame through the runtime region selector, then checks each of the 24 declared hand sockets, release cels and foot-plane/visual-offset projectile launches. The receipt includes actual manifest/atlas hashes, columns and cell dimensions. This is a resource/behavior check: rendered hand-to-glove alignment, full motion playback, appearance quality and the user's requested art/motion rating require separate actual-art review and browser/gameplay evidence.
