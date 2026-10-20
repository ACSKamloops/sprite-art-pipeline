#!/usr/bin/env python3
"""Independently reconstruct generated candidates from raw texels + idle heads."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate",type=Path,required=True)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    checks=[]
    images=[]
    def check(condition,name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    # Explicit pixel-center nearest coordinates, independent of the producer's
    # Pillow.resize call. The same integer source map serves the whole grid.
    axis=[int((x+.5)*1254/256) for x in range(256)]
    for name in ["lyra","brann"]:
        folder=root/name
        provenance=json.loads((folder/"input-provenance.json").read_text())
        call=json.loads((folder/"tool-call.json").read_text())
        check((folder/"literal-prompt.txt").read_text().removesuffix("\n")==call["prompt"],name+" exact submitted prompt retained")
        check(digest(call["prompt"].encode())==provenance["actual_prompt_argument_sha256"],name+" actual prompt argument hash matches")
        check(call["mode"]=="built-in" and call["transparent_background"] is True,name+" actual built-in transparent edit recorded")
        for ref in provenance["refs"]:
            check(digest((root/ref["path"]).read_bytes())==ref["sha256"],name+" actual reference "+ref["role"]+" matches")
        raw=Image.open(folder/"raw-return.png").convert("RGBA")
        check(digest((folder/"raw-return.png").read_bytes())==provenance["raw_png_sha256"],name+" frozen raw generation matches")
        idle=Image.open(folder/"idle-endpoint-reference.png").convert("RGBA")
        plan=json.loads((folder/"head-protection.json").read_text())
        for index,view in enumerate(["south","east","north","west"]):
            result=Image.new("RGBA",(128,128))
            gx,gy=index%2*128,index//2*128
            for y in range(128):
                for x in range(128):
                    pixel=raw.getpixel((axis[gx+x],axis[gy+y]))
                    result.putpixel((x,y),(0,0,0,0) if pixel[3]==1 else pixel)
            for y,x0,x1 in plan["views"][view]["rows_y_x0_x1"]:
                for x in range(x0,x1):
                    # Nearest downsample of the exact 4x replicated source
                    # reference recovers the original native idle pixel.
                    result.putpixel((x,y),idle.getpixel(((gx+x)*4+2,(gy+y)*4+2)))
            file=args.candidate/name/(view+".png")
            actual=Image.open(file).convert("RGBA")
            check(actual.tobytes()==result.tobytes(),name+" "+view+" exact raw-map plus source-head replay")
            check(actual.size==(128,128),name+" "+view+" native stage preserved")
            alpha=actual.getchannel("A")
            edge=[alpha.getpixel((x,0))for x in range(128)]+[alpha.getpixel((x,127))for x in range(128)]+[alpha.getpixel((0,y))for y in range(128)]+[alpha.getpixel((127,y))for y in range(128)]
            check(max(edge)==0,name+" "+view+" no native border clipping")
            apng=Image.open(args.candidate/name/(view+"-attack-before-after.apng"))
            duration=0
            for f in range(apng.n_frames):
                apng.seek(f)
                duration+=apng.info["duration"]
            check(duration==1570,name+" "+view+" comparison retains exact1570ms clock")
            images.append({"character":name,"view":view,"png_sha256":digest(file.read_bytes()),"rgba_sha256":digest(actual.tobytes())})
    report={"passed":True,"assertions":len(checks),"checks":checks,"source_axis_map":axis,
            "images":images,"note":"Raw-pixel/head ownership, clipping and timing checks; independent art and actual game motion review pending."}
    if args.report:
        if args.report.exists():
            parser.error("Report must be a fresh path")
        args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"passed":True,"assertions":len(checks),"native_cels":len(images)}))


if __name__=="__main__":
    main()
