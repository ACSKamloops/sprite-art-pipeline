# Unapproved generated-key comparators

Exported the root's frozen `wholebody-key-study-v1/motion-spec.json` and `upright-key-study-v1/motion-spec.json` without source edits or any contact construction. Both retain eight150ms holds,1,200ms source cycle, fixed origin, declared in-place root and unverified intended phase labels.

Actual outputs:

- `/home/astra/artifacts/captain-key-comparison-old-source-v1`
- `/home/astra/artifacts/captain-key-comparison-upright-source-v1`

Each contains eight three-loop MP4s: normal/half-speed ×native/nearest2× ×colour/silhouette, `source-keys.png`, exact copied `source-frames/00..07.png`, a local `index.html` video player and hash-bound per-sample `report.json`. Normal files are `rgba-1x-normal.mp4`, `rgba-2x-normal.mp4`, `silhouette-1x-normal.mp4`, `silhouette-2x-normal.mp4`; other variants say `half-speed`.

Run `serve_review.py --directory <one-output> --port 8153` for loopback actualvideo playback/seek. Comparators occupy approximately11.3MiB and10.8MiB. Each codec's actual timestamps match the integer-millisecond schedule; first decoded RGB canvas has maximum2LSB conversion difference for colour and1LSB for silhouettes. Original PNG copies remain exact. There are zero stage-clipped samples; this says nothing about source-sheet cropping, anatomical validity or convincing motion. Final source files were independently rechecked against the report/copies.

First export attempts failed because my caption oracle compared `0.0ms` with `0ms` glyphs. Commit880f2d6 normalizes formatting and adds a regression; the strict pixel check was not relaxed. Both incomplete attempts remain under outputname`-failed-caption`. The corrected full exports are bound by `proof/generated-key-comparators-v1.json`.

**No art review or approval is given.** These are proposal comparisons for real full-cycle review using `REVIEW_PROTOCOL.md`. Phase labels remain intended/unverified. Neither contacts nor quality are inferred from successful export, silhouettes, a chosen best key or previous Captain reviews.
