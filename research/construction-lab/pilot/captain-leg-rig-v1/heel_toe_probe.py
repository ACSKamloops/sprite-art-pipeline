"""Isolated source-attached hinge feasibility; never promotes a gait automatically."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,json,hashlib
import build
ROOT=Path(__file__).resolve().parent
PACK=ROOT/'dense-v22';OUT=ROOT/'heel-toe-feasibility-v22'
# Actual observed opaque sole pixels selected ONCE on the native rigid boot.
LANDMARKS={'right':{'toe':[63,220],'heel':[96,215]},'left':{'toe':[153,240],'heel':[180,231]}}
def main():
 if OUT.exists():raise ValueError('Refuse existing evidence')
 OUT.mkdir();rows=[];sheet=Image.new('RGBA',(1536,1064),(31,34,41,255));draw=ImageDraw.Draw(sheet)
 for li,(leg,land)in enumerate(LANDMARKS.items()):
  im=Image.open(PACK/'parts'/f'{leg}-boot.png').convert('RGBA');toe=land['toe'];heel=land['heel'];delta=[heel[j]-toe[j]for j in range(2)];length=math.hypot(*delta)
  for ci,(role,degrees)in enumerate([('heel',6),('flat',0),('toe',-6)]):
   pivot=land['heel']if role=='heel'else land['toe'];a=math.radians(degrees);render=build.transform(im,pivot,pivot,a);render.save(OUT/f'{leg}-{role}.png');actual_alpha=render.getchannel('A');p=actual_alpha.load();envelope=[]
   for x in range(256):
    ys=[y for y in range(256)if p[x,y]]
    if ys:envelope.append([x,max(ys)])
   # Proposed oblique straight support line through the manually identified points.
   # A rest violation rejects the floor annotation itself, rather than moving art.
   violation=max(((y-toe[1])*delta[0]-(x-toe[0])*delta[1])/length for x,y in envelope)
   rows.append({'leg':leg,'role':role,'degrees':degrees,'pivot_source_pixel':pivot,'pivot_source_RGBA':list(im.getpixel(tuple(pivot))),'proposed_floor_penetration_px':violation,'proposed_floor_gate_0_5':violation<=.5,'actual_RGBA_sha256':hashlib.sha256(render.tobytes()).hexdigest()})
   x=ci*512;y=li*532;sheet.alpha_composite(render.resize((512,512),Image.Resampling.NEAREST),(x,y+20));draw.text((x+8,y+4),f'{leg} {role} {degrees}deg; line violation {violation:.2f}px',fill='white')
 sheet.save(OUT/'hinge-comparison-2x.png');report={'schema':'captain-source-hinge-feasibility/v1','pack_manifest_sha256':hashlib.sha256((PACK/'manifest.json').read_bytes()).hexdigest(),'fixed_native_landmarks':LANDMARKS,'rows':rows,'promoted':False,'scope':'Actual sourceboot pixels rotated about fixed materialheel/toe, no perframefit/addedmarker. Proposed2Dfloor is REJECTED if rest or hinges penetrate. This is not an anatomical3Dfloor, gait proof or biomechanical roll approval. Keep flatv22 until projectedfloor/surfacecontact is authored convincingly.','palette_preserved':all(set(Image.open(OUT/f'{l}-{role}.png').convert('RGBA').getdata())<=set(Image.open(PACK/'parts'/f'{l}-boot.png').convert('RGBA').getdata())|{(0,0,0,0)}for l in LANDMARKS for role in ['heel','flat','toe'])};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print([(r['leg'],r['role'],round(r['proposed_floor_penetration_px'],2))for r in rows])
if __name__=='__main__':main()
