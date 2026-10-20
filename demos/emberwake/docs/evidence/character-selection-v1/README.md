# Character selection UI and save contract

The title now shows the selected emberkeeper's actual south-idle cel. **Choose emberkeeper** opens a keyboard/click gallery with three cards per page, selected-card focus, Back/Esc cancellation and an explicit apply button. New journeys use this choice; Continue always restores the saved character. Existing overwrite confirmation remains intact.

The paused field journal offers **Change emberkeeper** only while idle/walking in a quiet clearing. A living foe within 430 world pixels, a committed action/death or an in-flight combat projectile blocks it. Applying a character keeps the tree paused and preserves health, mana, location and quest state; it saves the changed appearance with the current checkpoint. This is an appearance choice, not a class/stat change.

The catalog is `res://assets/characters/catalog.json`, schema `emberwake-characters/v1`, with `{id,name,subtitle,description,atlas,manifest}` entries. Rowan remains available if the catalog is absent or invalid. Runtime art loads through `hero.set_character(id) -> bool`; the UI preserves the live character and save if that load fails. Saved `character_id` is optional in existing version-one saves. Missing, malformed or retired IDs normalize to Rowan without discarding valid journey progress.

Browser diagnostics remain read-only and expose pending title selection separately from the live character, gallery draft/count and normal UI controls' labels, action IDs, rectangles, focus and disabled state. They do not apply choices or bypass safety rules.

## Verification

`RESULTS.json` and the five logs record 176 passing engine assertions: 40 new selection/save/input checks plus 56 world, 26 pause, 20 input/closure and 34 save/HUD regressions. Real input dispatch checks mouse card/apply clicks, Tab focus, Enter selection and Esc cancellation, including the viewport stretch transform. The existing Journal `FOCUS_NONE` dodge fix is retained. Runs use isolated `XDG_DATA_HOME` directories and the test save, never the normal player save.

The 40-check selection case deliberately injects three metadata entries reusing Rowan's atlas and a minimal character-setter contract stub. This verifies UI/persistence integration independently while new production art and the real hero setter are prepared in other worktrees. **It does not establish that Lyra/Brann art exists, their animation quality, or successful real-hero atlas switching.** Those need the integrated build and real catalog.

The same 40 checks passed in a rendered Xvfb/Mesa Compatibility run. The two fixture screenshots under this worktree's ignored `output/character-ui/` were viewed to check layout; paths/hashes are in the report. Their repeated Rowan artwork is intentionally labelled as a fixture. No exported-browser test or character-art score is claimed here.

Re-run:

```bash
XDG_DATA_HOME=/ABSOLUTE/ISOLATED/TEST/DATA LP_NUM_THREADS=4 OMP_NUM_THREADS=4 \
  godot --headless --path "$PWD" --script tests/character_selection.gd -- --test-mode
# Optional normal renderer/captures (same fixture scope):
XDG_DATA_HOME=/ABSOLUTE/ISOLATED/TEST/DATA LP_NUM_THREADS=4 OMP_NUM_THREADS=4 \
  xvfb-run -a godot --path "$PWD" --script tests/character_selection.gd \
  -- --test-mode --capture-character-ui
```

After merging the real characters and hero setter, verify catalog discovery with no fixture injection, title/new/Continue and safe pause swaps for each actual ID, actual atlas resources in the exported PCK, and every direction/action's separate visual review. The gallery subtitle is intended as one short line and description as two short lines at the 960×540 logical viewport.
