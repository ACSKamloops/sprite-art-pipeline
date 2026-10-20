# History performance gate declared before new benchmark

The v1 supplied-marker baseline reported 0.904 seconds for the first edit and
18.123 seconds for the twentieth edit on 256x256, 24 frames and one shared cel.
The prior cumulative replay guard admitted fewer edits as layers increased.

For v2, require on the same local machine:

* 20 guarded one-pixel edits on 256x256, 24 frames, one shared cel/layer;
* 20 edits on 256x256, 24 frames, 11 distinct shared layer cels with partial alpha;
* every individual steady edit and warm undo/redo under 2 seconds;
* first-to-last edit ratio below 3 (small constant I/O growth is allowed);
* a genuinely fresh Python subprocess cold load of the final state under 15 seconds;
* exact equality to pinned scalar receipts on independent small differential
  fixtures, and cold replay/tamper detection, before accepting speed evidence.

Performance is measured separately from aesthetic quality. It proves neither
art generation nor full PixelLab parity. Cold verification remains linear in
history length and project complexity; the process-local proof cache is not an
on-disk trust shortcut. Separate resource caps bound peak working index values,
receipt count, checkpoint bytes and cold replay pixel/operation work.
