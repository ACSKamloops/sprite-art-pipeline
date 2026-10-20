# Captain v20: rejected after delivered-video review

Current status: **visually rejected by the user**. The previous 9.025/9.17 ratings are preserved as failed review judgments; no replacement numeric rating is invented. This is a construction/engine study, not production-ready walk art.

Root decoded the actual delivered MP4 into288 consecutive images, visually inspected one complete native loop and one complete2× loop (144images in sixchronological sheets), and inspected eight enlarged decoded keys. This is image-sequence inspection, not a claim of continuous video ingestion. Input hashes and coverage are in `user-rejection-v20.json`; raw sheets/audit are `/home/astra/artifacts/captain-video-rejection-review-v1/`.

## Animation defects

Across0.000–0.583s and0.600–1.183s, the bent-knee spread and forward sword/shield silhouette persist while lower legs cycle beneath it. Contact/extension/passing silhouettes are weak; there is little convincing push-off or support-side loading. The fixed combat illustration drives the motion design, producing a crouched shuffle. The2× segment2.400–3.583s magnifies busy transformed red armour clusters and the independent leg motion. Source ownership and smooth adjacencies do not repair these whole-cycle defects.

## Export/presentation defects

The video encoder is not scrambling the pose order. A reconstruction compared all288decoded frames to their declared source raster/clock. It samples the variable12–21ms source holds at60Hz: eachcycle presents66distinct poses, skips22/27/32/58/63/68 and repeats sixholds. The4:2:0lossy encode also changes fine red/gold edge colors (maximum per-frame foreground mean absolute RGBerror10.39 on0–255); this contributes edge degradation, not the entire bad gait.

The MP4 places each source image on a fixed background. It does not render physical root, episode-fixed stance correction or a floor, unlike the tested Godot presentation. Thus the successful whole-boot world tests did not validate the video we delivered. In-place animation still needs a convincing gait; restoring the tested presentation alone will not fix the anatomy/key-pose problem.

## Review failure and next gate

The previous reviews inspected adjacent poses/timed samples yet rated identity, connected joints and small chest settle as convincing locomotion. They lacked a strong full-body gait benchmark and accepted limited changes to a fixed combat pose. Exhaustive mechanical coverage cannot rescue an unsuitable pose design.

Next construction should establish a manageable set of deliberately authored whole-body contact/down/passing/up keys for each support side, with enough extension, pelvis transfer, foot clearance, push-off and equipment counterresponse to read as walking in silhouette. Verify opposing phases and full motion at intended speed before interpolating more frames or polishing ornament. Review the actual encoded deliverable and exact-source playback; record independent motion/design judgments rather than scores obtained by iterative threshold chasing.
