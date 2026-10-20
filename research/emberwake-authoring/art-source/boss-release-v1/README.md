# Warden rear attack release

Selected pixels: `candidate.png`, copied to `assets/enemies/poses/warden/back_strike.png`. Exact ImageGen request: `prompt.txt`; actual local edit inputs: `input-back_windup.png` and `input-back_neutral.png`; unmodified tool return: `raw.png` (1254×1254).

`bake.py` performs one whole-image nearest resize, component cleanup and the explicit stage translation `[0,-3]`. It recreates the selected PNG exactly from the retained raw image and never calls a model. Use a fresh output:

```bash
python3 art-source/boss-release-v1/bake.py --output output/new-rear-release.png
```

`uniform256.png` and `comparison.png` are earlier provisional registration previews; `candidate.png` and `sequence.png` show the selected cleanup/stage. Source-body pixels are newly painted, not preservation-certified. The independent narrow review accepted arm ownership, identity and footing and flagged the sharper return to neutral for runtime checking. It describes an away/up-left extension, not a calibrated centered or ground-impact strike. See `docs/evidence/warden-release-review.md`; actual gameplay quality is recorded separately.
