# Independent native H3 walk review

**Worth continuing; a promising motion draft, not a finished game sprite.**
This is a subjective adversarial review of one generic RPG hero. No provider,
agent or model calls were made by the reviewer. No Captain uploads or matched
PixelLab generation belong to this review.

Artifact root:
`/home/astra/artifacts/pixellab-h3-rpg-pilot-20261014/h3-walk-001/`.

| Artifact | SHA-256 |
| --- | --- |
| `source.png` | `571b74ac6bd1a945263c8c5cdf2b1eab9facf277bbc752c767de6f4412bf8084` |
| `native-video.mp4` | `97e83ef3522a8892af98672861ee7ec5214c24dd4f441e38cc448c762c5ab046` |
| `media-review/MANIFEST.json` | `b5798c0c8f5de2f67e671f9fa0ee93342219c207e1da2a1e7cd4e2430430dd5b` |

The reviewer independently verified the native video hash and all 107 decoded
native-frame hashes against this manifest. It records 768×768 H264/YUV420p,
24 FPS and presentation end 107/24 seconds (4.4583 seconds), for a requested
four-second clip. Those facts do not establish aesthetic acceptance.

## Actual coverage and provisional ratings

Viewed the original input, **all chronological pages 00–06 covering frames
0–106**, the eight-sample sheet, and native-resolution frames **19, 42 and 106**.
The chronological sheets display full native canvases at 256px. This is ordered
all-frame contact-sheet inspection, **not continuous video viewing**.

| Area | Subjective provisional rating | Reason |
| --- | --- | --- |
| Source design | **8/10** | Readable silhouette and coherent blue tunic/silver armor, with recognizable sword-and-shield identity. This is illustrated sprite art, not proof of a strict hand-authored pixel palette. |
| Motion | **6/10** | Clear alternating steps and arm motion, with loop cadence, leg readability and weapon presentation concerns. Temporal smoothness remains qualified by contact-sheet coverage. |
| Game-sprite readiness | **4/10** | Opaque video, unfinished full-clip cadence, one direction, unresolved edge/equipment consistency and no gameplay integration. |

These ratings are observations for this candidate, not automatic scores or a
general ranking of H3. There is no matched same-subject PixelLab run.

## Demonstrated observations

- **Identity:** hair, face, blue clothing, silver shoulder armor and both weapons
  remain recognizable across the sequence. No obvious equipment disappearance.
- **Full-clip cadence:** frames **0–6** remain close to idle; **99–106** return
  toward idle. The endpoints look compatible, but replaying the complete clip is
  likely to introduce a stop/start pause. The severity needs continuous visual
  playback review; a similar endpoint pose alone does not prove a clean loop.
- **Leg readability:** boots overlap tightly around **18–20** and **64–68**.
  Separation becomes difficult to read at sprite scale. These frames do not by
  themselves establish an impossible joint or definite foot sliding.
- **Sword presentation:** compare **0/16**, **40–49**, and **84–93**. The blade
  moves from a downward diagonal to nearly horizontal, with noticeably different
  apparent reach. Some change may be foreshortening; rigid dimensions and reliable
  grip are not established. Native frame **42** still shows a connected hand/hilt.
- **Shield and registration:** the shield remains broadly coherent and appears
  attached; its concealed grip cannot be certified. Framing remains visually in
  place, without obvious camera travel. Root stability was judged visually,
  without claiming measured ground-contact or registration accuracy.
- **Edges:** native frame **106** shows colored/speckled edge artifacts around
  hair and armor. Generation versus H264 contribution is unresolved. Black
  background removal risks damaging dark character details; no alpha fidelity
  is established by this opaque native video.

## Independent versus root evidence

After this review, root reported actual browser playback with 107 monotonic
native-speed callbacks over 4.458 seconds and zero dropped frames. That is
separate root-executed playback evidence. The reviewer has not inspected a
retained callback receipt in this report and does not inherit continuous visual
viewing from the callback count. Mechanical playback completion does not change
the ratings or establish loop, contact, weapon or visual approval.

At persistence time, root was preparing a **separate local transparent
`[16,64)` cycle** with eight/sixteen samples. It was not viewed or approved here.
Its mask, sampling, timing and seam behavior need their own actual-artifact
review. A separately accepted/running sword-slash job is also outside this review.

Continue with native-speed visual loop review and explicit weapon/contact checks,
then examine any derived cycle on its own terms. Do not call a local alpha/cycle
derivative native H3 output or a recovered PixelLab conversion. Keep original
bytes and this unfinished candidate preserved.
