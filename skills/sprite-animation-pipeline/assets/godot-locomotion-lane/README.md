# Local authored sprite locomotion consumer

Copy this folder to a fresh directory, supply your own authored images/manifests, then configure and launch:

```bash
python3 configure.py /absolute/path/walk/manifest.json --bank /absolute/path/bank.json --stride 48
godot --path .
```

No character images, selected configuration, test fixture or historical reports ship in this folder. Configuration copies all selected dependencies into `selected/`, creates relative runtime paths and records original source hashes. Runtime needs Godot4.7.2 (tested); configuration needs Python stdlib. GPU verification additionally uses Pillow/NumPy. This local raw-PNG consumer has no verified packed/exported-game build.

The room has one authored direction and keyboard/buttons: Right/D hold or Space toggle; P pause; N visual-pose inspection at a fixed physical root; R reset; .5/1/2x rates. Physical collision remains active during authored root motion. Input changes during a finite transition queue until completion. Single-pose idle variants may use arbitrary names. No anatomy interpolation or image blending creates missing source poses.

Source manifest fields: `canvas:[width,height]`, `pivot:[x,y]`, `loop`, optional rational `duration:[num,den]`, and ordered `frames:[{file,sha256,hold:[num,den]}]`. Holds must be positive; a declared duration must exactly equal their rational sum. Source files may repeat or have names unrelated to binding order. Configuration derives exact rational cumulative boundaries and cycle duration. Runtime selectors compare strict boundaries; only normal engine-clock floating arithmetic gets machine-roundoff normalization. Frame count, source dimensions, pivot and hold clock are data.

Bank schema `authored-locomotion-bank/v1`:

- `source_walk:{manifest,sha256}` pins the source walk.
- `idle_variants:{arbitrary_key:{manifest}}` selects authored single-pose stances.
- `initial_idle` is optional; defaults to the first declared idle key.
- `stop_by_walk_frame:[{walk_frame,manifest,to_idle,root_curve}]` supplies one immediate finite stop for every walk binding.
- `start_by_idle:{key:{manifest,walk_entry_frame,root_curve}}` supplies one finite start per idle variant.
- Each `root_curve` is ordered `[{time:[num,den],offset:[native_x,native_y]}]`; it starts at time0/offset0, ends at the exact clip duration and has strictly increasing times. The physical controller interpolates between these explicit cumulative offsets, scales them by display scale and limits incremental motion by real collision.

The adapter checks matching source canvas/pivot and exact PNG hashes at walk→stop→idle and idle→start→walk boundaries. It preserves all authored intermediate keys. A whole-actor draw bias survives stop/idle/start; optional walk contact targets include that bias. Final pixel draw origin rounds once while the collision root retains fractional precision. `stride` is explicit viewport pixels per walk cycle; it is not a measured anatomical stride.

Generic render checks:

```bash
xvfb-run -a godot --path . --rendering-method gl_compatibility --script capture_transitions.gd
python3 verify_transitions.py
xvfb-run -a godot --path . --rendering-method gl_compatibility --fixed-fps 60 --script capture_live.gd
python3 verify_transitions.py --records LIVE-CAPTURE-RECORDS.json --output LIVE-CAPTURE-VERIFICATION.json
```

Fixed-state transition capture samples every supplied clip pose at five fractions and two entry biases, assigning state in `_process` before rendering. Live capture injects real movement input and records runtime physics/state clocks without direct pose/root assignments. Source-pixel readbacks prove presentation, not art quality or foot anatomy.

Optional `--contacts /path/contacts.json --stance-lock` accepts one `frames` entry per walk binding. Flat episodes contain `flat:true`, `episode`, source `anchor:[x,y]`, `foot_mask`, `visible_foot_mask` and `ownership:{full_pixels,visible_pixels,occluded_pixels}`. Nonflat entries use `flat:false`. Visible masks must come from known compositing ownership, independently of RGB. `capture_contact.gd` and `measure_contact.py` compare actual raw/corrected full visible foot material samples, count occlusion and report within-pose versus across-pose changes separately. The correction translates one whole actor, never individual legs, and never establishes collision anatomy from target coordinates.
