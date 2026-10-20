# Dense v21 rigid-hip comparison

This is a NEW unapproved art candidate, not a replacement of frozen v20 proof. Root requested pelvis mean Y146 instead143 while retaining original hip-local offsets around130,143 and the same load/sway/lean, bones, boot art and foot tracks. Adaptive hip translation is explicitly disabled. All72 poses have0 reach excess and0 adaptive hip motion, so the torso can consume the same rigid pelvis transform as both hips. No stretch or per-pose boot fitting is used.

Actual eight-phase2× sheet was viewed. Body sits3px lower; full-kit anatomy/weight review must decide if this is preferable. Source v20 remains intact, with its recorded2.815px near hip compression. v21 is intended to remove that attachment compromise, not to justify an artistic score.

`contact-proof-v21/report.json` repeats the stronger actual whole-boot world RGBA test: every planted boot has exactly one world image per episode, both feet with one common actor translation. Actual sole spans0, unchanged≤0.5px gate; continuous physical held-frame negative control fails1px. Two cycles ×five samples/tick, Pillow CPU fixed512canvas; GPU/wholebody occlusion/force/anatomy outside scope. Maximum visual-vs-physical correction0.9144px.

`verification-v21.json` independently checks732 source/timing/chain/pixel/repeatability conditions. `adjacent-control-v21.json` records all72 adjacent joint steps includingloop. Source PNGs unchanged fromv20; frozen source3 under `dense-v21/source-bindings`. All72fullleg andboot-isolate PNGs, genuine1tickposes, GIF1200ms andmanifest are supplied. Parent must rerun independent composed/timed review and GPU validation with these fresh inputs; previous acceptance is never restamped.

```sh
python build.py --samples 72 --output fresh-v21
python contact_probe.py --pack fresh-v21 --output fresh-v21-contact
python verify.py --pack fresh-v21 --contact-report fresh-v21-contact/report.json --output fresh-v21-verification.json
```
