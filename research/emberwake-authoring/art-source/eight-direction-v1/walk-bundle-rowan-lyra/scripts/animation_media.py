from PIL import Image
import subprocess
from pathlib import Path
def emit_media(frames, path, scale=1):
 f=[im.resize((round(128*scale),round(128*scale)),Image.Resampling.NEAREST) for im in frames]
 # GIF cannot express 9/160 exactly. 6,5,6,6,5,6,5,6 centiseconds sums45.
 f[0].save(path.with_suffix('.gif'),save_all=True,append_images=f[1:],duration=[60,50,60,60,50,60,50,60],loop=0,disposal=2)
 # MP4 at160fps: each native exposure repeats9frames; durations exactly.45.
 bg=Image.new('RGB',f[0].size,(60,65,72))
 proc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{bg.width}x{bg.height}','-framerate','160','-i','-','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(path.with_suffix('.mp4'))],stdin=subprocess.PIPE)
 for _ in range(8):
  for cel in f:
   c=bg.copy();c.paste(cel,(0,0),cel)
   for __ in range(9):proc.stdin.write(c.tobytes())
 proc.stdin.close();assert proc.wait()==0
