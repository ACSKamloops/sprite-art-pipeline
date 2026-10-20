# Frozen Rowan NE03 source/editor package

This package reproduces the exact frozen03 transition PNG and preserves the seven current selected Rowan northeast control cels. It adds no artwork and does not establish normal-speed, engine or gameplay acceptance. The source experiment remains unchanged.

`projects/final.json` is an editable eight-cel **flattened composite** project. `exchange/tool-reopened.aseprite` is the actual LibreSprite-saved/reopened native file. Preserve `exchange/rowan-ne-final.aseprite.sprite-lab.json` and `exchange/RATIONAL-CLOCK.json` beside the native exchange: original9/160s holds and .45s loop are authoritative. Native millisecond holds are[56,57,56,56,56,57,56,56], a qualified preview totaling450ms.

The upstream visible source parts, literal owners, source-coordinate maps, eleven source seam-underlap texels, nine natural opposite-leg occlusions and the exact four-pixel sole recipe are under `retained-source/`. This is retained raster construction, not a fully layered anatomical rig. Only the necessary current inputs, maps, components and local toolkit dependencies were retained; historical failed trials and review media were not copied.

The two actual editor transactions are:

1. Import the completed-owner03 pose **before** the sole cleanup through its458-pixel literal source/target owner. Both project and cel hashes are guarded.
2. Apply the frozen sole cleanup: erase(66,111),(67,111),(73,111), then paint(69,110) with source03(70,111), RGBA[21,6,1,165]. A no-op candidate guard supplies the strict same-cel precondition before the actual eraser/pencil operations in this one atomic transaction. Its only composited changes are the four declared coordinates.

`projects/initial.json`, `after-import.json`, `final.json`, both transactions/receipts and the actual journal are retained. Both undo steps, both redo steps and journal replay pass. Seven negative checks reject stale project/cel hashes, outside-owner candidate pixels and an outside-mask sole erasure; every rejection leaves both project and history unchanged, including tests after staged palette mutations.

Independent literal-map replay reconstructs the pre-sole and final03 exactly without importing the original producer. All eight source and editor RGBA/PNG outputs match the frozen final inputs. All other seven cel index arrays remain exact. The toolkit's generic `exports/` uses its own PNG compression settings; decoded RGBA matches, while `editor-render/` preserves the exact frozen PNG bytes.

Actual LibreSprite batch commands opened/saved, reopened/saved and rendered the project twice. Both actual sheets and saved native cel data match all eight final RGBA images. Sidecar reimport reproduces the entire final project hash. Raw tool sheet encoding remains untouched; cropped renders encoded with the frozen PNG writer match all eight final PNG bytes. No approved pixel was changed to accommodate the tool.

See `verification/EDITOR-RECEIPT.json`, `verification/NATIVE-RECEIPT.json`, `INPUTS.json` and `INTAKE.md` for exact commands, hashes and replay. No model call, canonical/game edit, new bank art or score claim is part of this package.
