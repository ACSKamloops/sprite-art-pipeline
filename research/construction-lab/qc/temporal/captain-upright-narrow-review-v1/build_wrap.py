from pathlib import Path
from PIL import Image,ImageDraw
import subprocess
p=Path(__file__).resolve().parent;b=Path('/home/astra/projects/sprite-construction-lab-captain-techniques/pilot/captain-upright-narrow-v1/artifacts/audition-dense-in-place')
f=p/'decoded-next-cycle.png';subprocess.run(['ffmpeg','-y','-v','error','-ss','1.200','-i',str(b/'rgba-1x-normal.mp4'),'-frames:v','1',str(f)],check=True)
a=Image.open(p/'audition-dense-in-place/decoded/rgba-1x-normal/072.png').crop((96,80,352,336));z=Image.open(f).crop((96,80,352,336));o=Image.new('RGB',(1024,536),(38,43,49));o.paste(a.resize((512,512),Image.Resampling.NEAREST),(0,0));o.paste(z.resize((512,512),Image.Resampling.NEAREST),(512,0));ImageDraw.Draw(o).text((3,515),'selected1190ms -> decoded nextcycle1200ms',fill='white');o.save(p/'actual-wrap-2x.png')
