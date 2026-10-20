# Original-source fidelity review

Review base: `46257b3`; independent branch `codex/pixellab-source-fidelity-20261014`.
Research root: `/home/astra/projects/pixellab-local-test-20261011`.
This review covers the retained client procedural renderer and its local adapter.
It does not recover private model weights, service implementations, or validate art quality.

## Verified factory identity

All 46 files in `sprite_workbench/vendor/vfx/manifest.json` exactly equal the
UTF-16 `[start,end)` factory-expression ranges in their recorded original bundles.
The check decodes UTF-8, slices UTF-16 code units, then reencodes UTF-8 before
comparing bytes. All four full original bundle hashes match their records:

| Original `website-art-bundles/` file | SHA-256 |
| --- | --- |
| `create-vfx-be26fa3e471fd274.js` | `11a1ee402e10ddec3ebb1d558a3e699d7b06a605846b4ddc36f346c9aa7b9065` |
| `4354-3a62375cb4c03823.js` | `cc7e87ddeb584f550ab863bc10792addab01469be1143ede0cded67a096284de` |
| `7423-93e5d1cb073f2b5e.js` | `86bc86bf3636523d279fcd03ce1d4e9368c52cd407f894699a6623617b313956` |
| `3778-ef7c5cd0341f4223.js` | `47c12e2b6e6e0e3f127b993260c72c720454e2624129e95d8632b398eeede609` |

The manifest hash pinned by Python is
`188743c8078e006117a6cbc51fdf96a73cafecc387a1a998276d93aa8d19645f`.
`analysis-root/workbench-gap-closure/CLIENT-MODULE-INDEX.json` supplies the
selected 17-factory/function inventory, whose mappings also match the manifest.
The remaining 29 slices are verified directly against the full original bundles.
An inventory is not proof that every
included UI/auth module executes. For example factories 12538 (generation review
POST), 10971 (account data fetch), and 31824 (cookie UI) are present but outside
the exercised renderer dependency closure. The production adapter provides no
`window` or `fetch`. No service behavior should be inferred from their presence.

The executed renderer is entry 39852 export `sY`, forwarding to original 55110.
Original 47381 owns recipe schemas/defaults/normalization; original 78501 owns
animation sampling and clock helpers. Python's `effects.py` and the Node loader
add local limits, input transport, SHA checks, immutable storage, and rational
frame durations. These wrappers are locally authored. None of the 46 factories
was replaced with a newly authored raster algorithm.

## Independent full-bundle oracle

`tests/source_fidelity_oracle.cjs` evaluates the four complete original chunks
in an isolated Node VM to capture their webpack registration. It never reads
the production manifest or vendored factory files. It ignores the page bootstrap
callback and invokes the captured original entry directly. No browser, network
API, provider call, or replacement art method is involved. The independently
written loader supplies webpack export mechanics and raster transport only.

`tests/test_source_fidelity.py` checks:

- Original ranges, full bundle hashes, vendored hashes, and closed factory file inventory.
- All 17 retained exact family inputs, normalized recipes, subject boxes,
  factory execution order, every byte in frame/back/front streams, and retained stream hashes.
- The two retained server recipe inputs through both independent loading paths.
- Supplied alpha values 0, 1, 127, 128, 254, 255, with source binary visibility
  at 128, mirrored subject motion, loop/one-shot sampling, and exact local clocks.
- A deliberately small diagnostic variation checking seed changes and both depth streams.

The last diagnostic is a test input, not a proposed preset or a PixelLab art
method. Both sides execute the same original algorithm. These tests establish
adapter fidelity, not an independently derived algorithm, exhaustive source
semantics, private service parity, visual approval, or useful artistic results.

The original research tree is deliberately external to the package. If absent,
source-dependent tests explicitly skip; packaged factory hashes still run.
Set `PIXELLAB_RESEARCH_ROOT` to the retained research root elsewhere. A present
but changed original fails instead of silently skipping.

## Authentic returned preset data

`tests/fixtures/effects/server-cases.json` contains two **retained PixelLab MCP
preset snapshots**. Their current live service identity is unverified. They are
not locally authored requests disguised as vendor presets.

The selected HAR requests in
`controlled-tests/prepared-parts/capture/documentation-curated.har` are:

