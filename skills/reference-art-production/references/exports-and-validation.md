# Export profiles and bundled helper

The helper is optional. Use a project's existing pipeline when it already supplies these guarantees. It performs mechanical transformations only, requires Python with Pillow, and makes no API calls. Locate it relative to this skill's folder; do not hard-code a particular user's home in project scripts.

## Pixel-sprite profile

Choose dimensions, fit, anchor, scales and alpha handling from the art brief. An example modern portrait profile uses a 256×256 canvas, a maximum 224×224 subject, bottom anchor at y=240 and exact 2× enlargement to 512×512. These are example settings, not rules for other art.

The helper crops to the master's alpha bounds, fits with nearest-neighbour resizing, then anchors the **actual resized opaque bounds**. Nearest downsampling can discard the final opaque row; placing by the intermediate image height can produce a one-pixel baseline error. Pixel variants must equal an exact integer enlargement of the canonical image, not separate AI generations or filtered resizes.

Thresholding alpha is appropriate only when the chosen pixel pipeline calls for it. `alpha_threshold: null` preserves alpha; an integer threshold makes it binary. Keep the unthresholded master. A transparent image may contain soft glow/shadow pixels; inspect the final thresholded export to avoid halos or losing thin appendages. Never claim that a binary alpha check proves the silhouette is correct.

`reject_source_boundary_touch` catches silhouettes touching the generated canvas before fitting. Fitting a clipped subject into a smaller canvas does not restore the missing part. A false value can be appropriate for intentional edge crops; record that decision and review visually. Transparent backgrounds must actually have an alpha channel, not a painted checkerboard or a solid colour.

For engine imports, keep pixel filtering nearest and use lossless assets. Apply mipmap and alpha-border processing settings deliberately and test them in the target engine. Pixel portrait sizes do not determine physical unit scale or animation pivots.

## Raster profile

`kind: raster` copies the selected master at native resolution, byte for byte. It preserves gradients, soft alpha, colour encoding and native framing. It does not enforce the pixel-sprite canvas, anchor or scale rules. Choose `transparent: true` only when transparency is actually required. For requested resized print/web assets, use the appropriate colour-aware image/export tool and inspect the result; do not silently convert the art into sprites.

## Manifest contract

Keep this manifest in the working collection root. File paths resolve from that directory; output paths are relative and stay inside it. Masters may be absolute machine-local paths, but references and prompt receipts should be copied into the delivered collection when portability matters. Store actual input hashes using SHA-256, not the literal tokens in this example.

```json
{
  "schema_version": 1,
  "complete": false,
  "target_ids": ["character-01", "character-01-alt-catalog-entry"],
  "art_spec": {
    "kind": "pixel-sprite",
    "transparent": true,
    "canvas": [256, 256],
    "fit": [224, 224],
    "anchor": "bottom",
    "baseline": 240,
    "alpha_threshold": 128,
    "scales": [1, 2],
    "reject_source_boundary_touch": true
  },
  "subjects": [{
    "id": "character-01",
    "name": "Original clockwork explorer",
    "group": "Characters",
    "covers": ["character-01", "character-01-alt-catalog-entry"],
    "master": {"path": "masters/character-01.png", "sha256": "ACTUAL_SHA256"},
    "prompt": {"path": "receipts/character-01.json", "sha256": "ACTUAL_SHA256"},
    "references": [{
      "role": "identity",
      "path": "references/character-01.jpg",
      "sha256": "ACTUAL_SHA256",
      "page_url": "ORIGINAL_SOURCE_PAGE_IF_DOWNLOADED",
      "credit": "Actual source creator",
      "notes": "Full-body geometry reference"
    }],
    "notes": ["Static portrait; goggles and backpack retained"],
    "edits": []
  }]
}
```

For an original brief with no input images, use `references: []` and save the brief plus the actual executed prompt in the receipt. For native raster art, the `art_spec` can be just `{"kind": "raster", "transparent": false}`. An edit can add an actual receipt under `edits: [{"prompt": {"path": "receipts/repair.json", "sha256": "..."}, "reason": "..."}]`. Point `master` at the **latest accepted candidate**, preserving earlier versions separately.

`target_ids` is the frozen requested inventory. Do not regenerate it from successful outputs: that would hide missing subjects. `covers` defaults to the representative ID; use aliases only for art that is genuinely interchangeable. The helper checks exact unique coverage.

## Commands

Use the actual discovered skill path in place of `$ART_SKILL` below. Run from the collection root, with a versioned working manifest if preserving an existing delivery. `export` writes derived files under `exports/` and updates the manifest. It never accepts a visual review automatically.

```bash
python "$ART_SKILL/scripts/art_assets.py" export manifest.json
python "$ART_SKILL/scripts/art_assets.py" contact-sheet manifest.json --page-size 8
```

For a batch review queue, add `--pending-only` and a fresh `--out review/pass-02` directory. Use that directory's `pages.json` as the snapshot index. For the claim/source-review/worker setup and durable review recording, follow [batch-runbook.md](batch-runbook.md).

Inspect the labelled images and their references. Record each review honestly against the canonical export hash from the updated manifest:

```json
"visual_review": {
  "status": "accepted",
  "export_sha256": "ACTUAL_CANONICAL_1X_EXPORT_SHA256",
  "reviewer": "root-agent",
  "observations": ["Matched silhouette, palette and visible accessories", "Hidden rear detail remains authored"]
}
```

Use the actual reviewer identity; do not fabricate a user or independent-agent review. The comparison-sheet index only records what was displayed, not who inspected it. The helper retains a stale review in `review_history` and resets the current review if an export changes.

```bash
python "$ART_SKILL/scripts/art_assets.py" verify manifest.json
python "$ART_SKILL/scripts/art_assets.py" verify manifest.json --complete
```

Verification requires accepted current review hashes, exact coverage, actual prompt receipts, valid source/master hashes, correct export pixels and promised transparency. It writes `verification.json` and exits nonzero on failure. `--complete` sets the manifest complete only on success. It does not establish pose continuity, texture seams, editable layers, artistic accuracy or engine runtime behavior; perform the additional checks required by the brief before using that completion command.

The helper emits no browser gallery or packaging automatically. Build only the gallery/ZIP/source-ID map requested or useful for this project. Handoff links must point to files that actually exist. For animation, include separate frame IDs, timing and pivots and verify continuity; do not relabel still portraits as animation-ready.
