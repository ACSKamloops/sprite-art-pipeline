# Delivered Captain MP4: visual acceptance withdrawn

**Rejected as the requested convincing game walk.** This supersedes my v20 art approval in commit `1bf4d9e`; the original receipt is retained unchanged. The user's direct viewing and rejection exposed a failure in my review. I am not assigning a replacement score or tuning a verdict to the old threshold.

The delivered MP4 is `d749819c6551d6a21a5ea2188180b0f1c9974779dfa861c96f2eb27e7cf2cb89`. Its source manifest is `82cc443fc6b5f05e806a60788a01602c4f683376f1a6ff303abb5cdb43a6da86`.

I independently decoded all 288 frames. The file is 512×544, 60 fps and 4.8 seconds: two 1.2-second loops at native size, then two at nearest 2x. Every sprite crop's closest source pose agrees with the declared source clock: 288/288. Average expected-pose RGB error is 3.30/255, maximum 4.41/255, consistent with this lossy H264 viewing artifact. There is no demonstrated reversal, scrambled sequence or doubled-speed export. Each 60 Hz cycle presents 66 of 72 poses because some 12–21 ms source holds are shorter than a video sample. That sampling is a limitation, not an explanation for the poor underlying walk.

I personally viewed every consecutive displayed frame of the first native loop and first 2x loop: 144 displayed frames in 24 sheets, plus both actual loop boundaries. The second loop at each scale was algorithmically compared, not separately claimed as visually reviewed. I also inspected the parent's actual-video eight-key sheet. This is decoded chronological image review, **not continuous real-time video ingestion**. The user's real-time viewing remains distinct evidence.

Concrete visual problems:

- **0.20–0.38 s; repeated at 2.60–2.78 s:** the legs bunch under the holster into a compact bent-knee silhouette. The apparent action is feet shuffling beneath a largely retained hero illustration, rather than the body passing persuasively over a supporting leg.
- **0.80–1.00 s; repeated at 3.20–3.40 s:** the opposite exchange repeats that tucked configuration. Alternation exists, but alternation alone does not make an appealing or convincing heavy walk. The lower-leg shapes articulate like separate panels rather than a coherent changing armored limb.
- **Whole 1.2-second cycle:** the raised sword, shoulders, shield and torso oscillate around the original pose. Their attachments are mostly preserved, yet the small compression and counterrotation do not establish a strong enough load/push/release relationship. A technically connected cutout can still look puppet-like and funny.
- **2x segment, especially 2.73–3.18 s:** the enlarged view makes the difference between richly illustrated upper kit and comparatively simple moving leg panels more conspicuous. Cap seating and shell shading improved individual parts, but did not solve the whole figure's motion appeal.

The flat background provides no environmental translation or contact reference. That makes this preview a poor demonstration of grounded travel, but it does not justify blaming the export or inventing a measured foot-slip failure. No heel/toe force or physical support is established by these sheets. There is no evidence that merely changing the container format would repair the artwork.

Why I missed it: I focused on whether each requested local repair had worked—cap seat, chest separation, grip and wrap—and let incremental improvement become a high overall quality score. Absence of clipping, popping and detachment was treated as stronger evidence of appeal than it is. My sparse browser screenshots sampled the sequence, but did not supply continuous temporal perception. Exhaustive adjacent-pair inspection verified continuity; it could not justify the claim that the result was a convincing 9/10 animation. The source poses are substantially the same ones I had already inspected, so this is a correction of my judgment, not discovery of a hidden export defect.

The prior mechanical/source tests remain useful for their narrow claims. The prior art acceptance is withdrawn. This report is a diagnostic, not an art-repair prescription or approval of another candidate.

Reproduce: `python qc/temporal/captain-delivered-video-review/audit_video.py`. This uses read-only original MP4/source inputs and writes only this review directory. `sequence-check.json` retains per-video-frame source matches; `ffprobe.json` retains actual codec/timing information.
