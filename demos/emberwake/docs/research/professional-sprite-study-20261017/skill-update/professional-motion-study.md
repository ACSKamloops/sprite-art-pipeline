# Learn motion from actual artist sources

Use this before another generated bank when the user asks for professional
examples or has rejected apparently successful numerical/still reviews.
This is reference analysis, not an instruction to generate replacements.

## Pick useful evidence

Choose real downloadable artist or shipped-game files. Pin the upstream
version, archive/Git blob hashes, authors, license, relevant source paths and
intended action/view. Preserve downloads; execute no bundled code merely to
inspect images. Keep licenses with the files and respect distribution and
AI-use restrictions. A free download is not universal reuse permission.

Match references to the actual target before building an extensive measurement
study. Put untouched native target/candidate poses beside each other. Compare
head/body proportions, limb mass, elevated/front/oblique camera, shaded material
volume, native visible body height and the specific action. A run is not a walk.
A professionally finished animation can still be the wrong comparison. Do not
let storefront tags, a large cell size or exact extraction substitute for fit.
Keep appearance matching separate from motion/action usefulness. In this study,
the user rejected Duelyst/Tiny Swords as primary references because their styles
were too different. Later Ragnarok walks were closer shaded JRPG comparators,
but still slimmer/smaller-headed; the reviewer qualified their walk usefulness
without accepting them as the primary appearance/proportion target.

Assign a visual role only after inspecting native-size complete chronology:
finished-art/motion reference, stylized body/action example, geometry-only
control, or excluded. Commercial provenance and a valid file do not establish
quality or suitability. A bare-body base is not the finished-art standard.
View every pair and wrap, or the actual one-shot entry/recovery transition.

## Recover the actual clock and registration

Decode native tags/exposure lists, trim rectangles, rotation and offsets.
Verify source-atlas cells against native composites. A row may contain one
idle plus eight walk poses; grid count is not animation order. Preserve the
full fixed source canvas; never recenter each drawing independently.

Separate native file holds, creator GIF timing, written recommendations,
cache defaults and active runtime modifiers. In the pinned Duelyst study,
resource80ms became64ms through a4/5 cache multiplier; movement/attack speed
wrappers also had to be checked. The recorded default modifiers were1.0.
These are source-derived defaults, not a live gameplay capture. Different
configurations can change them. Trace callbacks/state queues as well as cels.

An attack is not automatically cyclic. One verified Duelyst profile was
23attack cels ×64ms,11idle-transition cels ×64ms, then breathing12×96ms.
Its3328ms finite review samples one breathing cycle; native breathing repeats
under the recorded unselected/no-queued-state conditions. Two visual sweeps
do not establish two gameplay damage events. Keep visual and rule events apart.

Use the exact APNG helper or another verified writer when retaining holds.
Some exporters merge repeated identical cels; decode and compare every RGBA
exposure and actual delay field, rather than assuming frame count survived.

## Measure only what can be observed

Keep a fixed reference body extent for the whole clip, with its defining
source pose/edges. Label it an analyst visible-art proxy rather than stature.
Do not use a weapon/VFX-expanded bounding box as body height or fit each pose.
Preserve source coordinates and the actual rational clock. Label any optional
common-height or normalized-phase display as a diagnostic transformation.

Transcribe visible head/body/belt/hand/foot features per frame, with visibility,
uncertainty, source-pixel witnesses and persistent identity where supported.
Use null for hidden or ambiguous points. A screen-side dark contour may switch
limb identity; it is not a persistent anatomical foot. Do not interpolate
unknown joints into measured data. Confidence labels are not probabilities.

Alpha-on-paint verifies occupancy, not semantic identity. Independent review
found three alleged Duelyst boot points on opaque white/gold slash effects.
A conservative reread withdrew 22 uncertain samples in total, including those
three, rather than moving them onto guessed anatomy. They became null in a
separate annotation revision while the original source freeze stayed untouched. Recompute derived profiles, plots and viewer
metadata from the corrected revision, not only the visible overlay.

Useful descriptive measurements include duration/holds, body-proxy range,
visible feature paths, pose-onset displacement, silhouette change and loop
boundary context. An onset secant is not continuous painted velocity; values
below annotation uncertainty do not establish precision. Do not average
different styles/actions/cameras into a universal ideal or quality score.
Tiny Swords run uses6×100ms and pronounced stylized bob; LPC native walk uses
8×1/9s and a much smaller head range. These are different designs.

Fit ground-relative contact only after establishing a persistent contact-bearing
landmark, contact phases, projection and root motion. A conditional boundary
fit can have zero residual while a held sprite still drifts during the hold.
The real study deliberately made no source stance/contact fits; synthetic
analytic tests checked the formula without claiming recovered biomechanics.

## Review and apply

Have an independent reviewer inspect source mapping/clock and visual feature
identity. Preserve rejected annotations, exact corrections and fresh hashes.
Check the actual local player: native versus normalized clock, all source
hashes, pause/step, finite completion and recovery. Timed callback captures
establish transport, not continuous human perception or art acceptance.

Keep the actual user-preferred original beside later experiments. Select a
specific action/view/style and one observed deficiency before transferring
motion. Use normalized deltas as construction guides only; new material planes,
occlusion, silhouette and hidden anatomy still need drawing and visual review.
Do not commission another full sheet merely because the measurements ran.

The local tested study is at
`/home/astra/artifacts/emberwake-professional-sprite-study-20261017`.
Its scripts/data are evidence pointers, not a redistributable asset license.
The case includes restricted local-only artist material; do not package the
entire folder into a skill or publish it. Store general tools and synthetic
tests separately from creator art.


## Portable descriptive analyzer

`scripts/measure_reference_motion.py` requires Pillow, NumPy and Matplotlib.
Run it against a SHA-bound manifest using a fresh output folder:

```sh
python3 scripts/measure_reference_motion.py /path/to/study.json --out /path/to/fresh-results
PYTHONPATH=scripts python3 -m unittest discover -s assets/professional-motion-math-tests -v
```

The input has a `clips` list. Each clip needs a unique safe `id`, `timing`
(provenance object), one fixed positive `reference_height_px`, `loop`, and
`frames`. Each frame has an image path relative to the manifest folder, PNG
`sha256`, and positive rational `hold: [numerator, denominator]` in seconds.
Keep frames on the same canvas. Unknown timing uses null holds and is labelled
uniform pose index only; do not mix known and unknown exposures as a clock.
Optional `landmarks` maps feature names to `samples`, one per exposure:
`{xy: [x,y] or null, visible: true or false, ...source_notes}`. Retain uncertainty
and proxy identity in `annotation_uncertainty`/`proxy_scope`. Observed features
remain paint proxies. Set `contact_fit_eligible: false` and
`stance_hypotheses: []` unless persistent contact identity and the required
motion assumptions have actually been established.

Outputs are descriptive `MEASUREMENTS.json` and trajectory plots; quality_score
is always null. The analytic tests check conditional fitting and its held-pose
limitation, not visual quality. Native source conversion and the local player
remain separate adapters and require their own source-clock checks. A third-
party rendered APNG can prove its encoded preview holds, not the original
client's pacing, sprite scale or full compositing fidelity.
