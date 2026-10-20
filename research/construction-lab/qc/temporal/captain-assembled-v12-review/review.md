# Captain assembled-v12 independent visual review

**Changes requested — 8.175/10.** Gate unchanged: overall at least 9, every category at least 8.5, no critical defects. Engineering, source preservation and contact tests do not award visual points.

Manifest: `847e859fffb80656e98ae8ae7582655edeffde409ee4dbbc402bc42c0886d9df`. Browser-served manifest matches; exact player-source hash is in the receipt.

Fresh actual visual coverage: all 72 source poses, 71 ordinary adjacencies and the 71→0 wrap on 18 fixed native-canvas pair pages; keys0/18/36/54 at nearest2x; all40 actual browser chronological screenshots on28 strips. Native compensation-on played4.350s, compensation-off2.033s, nearest2x4.333s, at the declared1.2s cycle. Screenshot clock labels are bounded before/after ranges, not exact pose readbacks. No continuous-video-ingestion claim.

The source-only foreground knee/greave fixes the disappearing kneepad and does not exhibit an order pop. Relative sword carry, shield lag and cape motion improve the previous rocking-unit problem. No gross neck/grip detach, clipping or wrap snap was confirmed.

- **near-leg-volume**: The kneepad is now visible, but the near greave retains a broad flat red panel contour and largely fixed shading as it moves through passing. At native size the near armored leg has less convincing volume than the far one. Author near-leg down/pass contour and overlap keys: show the shin barrel, knee-to-shin compression and ankle cuff depth, preserving sole location and correct shield/holster ownership. Test these actual keys before adding more global width or bob.
- **loaded-release**: Body load and relative kit lag are improved, but support-leg bend, loaded pelvis position and released swing are still too similar in visual effect for a compelling heavy march. Strengthen localized support/compression versus passing/release poses and their timing contrast. Flat armored sole contact is acceptable as a conservative choice; heel/toe roll is not a mandatory missing feature or an asserted collision proof.

| Category | Score |
|---|---:|
| art_target_match | 8.75 |
| anatomy_volume | 8 |
| joint_continuity | 8 |
| pixel_craft | 8 |
| cyclic_weight_leg_phasing | 7.75 |
| gear_attachment_secondary_motion | 8.75 |
| game_usability | 8 |

This review does not require unproved heel/toe roll: conservative flat armored stance is legitimate. The remaining weight judgment concerns visible loaded-versus-released pose contrast. Do not revert the restored knee behind the holster. No production, other-direction or other-action approval is given. V6/V9 evidence remains unchanged.

Reproduce fixed-canvas evidence with `build_pairs.py`; build chronological strips from retained actual browser captures with `build_browser_strips.py`; regenerate receipt with `write_review.py`. Browser `capture.sh`, configuration, raw screenshots and clock/source logs are retained under `output/playwright/`.
