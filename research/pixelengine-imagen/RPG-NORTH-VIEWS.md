# Rear-view RPG expansion candidates, 2026-10-21

Six actual built-in OpenAI ImageGen calls produced three 24-pose banks and one
bounded repair for each bank. No H3, local model, API runner, video generation,
or baseline replacement was used. These are unreviewed candidates. The user
preferred Hybrid only for its original southeast walk; that preference does not
approve new views or actions.

The shared contract and generated art remain external at
`/home/astra/artifacts/hero-rpg-expansion-20261021/`. This worker exclusively
authored `views-north/N`, `views-north/NE`, and `views-north/NW`. Literal submitted
prompts, ordered references with hashes, result metadata, and producer findings
are also retained under [rpg-north-20261021/](rpg-north-20261021/).

| Candidate | Actual size | Layout | Finding |
| --- | --- | --- | --- |
| N/raw.png | 1024x1536 | 4x6, 24 bodies | Repeated passing role, row overflow, dodge21 turns right |
| N/raw-retry.png | 1024x1536 | 4x6, 24 bodies | Opposite passing boots improved; dodge21 still wrong |
| NE/raw.png | 1024x1536 | 4x6, 24 bodies | Rear camera coherent; walk exchange weak |
| NE/walk-repair-raw.png | 1774x887 | 4x2, 8 bodies | Same visible raised boot in2/6; repair rejected |
| NW/raw.png | 1024x1536 | 4x6, 24 bodies | Rear camera coherent; walk exchange weak |
| NW/walk-repair-raw.png | 1774x887 | 4x2, 8 bodies | Pose-guide exchange not obeyed; repair rejected |

The 24-cell sheets map walk0..7, compact unarmed punch8..11, body-only cast12..15,
idle16..17, hurt18..19, dodge20..23. Walk repairs map their0..7 only to original
walk0..7; all other original action cells remain separate. Neither repair is
selected. N retry uses the original 24-cell mapping and is a stronger walk
candidate, with its unresolved pure-back dodge explicitly flagged.

Initial N and NE used Hybrid first and the shared turnaround as appearance
context. NW used its single rear-left appearance crop first and Hybrid only as
secondary palette/style context. The north retry used the single north crop
and actual north bank as its edit target. NE's walk repair used its rear-right
crop and exact first-eight-cell crop. NW's walk repair used its rear-left crop
and an authored colored schematic pose guide. The guide is a geometry hypothesis,
not recovered anatomy or final sprite art. Its red/cyan leg chains visibly
exchange, but the resulting paint still repeats a passing role.

All returns contain real alpha. The original 24-pose returns have alpha0..254;
the walk-only returns have alpha0..255. Brown RGB in transparent pixels can make
the raw image viewer appear to show a backdrop. Alpha and checker composites
confirmed a transparent backdrop. No alpha cleanup or hidden-RGB normalization
was applied here.

N's first result returned only a data URL during a full-filesystem condition,
without a cache hint. Its exact PNG was preserved through non-echo raw TTY stdin
under `/tmp/hero-rpg-expansion-20261021/views-north/N/raw.png`, copied to the durable
artifact path, and SHA-256 compared. The other five results were copied byte for
byte from their tool-reported generated-images cache; each metadata receipt
records equality. Full data URLs are deliberately absent from text receipts.

## Inspection and processing boundary

[rpg-north-inspect.py](tools/rpg-north-inspect.py) measures actual source size,
alpha, nominal equal-cell bboxes, and full 4-connected body bboxes at alpha>=32.
All 24-pose candidates have exactly 24 components of at least 1000 source pixels;
both walk repairs have exactly 8. This count does not establish anatomy or motion.
It saves row-wise full-body bbox bottoms across all four cells so a packer can
reason about row offsets without clipping source toes or heads.

The chosen diagnostic preview is one whole-sheet nearest resize to 320x480 for
24-pose sheets, or 320x160 for walk sheets. The nominal 80-square crops and 3x
checker contact sheet reveal grid conformance problems; they are not final
native sprites. No frame was fitted, resized, or recentered independently.
Production scale, row origins, source-body ownership, alpha policy, and final
80-square/pivot [40,72] registration belong to the root/pack worker. Source body
height varies between returned banks; it has not been silently normalized here.

Run the inspection with the existing repository Python environment:

```bash
/home/astra/projects/sprite-art-pipeline/.venv/bin/python \
  research/pixelengine-imagen/tools/rpg-north-inspect.py \
  /ABSOLUTE/raw.png /ABSOLUTE/fresh-inspection --rows 6
```

Use `--rows 2` for walk-only returns. Durable inspections are in each candidate's
`qc-initial`, `qc-retry`, or `qc-walk-repair` directory. Every pose was inspected
as a sheet and with fixed-grid nearest previews. Continuous normal-speed review,
independent scores, native package export, sockets, editor exchange, and engine
acceptance were not performed by this worker.

The exclusive `sprite-art-pipeline-rpg-views` worktree remains until its commit
is integrated and root review/handoff is retained. Root owns its integration and
cleanup. It was narrowed with Git sparse-checkout to docs/skills/research/scripts,
freeing 134,791,168 bytes at that point. No unique data or shared cache was removed;
omitted tracked paths remain recoverable from Git. The canonical checkout and
preferred baseline were untouched.
