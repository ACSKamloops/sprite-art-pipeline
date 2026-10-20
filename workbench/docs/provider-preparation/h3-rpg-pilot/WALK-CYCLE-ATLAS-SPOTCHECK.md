# Separate walk-cycle atlas spot check

After completing the native slash review, the reviewer viewed the actual
`h3-walk-001/sprite-cycle/cycle-8/sprite-atlas.png` and
`cycle-16/sprite-atlas.png` at their original sheet resolution. This is a separate
**24-cell atlas inspection**, not continuous playback, all native-cycle frames,
a game-engine run or comprehensive alpha-edge acceptance. The earlier native
walk's 107 contact frames are covered by its own report.

The manifest explicitly calls this locally authored key/sampling/resize/export,
not recovered PixelLab code. It selects native interval **[16,64)**, keeps the
fixed canvas, uses a border-connected black alpha key with RGB tolerance 12 and
four-connectivity, and applies a uniform nearest resize to 256×256. It performs
no quantization, recoloring or AI repair. Eight samples have 1/4-second holds;
sixteen samples have 1/8-second holds, both over an authored two-second loop.
Those are local derivative clocks, not a recovered sprite FPS.

The sheets show a useful sequence of alternating legs with recognizable clothing,
hair and equipment. Removing the full video's idle lead/tail makes this a more
plausible cycling candidate. The 16-pose sheet describes transitions more clearly
than the eight-pose sheet. Sword-angle/reach variation and close boot overlap
remain present; sampling does not repair them. A seam rating requires timed
last-to-first viewing. The atlas alone does not establish planted-foot behavior.

On the tool's dark image display, no large character region visibly disappears,
but this does **not** validate black-key edges against light or colored scenery.
Dark outlines touching the keyed background may be lost, and brighter compressed
fringes may survive. No contrasting-background visual test was performed here.
The native video was opaque; this alpha is a local approximation and must remain
labelled accordingly. No production-readiness rating or alpha approval is added.

The reviewer independently checked every file listed in the derivative manifest
against its recorded SHA-256. The selected native source manifest/video identities
remain those in `NATIVE-WALK-REVIEW.md`. Source video is referenced externally and
is not embedded in this derivative bundle, as the manifest already discloses.