- ID 110: `vfx_workbench`, `argv=[step,"get_preset",'{"name":"energy_orb","peek":true}']`.
- ID 124: `vfx_workbench`, `argv=[step,"get_preset",'{"name":"slash_arc","peek":true}']`.

The requests submit a preset name and peek flag, not recipe data. In the returned
`responses/{id}-metadata-preset-{name}.json`, parse `result.content[0].text`,
split once at the first newline, then decode the leading JSON value using
`JSONDecoder.raw_decode`. That object exactly equals the fixture recipe.
Tests inspect only those selected requests and do not publish the HAR.

| Name | Returned response SHA-256 | Extracted preset file SHA-256 |
| --- | --- | --- |
| `energy_orb` | `e3a368a4804c1c3c6621787c5e63faf1f43914ae6b123b79a219976dc51091b4` | `2ef88bedad96433b84107b9e7e44b10524b172aeb99443c23aa9f3988193c41e` |
| `slash_arc` | `942cdb8798f06a8c8deae24c629eb5639e8263afde0b4d22271dc637f4941897` | `ff996e7e7479b6fa6ac46afafda6204ff1dfa71b3b8c18405222812b55628931` |

The corresponding extracted files are
`controlled-tests/prepared-parts/presets/{name}.json`. Retained fixture export
image/JSON hashes are independently checked against `server-cases.json`:

| Name | PNG SHA-256 | Export sidecar SHA-256 |
| --- | --- | --- |
| `energy_orb` | `53e8243be0b87c8e736eeb8616edba40bb6ede6749550679ea55e06157770776` | `c19b07ef29c88c61dfcf4b0b6aa0e52ee0bf37851113bc7e0827e9bc9f2fdfc1` |
| `slash_arc` | `6521cf2fdf58f0259a9012eb604f43051168ebe30b0ec72ed3066e217a5326fe` | `60bc038ac88815ffd3eeb42e83a1ab8f46b8954dd67c7678952904dc919c2aa5` |

The other fixture file, `reference-cases.json`, contains diagnostic recipes for
17 families, with per-case `source_receipt.path`, `sha256`, and JSON pointer
into retained execution outcomes. Those diagnostic recipes must not be labeled
vendor presets. Their original outcome hashes and case identities are checked.

## Existing local methods remain a separate authority

`raster.py` names its behavior `local-v1`: pixel-center polygon coverage, clipping,
selector semantics, and guards are local policies. `construction.py` integrates
the locally authored sprite-edit-project toolkit, with its own history,
indexed-cel, import, and composite policies. Similar tool names, deterministic
results, or source-bound public contracts do not make those implementations
PixelLab's private pixel-workbench handlers. They cannot substantiate claims
about PixelLab repair, shading, cleanup, ownership inference, or neural methods.

`METHODS-SOURCE-BINDINGS.json` documents selected pose/projection equations and
conditioning contracts. Its boundaries remain relevant: deterministic projection
and source schema recovery do not recover the generation service. A UI restricted
to the exact retained procedural renderer plus clearly attributed preset/control
data fits the evidence. Relabeling the separate local construction algorithms as
PixelLab methods would violate the user's source-method constraint.

## Validation and remaining review

After merging root integration `55cec16`, the oracle also calls full-bundle
47381 exports `W$` and `uY` directly. The expanded fidelity suite compares both
authentic preset declarations and six default/override set/mul/add scenarios
against the new services, including rendered bytes. This verifies that declared
recipes enter rendering and bindings apply once; the effective inspection recipe
is not accidentally rendered for a second application.

Original errors for range violations, overlapping bindings, and normalizing the
already normalized `rng:null` result match the service exactly. Normalization
is not generally idempotent; an inspection result is not a universally safe
replacement for the original declared input. The wrapper's rejection of an
unknown supplied control ID is explicitly a local guard: original functions
receive recipe declarations, not this wrapper's separate values dictionary.

`python -m pytest tests/test_source_fidelity.py -q` completed with **41 passed**.
The combined fidelity, controls, source-service, and effects suites completed
with **94 passed** in 19.55 seconds.
Before the additional service cases, the combined original 29 fidelity cases and
20 existing effects cases completed with **49 passed**. No observed algorithm or
control substitution required a production fix during this review.

The new UI needs a subsequent integration review once it lands. Full editor interactions, all
possible recipes, image inputs, exports/codecs, and visual quality are not
exhaustively covered by this bounded differential.
