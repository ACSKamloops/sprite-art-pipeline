#!/usr/bin/env python3
"""Decode a retained native H3 video with PTS; create explicitly local previews.

No generation, background removal, palette mapping or temporal repair. Eight
samples are a review derivative, never a recovered PixelLab frame sampler.
"""
import argparse
from bisect import bisect_right
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_frames(times, end, count):
    """Select the actually displayed source frame at each half-open sample time."""
    if not times or count < 1 or any(b <= a for a, b in zip(times, times[1:])) or end <= times[-1]:
        raise ValueError("Monotonic source presentation times and a positive final hold are required")
    return [(times[0] + (end-times[0])*i/count,
             max(0, bisect_right(times, times[0] + (end-times[0])*i/count)-1)) for i in range(count)]


def analyze(run):
    video = run / "native-video.mp4"
    media = run / "media-review"
    media.mkdir(exist_ok=False)
    native = media / "decoded-native"; native.mkdir()
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-show_frames", "-show_format", "-of", "json", str(video)], capture_output=True, check=True, timeout=60)
    (media / "ffprobe.json").write_bytes(p.stdout)
    probe = json.loads(p.stdout)
    stream = probe["streams"][0]
    frames = [f for f in probe["frames"] if f.get("media_type") == "video"]
    tb = Fraction(stream["time_base"])
    times = [int(f.get("best_effort_timestamp", f.get("pts")))*tb for f in frames]
    duration_ticks = frames[-1].get("duration", frames[-1].get("pkt_duration"))
    last_hold = int(duration_ticks)*tb if duration_ticks is not None else times[-1]-times[-2]
    end = times[-1] + last_hold
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-threads", "8", "-i", str(video), "-map", "0:v:0", "-fps_mode", "passthrough", "-start_number", "0", "-threads", "8", str(native / "frame-%06d.png")], check=True, timeout=180)
    files = sorted(native.glob("frame-*.png"))
    if len(files) != len(frames):
        raise ValueError("Decoded PNG count differs from probed video-frame count")
    entries = []
    for i, (f, t) in enumerate(zip(files, times)):
        entries.append({"index": i, "file": str(f.relative_to(media)), "pts_ticks": int(frames[i].get("best_effort_timestamp", frames[i].get("pts"))), "pts_seconds_exact": str(t), "time_base": str(tb), "sha256": sha(f)})
    chosen = select_frames(times, end, 8)
    sample = media / "local-eight-samples"; sample.mkdir()
    sample_rows = []
    for i, (target, idx) in enumerate(chosen):
        with Image.open(files[idx]) as im:
            im.convert("RGBA").resize((256, 256), Image.Resampling.NEAREST).save(sample / f"sample-{i:02d}.png")
        sample_rows.append({"sample": i, "target_seconds_exact": str(target), "native_frame_index": idx, "native_pts_seconds_exact": str(times[idx]), "file": f"local-eight-samples/sample-{i:02d}.png", "sha256": sha(sample/f"sample-{i:02d}.png")})
    # All frames are shown in chronological pages, without independently recentering them.
    contacts = []
    for start in range(0, len(files), 16):
        sheet = Image.new("RGB", (1024, 4*282), "#171c28")
        draw = ImageDraw.Draw(sheet)
        for n, f in enumerate(files[start:start+16]):
            with Image.open(f) as im:
                im = im.convert("RGB").resize((256, 256), Image.Resampling.NEAREST)
                x=(n%4)*256; y=(n//4)*282
                sheet.paste(im, (x, y+26)); draw.text((x+7,y+7), f"frame {start+n:03d} | {float(times[start+n]):.3f}s", fill="white")
        name=f"chronological-{start//16:02d}.png";sheet.save(media/name);contacts.append(name)
    selected_sheet = Image.new("RGBA", (8*256, 282), "#171c28"); draw=ImageDraw.Draw(selected_sheet)
    gifs=[]
    for i, (_, idx) in enumerate(chosen):
        with Image.open(sample/f"sample-{i:02d}.png") as im:
            selected_sheet.paste(im, (i*256,26));gifs.append(im.convert("RGB"))
        draw.text((i*256+6,8), f"sample {i}; native frame {idx}", fill="white")
    selected_sheet.save(media/"eight-samples.png")
    # Preview hold is explicitly independent, not inferred provider/sprite timing.
    gifs[0].save(media/"eight-samples-preview.gif", save_all=True, append_images=gifs[1:], duration=125, loop=0, optimize=False)
    report = {"version":1,"native_video_sha256":sha(video),"codec":stream.get("codec_name"),"native_dimensions":[stream["width"],stream["height"]],"pixel_format":stream.get("pix_fmt"),"reported_average_frame_rate":stream.get("avg_frame_rate"),"time_base":str(tb),"decoded_frame_count":len(files),"last_hold_source":"probed frame duration" if duration_ticks is not None else "local preview fallback: last observed PTS delta", "presentation_end_seconds_exact":str(end),"native_frames":entries,"local_samples":{"policy":"eight evenly spaced half-open presentation times; choose displayed native frame; whole-canvas nearest resize to256; no reference prepending, masking, quantization or repair", "is_pixellab_conversion":False,"inferred_sprite_fps":None,"preview_gif_hold_ms":125,"samples":sample_rows},"chronological_pages":contacts,"aesthetic_acceptance":False,"alpha_note":"No output alpha reconstruction attempted; inspect native pixel format separately"}
    write_json(media/"MANIFEST.json",report)
    html='''<!doctype html><meta charset="utf-8"><title>Original RPG hero — H3 motion pilot</title>
<style>body{background:#171c28;color:#eef1f7;font:16px system-ui;margin:30px}img{image-rendering:pixelated;max-width:100%}video{width:512px;max-width:100%;display:block}section{display:flex;gap:30px;align-items:start;flex-wrap:wrap}a{color:#8cc8ff}p{max-width:950px}</style>
<h1>Original RPG hero: H3 walking pilot</h1><p>Native H3 output and explicitly local inspection derivatives. No PixelLab checkpoint/conversion parity or production quality acceptance is claimed.</p><section><div><h2>Conditioning sprite</h2><img src="../source.png" width="256"></div><div><h2>Original returned video</h2><video controls loop src="../native-video.mp4"></video></div><div><h2>Eight-sample diagnostic loop</h2><img src="eight-samples-preview.gif" width="256"><p>125ms per selected frame is a local preview clock.</p></div></section><h2>Selected frame progression</h2><img src="eight-samples.png"><p><a href="MANIFEST.json">Full PTS/frame mapping and hashes</a></p>'''
    (media/"index.html").write_text(html)
    return {"frames":len(files),"dimensions":report["native_dimensions"],"codec":report["codec"],"time_base":str(tb),"presentation_end_seconds_exact":str(end),"review":str(media/"index.html")}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("run",type=Path)
    print(json.dumps(analyze(parser.parse_args().run.resolve())))
