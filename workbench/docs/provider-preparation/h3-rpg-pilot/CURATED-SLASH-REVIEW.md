# Curated local margin-slash review

**Corrected coverage helps: the sixteen-pose derivative now exposes the actual
strike transition instead of skipping it. Native weapon clipping and ambiguous
blade/grip presentation still block complete game-sprite acceptance.**

Reviewed artifact:
`/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/h3-slash-margin-002/sprite-once-curated/`.
Manifest SHA-256:
`9a09e1922eb8c4615a96006c2b42aef4d314e28a2b97cbc692e2473c26563a55`.
It binds native video
`aed5ac139188860f2e3e39f58484ebda394c77fa7b8ae99f777cced03c572132`
and manual index-file SHA-256
`17d34301104835b6542745d1c9448111043b05e220f6a5c4f8fe4b55aacc8968`.
Every file listed in the derivative manifest passed its recorded content hash.

Actual visual coverage: the complete **once-16 sprite atlas**, plus individual
native frames **24, 26, 27 and 35**. The prior rejected uniform atlas was already
viewed in the matched comparison; its index mapping was compared for coverage.
This is still-image inspection, **not continuous video or sprite playback**.
Root's separate callback/completion check does not add continuous visual viewing
to this reviewer's coverage. The curated eight-pose variant was not viewed.

The selected indices are
`0,12,18,23,24,25,26,27,28,35,52,73,78,85,94,106`.
The old uniform sixteen-pose derivative omitted **26/27**, the fast strike.
Their inclusion now makes the transition from drawn-back weapon to crossed-body
stroke apparent. Including **24/25** also exposes the clipped backswing instead
of hiding it between samples. This is a useful correction of local sampling,
not an improvement to native generation or a recovered PixelLab extraction rule.

The actual native checks show the remaining issues:

- **24:** the physical blade exits the left canvas; the tip is missing. It cannot
  be recovered by keying, resizing or adding padding to these pixels.
- **26:** the blade is not separately readable amid the foreshortened/blurred
  forearm and torso. It may be an edge-on strike or motion smear; this view does
  not prove literal weapon disappearance, nor establish stable grip/rigidity.
- **27:** a broad doubled/smeared blade-like shape crosses down-right. It conveys
  speed but does not provide a clean, inspectable rigid sword silhouette.
- **35:** the physical blade continues past the right boundary, again without
  a tip. The native crop remains a stronger acceptance blocker than sampling.

The manifest correctly describes local manual selection, a border-connected
black alpha key, uniform nearest resize to 256px, no recentering, no quantization,
no recoloring and no repair. Sixteen selected PTS differences plus the native
terminal hold retain total **107/24 seconds**, with once-only playback. This does
not preserve every native motion frame: omitted motion is approximated by holding
the selected poses. In particular, selected **35→52→73** retain roughly **1.58
seconds** of follow-pose time; corrected coverage does not remove the long native
follow-through or idle tail. Their timed aesthetic effect remains unviewed here.

The hero's face, hair, tunic, armor and shield remain recognizable in the atlas.
Ground contact, concealed shield grip, consistent weapon length and alpha edges
against varied backgrounds remain unapproved. The dark tool display can hide
black-key outline loss or residual video fringes. These are local approximate
transparent sprites derived from opaque video, not native generated alpha.

Keep the rejected uniform derivative and this corrected derivative separately.
The curation is a useful, honest diagnostic and authoring step, but is not finished
game art and receives no automatic higher rating. No provider/model/agent calls,
credential access, native repair or root edits occurred in this review.
