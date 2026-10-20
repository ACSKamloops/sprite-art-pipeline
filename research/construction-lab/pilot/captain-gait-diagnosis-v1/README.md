The combined walk remains changes requested. The actual exported sequence loses readable separation of support and advancing legs around 400–780 ms. This is not a missing knee bend: the guide already flexes the swinging knee to about 78°. Source armor width, foreground kit and camera projection make the visible movement look much straighter than its bones.

The photographed primary control shows support, release and folded passage clearly. Its side camera, casual body proportions and free arms differ from this guarded armored character. It does not justify inventing large bob or free sword-arm swing. The current upper module improves attachment but does not by itself create convincing mass transfer.

One bounded diagnostic widens fixed foot tracks by 6 world units per side and hips by 3 along the existing transverse axis. Foot gap becomes 37.2 world units, hip gap37.6; f27 projected ankle separation rises from8.89 to18.49 pixels. Stride, contact/pitch/swing schedule, 72 holds totaling1200ms, upper packet and bone lengths remain unchanged. Dense1441-sample preflight has minimum reach margin0.708, bone error3.55e-14 and mathematical ground error below floating tolerance. These are geometry checks, not art or material-contact approval.

**Binding contract:** `alternative-poses.json` intentionally retains the baseline `neutral_bind` and `source_upper_registration`. Use those for the same source meshes/upper attachments. Do not rebuild neutral bind from alternative pose0 or fit parts per frame. Candidate hips shift by a fixed3world units; inspect belt/hip attachment and armor collisions after rendering. The packet has no replacement shin/cap/boot art. Apply it to the repaired surfaces separately, then compare actual silhouette/fullcolor450/600/750ms against unchanged baseline. Reject widened tracks if they expose seams or produce a splayed gait.

Reproduce from this worktree:

```sh
python pilot/captain-gait-diagnosis-v1/probe.py
python pilot/captain-gait-diagnosis-v1/decode.py
```

`probe.py` uses only bundled inputs and Pillow; `source/generator.py` is the frozen authored guide with two configurable fixed offsets. `decode.py` reads the original external actualMP4 artifact read-only and verifies video hashes. It generates all requested review sheets; only the visual subset explicitly listed in `review.json` was personally inspected. Sheet labels say requested timestamps; `decoded/receipt.json` records actualselectedPTS. No continuous-video ingestion or all-three-cycle art review is claimed.

`review.json` binds actual inputs and observations; `metrics.json` covers all72 pose metrics; `track-comparison.png` is a skeleton experiment, not a finished-sprite audition. No commercial artwork acceptance and no score are assigned.
