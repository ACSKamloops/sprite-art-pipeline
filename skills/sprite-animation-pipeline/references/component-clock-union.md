# Preserve component clocks when combining painted parts

Use this for separately painted body, equipment or effect tracks whose existing cycles share a period. A matched period does not establish that their poses belong together. Inspect opposing phases and intermediate combinations before building all media.

`scripts/union_component_clocks.py` takes explicitly looping frame manifests with positive rational holds and verified source-file hashes. It emits every union boundary and the active source position for each component. It does not interpolate paint, duplicate events, shift phase, mask, register, or infer hidden anatomy. Unequal periods reject; choose any retiming or phase offset separately and review that change explicitly.

```bash
python3 scripts/union_component_clocks.py \
  --track upper=/work/upper/manifest.json \
  --track lower=/work/lower/manifest.json \
  --output /work/new-component-schedule.json
```

The output names source files and pins their hashes; output must be new. A source frame may occupy several combined states while another component changes. For example,16×5/64s and30×1/24s produce44 combined states on192Hz,240ticks=1.25s. This preserves both original clocks. It does not mean44 newly painted poses or that the result needs to be slowed down. A1tick hold is5.208ms; verify actual movie/engine timing. Exact APNG delay fields do not guarantee browser playback of such short delays.

Construct each combined state from explicit masks/layer order. Retain sourceXY/RGBA witnesses and identify new occlusions. A “lower” owner may intentionally retain waist context; name that qualification instead of claiming a complete anatomical rig. In the demonstrated pilot, four opposing stills hid mistakes found when all component poses were isolated: upper owners included trouser wedges and lower owners retained old hand/coat edges. Correct those semantic owners against visible source paint before rendering the full union.

Inspect all combined states, successive pairs and the wrap at game scale on several backgrounds, then actual timed motion. Check hip seams, old-limb ghosts, material consistency, arm–leg coordination and whether different component update rates feel coherent. Independent clock verification cannot pass this art gate. The demonstrated44-state schedule has been checked against every240 source tick; its full artwork remains separately reviewed.

If correct owner removal exposes genuinely hidden body paint, keep the failed source-only baseline. Author the missing region explicitly on a separate underpaint layer, using a declared mask and known palette/sourceRGB donors where useful. Donor provenance proves color origin, not that the new arrangement was recovered. Check that every known visible source pixel and all protected parts remain unchanged; replay and undo the actual edit journal. Test affected neighboring component combinations, not only the original gap. In the demonstrated repair,98 authored waist pixels on three lower cels produced73 visible changes across four combined states. A local independent pixel gate passed; that did not establish full-motion approval.

Deliver original lower paint, authored underpaint and upper paint as separate editable layers. The44-state case was actually saved/reopened in LibreSprite with82 linked cels and all flattened alpha/visibleRGBA checked. Its native192Hz sidecar remains authoritative beside the editor's integer-millisecond preview. This proves editable exchange for those inputs, not an inferred anatomical rig or animation quality.

Test the runtime with these actual variable holds. Source resource values can be exact while live playback is wrong. A local Godot4.7.2 probe at192Hz with weights[1,239] wrapped seven times in about2.61s instead of two; the[120,120] control wrapped near1.25s and2.50s. This matches the failure class in the September17,2026 [confirmed upstream issue](https://github.com/godotengine/godot/issues/123572); the October3 [proposed fix](https://github.com/godotengine/godot/pull/124121/files) changes when duration scaling is evaluated. The proposal was not applied to the local binary. Keep the failed traces. Where needed, select frames from an explicit monotonic cumulative-hold clock and use that same clock for root motion/events, pause/resume and seeks. Verify actual presentations and wrap times separately from offline every-tick captures. Legitimately unpresented short states must still consume their intended time; skipping a long following hold is a different failure.
