# Original website VFX controls

`source_controls.py` calls `source_vfx.run_source_vfx('apply_controls', ...)`, which executes the retained, unchanged factory `47381`: export `W$` (`G`) normalizes and validates; export `uY` (`en`) applies controls. No local expression evaluator, bind resolver, slider mapping, rounding, control validation or substitute craft algorithm is added.

The retained source is `website-art-bundles/create-vfx-be26fa3e471fd274.js`, SHA-256 `11a1ee402e10ddec3ebb1d558a3e699d7b06a605846b4ddc36f346c9aa7b9065`. Exact UTF-8 byte ranges and selected hashes in retained `analysis-root/workbench-gap-closure/CLIENT-SOURCE-CLAIM-LEDGER.json`, claim S05:

| Original symbol | Bytes [start,end) | SHA-256 |
| --- | --- | --- |
| P, JSON copy | 42560..42594 | `3f2ee11070f5c92d37d1c188c0262df2480c4a4ff826f5180c66a7ec3510ed67` |
| V, existing bind target | 73717..75941 | `12fec4d1c179a466a1938f821f0cce26fa8e9b2e381acaa185c627f10c8328f0` |
| Q, applied target validation | 76413..77006 | `efcb55bf6c884e31ce9b7e51f75d2c2c83f7a12ccc1b34c619393d1759a84991` |
| ee, mapping | 77006..77749 | `10e46bdfeae27079d5ef317eb7fd4e370f4d4575b5b1dcf5bc9d0ceef154dca1` |
| en, applyControls | 77814..78120 | `c5ab3dd792fa0505f9c1dba34cfaf7e9a275e303cc33f983642421d1f08751e2` |

The vendor manifest binds the complete original factory, including `G` and its endpoint validation; the runner verifies factory identities. This is the retained website implementation, without an asserted MCP/server implementation binding.

## UI integration contract

`describe_controls(recipe)` returns source-normalized declarations. A UI can render `slider`, `toggle`, `select`, and `ramp` types using the declared label/help/value, numeric min/max/step, and options. No controls are invented for recipes without controls.

`apply_controls(recipe, values={id: value})` assigns only declared control values on an isolated JSON copy, calls original normalization then original applyControls, and returns:

- `controls`: normalized declarations, including normalized binds and values;
- `declared_recipe`: raw recipe with assigned control values;
- `normalized_recipe`: original `W$` output before control application;
- `recipe`: original `uY` applied result, for inspection;
- `renderer_input`: the raw declared recipe, ready for the original renderer;
- `hashes`: SHA-256 of canonical JSON input, declared, normalized and applied recipes, normalized control declarations and all effective ID/value pairs.

The source renderer itself calls normalization and applyControls. Rendering the applied preview would apply mul/add a second time. Re-inputting normalized output also fails for source-generated `rng: null`. `render_controlled_effect` therefore renders `renderer_input` and persists a content-addressed control receipt with all returned data and hashes. It returns the ordinary renderer response plus `control_receipt`, `control_hashes`, `controls`, and `controlled_recipe`.

Original source performs `value*scale+offset`; set replaces a scalar, and mul/add transform existing scalar, pair and supported animation forms. Integer scalar/pair mapping uses `floor(v+0.5)`. Original normalization rejects overlapping targets and validates slider endpoints and selected values. Our only additional ID policy is rejecting values keyed by unknown controls; wrapper JSON/resource budgets are local policies.

## Executed diagnostic coverage

`python -m pytest tests/test_source_controls.py -q`: **13 passed**. `tests/test_source_controls.py` exercises scalar mapping, from/to, keys, expressions, waves, integer pairs, nested key targets, original rejections and successful single-application render equivalence. Rejection checks compare the complete caller recipe before and after the exception. This establishes isolation through this adapter; it does not assert arbitrary original runtime or server transaction atomicity. Recipes are retained diagnostic fixtures or small explicit boundary cases, with no provider/model, paid generation or character-art calls.
