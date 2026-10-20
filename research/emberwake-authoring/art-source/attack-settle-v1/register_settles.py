#!/usr/bin/env python3
"""Replay saved ImageGen settle paint with one fixed whole-grid registration.

No model call is made. Inputs, literal head masks and neighboring cels are local.
Use --output with a fresh directory. Each character's native cels are candidates,
not runtime replacements or a quality certification.
"""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

VIEWS = ["south", "east", "north", "west"]
BEFORE_MS = [60,70,55,55,65,105,580,580]
AFTER_MS = [60,70,55,55,65,35,35,35,580,580]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def context_cell(image, col, row):
    return image.crop((col*128,row*128,col*128+128,row*128+128))


def selected_at(frames, holds, tick):
    time = 0
    for frame, duration in zip(frames,holds):
        time += duration
        if tick < time:
            return frame
    return frames[-1]


def produce(character_dir, output):
    provenance = json.loads((character_dir / "input-provenance.json").read_text())
    raw_bytes = (character_dir / "raw-return.png").read_bytes()
    if sha(raw_bytes) != provenance["raw_png_sha256"]:
        raise ValueError("Raw model output no longer matches frozen generation")
    for ref in provenance["refs"]:
        if sha((character_dir.parent / ref["path"]).read_bytes()) != ref["sha256"]:
            raise ValueError("Actual generation input changed")
    if sha((character_dir / "literal-prompt.txt").read_bytes()) != provenance["literal_prompt_sha256"]:
        raise ValueError("Literal request changed")
    context_path = character_dir / provenance["offline_context"]["path"]
    if sha(context_path.read_bytes()) != provenance["offline_context"]["sha256"]:
        raise ValueError("Offline endpoint context changed")
    raw = Image.open(character_dir / "raw-return.png").convert("RGBA")
    if raw.size != (1254,1254):
        raise ValueError("This frozen registration expects the actual 1254-square return")
    # No individual bbox fitting, body scale adjustment, per-cel translation
    # or interpolated limb drawing. Exactly one whole-sheet nearest resample.
    transported = raw.resize((256,256),Image.Resampling.NEAREST)
    untreated_transport = transported.copy()
    # Both actual returns have a few distant background specks with alpha=1,
    # including cell-border texels. They are not clipped body geometry. Remove
    # exactly that 1/255 alpha noise; keep every alpha>=2 contour value intact.
    alpha1_removed = 0
    for yy in range(256):
        for xx in range(256):
            if transported.getpixel((xx,yy))[3] == 1:
                transported.putpixel((xx,yy),(0,0,0,0))
                alpha1_removed += 1
    guards = Image.open(character_dir / "guard-edit-target.png").convert("RGBA").resize((256,256),Image.Resampling.NEAREST)
    idles = Image.open(character_dir / "idle-endpoint-reference.png").convert("RGBA").resize((256,256),Image.Resampling.NEAREST)
    context = Image.open(context_path).convert("RGBA")
    head_plan = json.loads((character_dir / "head-protection.json").read_text())
    output.mkdir(parents=True)
    untreated_transport.save(output / "untreated-transported-sheet.png")
    transported.save(output / "transported-sheet.png")
    rendered_sheet = Image.new("RGBA",(256,256))
    triptychs = Image.new("RGBA",(3*384,4*418),(30,45,49,255))
    label = ImageDraw.Draw(triptychs)
    native_proof = Image.new("RGBA",(3*128,4*146),(30,45,49,255))
    native_label = ImageDraw.Draw(native_proof)
    views = []
    for row,view in enumerate(VIEWS):
        x,y = row%2*128,row//2*128
        generated = transported.crop((x,y,x+128,y+128))
        guard = guards.crop((x,y,x+128,y+128))
        idle = idles.crop((x,y,x+128,y+128))
        if guard.tobytes() != context_cell(context,5,row).tobytes() or idle.tobytes() != context_cell(context,6,row).tobytes():
            raise ValueError("Generation refs do not match frozen whole-attack endpoints")
        head = Image.new("L",(128,128))
        for yy,x0,x1 in head_plan["views"][view]["rows_y_x0_x1"]:
            ImageDraw.Draw(head).line((x0,yy,x1-1,yy),fill=255)
        # The guard's side-view fist partially occludes the jaw. Its broad head
        # crop can carry a detached old fingertip into a lowered-arm drawing.
        # The actual following idle supplies the known unobstructed same-view
        # head/neck paint, so no missing face anatomy is invented here.
        head_source = idle
        protected = generated.copy()
        protected.paste(head_source,(0,0),head)
        for difference in ImageChops.difference(protected,generated).split():
            if ImageChops.multiply(difference,ImageChops.invert(head)).getbbox() is not None:
                raise AssertionError("Protected composite changed pixels outside literal head mask")
        for difference in ImageChops.difference(protected,head_source).split():
            if ImageChops.multiply(difference,head).getbbox() is not None:
                raise AssertionError("Existing idle head pixels not retained exactly")
        border = sum(protected.getpixel((xx,yy))[3]>0 for xx,yy in
                     ([(xx,0) for xx in range(128)]+[(xx,127) for xx in range(128)]+
                      [(0,yy) for yy in range(1,127)]+[(127,yy) for yy in range(1,127)]))
        if border:
            raise AssertionError("Generated body touches native stage border")
        new_owned_changes = sum(protected.getpixel((xx,yy)) != guard.getpixel((xx,yy))
                                for yy in range(128) for xx in range(128) if head.getpixel((xx,yy)) == 0)
        if new_owned_changes < 250:
            raise AssertionError("Candidate does not contain substantial new body/limb paint")
        protected.save(output / (view+".png"))
        head.save(output / (view+"-head-mask.png"))
        rendered_sheet.paste(protected,(x,y))
        for col,(image,caption) in enumerate([(guard,"ORIGINAL GUARD"),(protected,"NEW SETTLE"),(idle,"EXISTING IDLE")]):
            triptychs.alpha_composite(image.resize((384,384),Image.Resampling.NEAREST),(col*384,row*418+34))
            label.text((col*384+5,row*418+8),view+" "+caption,fill="white")
            native_proof.alpha_composite(image,(col*128,row*146+18))
            native_label.text((col*128+2,row*146+3),view+" "+caption.split()[0],fill="white")
        before = [context_cell(context,col,row) for col in range(8)]
        after = before[:5]+[guard,protected,idle]+before[6:]
        boundaries = {0}
        for holds in [BEFORE_MS,AFTER_MS]:
            t=0
            for ms in holds:
                t+=ms
                boundaries.add(t)
        times = sorted(boundaries)
        frames,durations = [],[]
        for a,b in zip(times,times[1:]):
            pair = Image.new("RGBA",(512,282),(30,45,49,255))
            draw = ImageDraw.Draw(pair)
            for col,(sequence,holds,caption) in enumerate([(before,BEFORE_MS,"ORIGINAL"),(after,AFTER_MS,"CANDIDATE")]):
                pair.alpha_composite(selected_at(sequence,holds,a).resize((256,256),Image.Resampling.NEAREST),(col*256,26))
                draw.text((col*256+3,5),view+" "+caption+" %dms"%a,fill="white")
            frames.append(pair)
            durations.append(b-a)
        frames[0].save(output/(view+"-attack-before-after.apng"),save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=0,blend=0)
        views.append({"view":view,"guard_source_frame":13+row*28,"idle_source_frame":14+row*28,
                      "native_png_sha256":sha((output/(view+".png")).read_bytes()),
                      "native_rgba_sha256":sha(protected.tobytes()),"protected_head_pixels_exact":True,
                      "protected_head_source":"following same-view existing idle endpoint",
                      "outside_head_mask_equals_generated":True,"new_owned_rgba_changes_from_guard":new_owned_changes,
                      "border_alpha_pixels":border,"alpha_bbox":list(protected.getchannel("A").getbbox()),
                      "head_mask_sha256":sha((output/(view+"-head-mask.png")).read_bytes())})
    rendered_sheet.save(output/"four-settles.png")
    triptychs.convert("RGB").save(output/"guard-settle-idle-3x.png")
    native_proof.convert("RGB").save(output/"guard-settle-idle-native.png")
    receipt={"schema":"emberwake-generated-attack-settle/v1","character":character_dir.name,
             "raw_png_sha256":sha(raw_bytes),"raw_dimensions":list(raw.size),
             "actual_reference_hashes":[r["sha256"]for r in provenance["refs"]],
             "literal_prompt_sha256":provenance["literal_prompt_sha256"],
             "registration":{"operation":"Whole-grid nearest-neighbor resize","from":[1254,1254],"to":[256,256],"per_cell_translation":[0,0],"per_cell_bbox_fit":False},
             "alpha_cleanup":{"rule":"Only native texels with alpha==1 replaced by transparent RGBA zero","changed_native_texels":alpha1_removed,"alpha_ge_2_unchanged":True},
             "head_plan_sha256":sha((character_dir/"head-protection.json").read_bytes()),
             "views":views,"proposed_attack_ms":410,"proposed_gameplay_hit_ms":160,
             "old_final_guard_ms":105,"proposed_final_guard_settle_idle_ms":[35,35,35],
             "preview_loop_ms":1570,"quality_status":"Candidate only; independent motion and costume review pending",
             "limits":["Generated forearms often closer to idle than exact midpoint; guard-to-settle movement remains.","New body paint still changes some tunic shading; head protection does not certify complete costume identity.","No runtime manifest, attack events or balance was changed; previews show the proposed timing only."]}
    (output/"RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    if args.output.exists():
        p.error("Output directory must be fresh")
    here=Path(__file__).resolve().parent
    receipts=[produce(here/name,args.output/name) for name in ["lyra","brann"]]
    print(json.dumps({"characters":[r["character"]for r in receipts],"native_cels":8,"head_mask_exact":True,"stage_border_alpha_pixels":0,"quality_status":"Candidate review pending"}))


if __name__=="__main__":
    main()
