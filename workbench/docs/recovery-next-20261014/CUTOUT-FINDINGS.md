# Public cutout: three captured calls, one RGB design

All three returned PNGs are **byte-identical**, SHA256 `4723b057cb4ba061ce5d416fe5acb5f330622f2465356ee4906ccc8a9573ea16`. Simple/Complex on the opaque image and Simple on the alpha-patched version produce the same binary-alpha cutout. This is an exact observation on one RGB design, not proof of shared implementation or PixMiniMax internal processing.

The reviewer made no calls. Parent submitted three requests, each HTTP 200 with reported usage 1.0 generations, 3.0 total. [Machine findings](CUTOUT-FINDINGS.json) bind frozen PLAN `7fe6dea39aead1e171caa7239ce1b8e08b766b45568873faa3e7da61e89b8260`, all source/request/wire/response/HAR/state/output hashes, regional measurements and all 12 counter-candidates. `analyze_cutout.py` verifies the actual HAR POST bytes against each frozen wire hash, actual embedded source PNG against retained source bytes, and both HAR/response PNG descriptors against `output-00.png` **before** measuring pixels. Authorization/header values are not accessed or printed. No frozen input/preparer was changed.

## Measurements and fixture correction

- Opaque inputs: 6538 pixels change from opaque background to `[0,0,0,0]`; 2678 remain opaque with unchanged RGB. No RGB changes where both input/output are visible. Enclosed background-colored 64-pixel patch, 42-pixel channel-shaped patch, dark chest details and near-green decoration all remain opaque with exact RGB.
- Alpha input: 6538 background pixels become zeroRGBA; six alpha 0 armor pixels become visible alpha 255; six alpha 64 and six alpha 128 pixels also become 255. Original hidden armor RGB is retained and made visible, not composited against white or zeroed. Thus source alpha is **not preserved** here. Of 6556 alpha changes, 18 are these foreground patches.
- All output alpha 0 pixels have zero RGB. This describes returned pixels, not the location or algorithm of hidden-RGB cleanup. Input alpha 0 RGB becomes visible on retained foreground; this differs from Godot's separate pre-upload normalization.
- **Our original region name was wrong:** `open_same_background_channel` is enclosed. The left arm at x27,y59–61 blocks its intended mouth at x28. Connectivity measured from the source pixels, with both 4/8 neighbors, confirms 0/42 of this region reaches the border. The original annotation/fixture is preserved; this report corrects the interpretation. It was not a valid open-channel discriminator.

The source has 6644 exact-green pixels: 6538 border-connected, plus 64+42 enclosed. Four- and eight-neighbor connectivity give the same result. These geometry facts are measured source properties, not assertions about what a semantic mask should remove. The green chest patch may be a panel or hole; no quality score is justified.

## Bounded candidate fit

Twelve authored candidates were tested: 4/8 neighbors × maximum RGB-channel distance from top-left background ≤0/8/16 × retaining source alpha or forcing retained alpha 255. Border-connected eligible pixels become zeroRGBA. There is no per-region fitted mask or arbitrary global lookup.

Forcing retained alpha 255 gives **zero full-RGBA mismatches on all 9216 pixels of each of the three captured cases**, for all six connectivity/threshold combinations. Preserving source alpha matches both opaque cases but fails 18 armor pixels on the alpha case; counterexamples are retained in JSON. This identifies an exact small candidate family for these observations, not a recovered algorithm. Threshold 0 cannot be distinguished from 8/16, and 4 cannot be distinguished from 8 neighbors because this fixture lacks the required reachable near-color/diagonal features. An unknown semantic/morphological method could produce the same mask here.

Simple/Complex have identical returned PNG and response JSON bytes on this single design. That does not establish their task modes are aliases, their results generally identical, their seeds deterministic, or either exact policy inside PixMiniMax. A corrected independently checked diagnostic fixture is needed to distinguish connectivity/tolerance hypotheses; no additional calls were made during this analysis.

Reproduce offline:

```
/home/astra/projects/pixellab-local-workbench/.venv/bin/python docs/recovery-next-20261014/analyze_cutout.py
```

Follow-up: [corrected connectivity findings](CUTOUT-CONNECTIVITY-FINDINGS.md) test a separately frozen, pixel-verified source. They distinguish Simple/Complex and reject every predeclared flood candidate, including the family that fit this initial design. Initial measurements and the blocked-channel correction above remain historical evidence.
