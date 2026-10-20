# Combat readability pass

Input evidence: `/home/astra/projects/emberwake-review/game-v2/07-scout-strike.png` and `19-crown-combat.png`, viewed before editing. Those show overlapping enemy bodies and multiple large warning sectors. This pass changes presentation and local group behavior without editing painted assets, damage, reach, hit times, obstacle checks, spell costs, or actor pause boundaries.

- An approaching enemy applies elliptical local separation to account for painted bodies rising above their physical feet. Waiting foes move toward a useful striking distance and separate, rather than orbiting along a prescribed route.
- A nearby actor's windup, strike, phase transition and first 0.20 seconds of recovery reserve a commitment against the same target. Older eligible waiting foes have priority; distance breaks near ties. Reservations derive from current actors and states, so interruption, death, deactivation and disabled/dead targets release them without a global queue. Direct `_start_attack()` remains a forceable helper; ordinary AI goes through arbitration.
- Existing anticipation, contact and neutral paintings get small explicit whole-cel staging offsets. Contact pose returns to neutral earlier during recovery. These offsets do not constitute new authored limb animation. Missing rear-bank keys still fall back to valid rear neutral, so separately validated new paintings can load through the existing bank loader.
- Enemy melee release traces the exact locked floor sector for 0.16 seconds. Missed or invulnerability-rejected contact gets a small hollow tick. Accepted damage retains the actor's painted impact. A projectile no longer adds a duplicate large impact over the victim's own burst. No hitstop or extra damage-active frames were added.
- `take_damage()` on hero and enemy returns whether damage was accepted; existing callers may continue ignoring it. Read-only enemy diagnostics expose commitment count, wait time, reservation state and last strike outcome.

## Reproduction and boundaries

Run `python3 tests/run_checks.py`. The new `combat_readability.gd` case has 30 assertions for actual physics spacing, repeated group pressure, all-actor participation in the real Crown kind/position mix, one live commitment, interruption/death release, independent targets, locked aim, exact single damage release, missed-hit cues, recovery art, actual pause/resume and duplicate projectile impacts. It does not grade game feel or art.

The crowded three-scout fixture starts with a 23.80-pixel minimum elliptical visual gap, reaches 50.75 pixels after 3 seconds, and produces 11 commitments over 10 seconds with a maximum of one reservation. The Crown mix produces 10 commitments, all five foes participate, maximum one reservation, final minimum visual gap 59.98 pixels. These are reproducible stationary invulnerable-target fixtures, not a difficulty benchmark.

Optional native visual fixture:

```bash
LP_NUM_THREADS=4 OMP_NUM_THREADS=4 xvfb-run -a godot --path . --script tests/capture_combat.gd -- --test-mode
```

It writes four screenshots under `output/combat-polish/` and prints state chronology to standard output. This deliberately moves an invulnerable hero to the Crown approach and lets the real encounter AI run for six seconds. Screenshots 1 and 2 were visually inspected: four active bodies stand apart around the hero, with one main warning, rather than the earlier stack. A fifth scout remains behind the ward because its real line of sight is obstructed. The fixture's objective remains the introduction objective because it bypasses the journey. It is not ordinary-player, independent-review or smoothness evidence.

Remaining limits: few authored enemy action keys; some body overlap may remain at narrow physical obstacles or during moving-player collisions. New pose paintings integrated separately need their own art and transition review. Human combat feel and the revised encounter balance require fresh actual-key play review on the exported build. No numeric quality rating is asserted by this pass.
