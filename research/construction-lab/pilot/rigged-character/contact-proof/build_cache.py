"""Export measured held sole table only when actual proof/source/cache hashes match."""
import hashlib,json
from pathlib import Path
from PIL import Image
HERE=Path(__file__).parent
BASE=HERE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((HERE/'contact-lock-report.json').read_text())
for name,value in proof['source_sha256'].items():
    if sha(BASE/name)!=value:raise ValueError(f'Stale proof source: {name}')
if sha(BASE/'foot_contact.gd')!=proof['policy_source_sha256']:raise ValueError('Stale helper')
raw=json.loads((HERE/'report.json').read_text())
out={'schema':'copper-scout-held-sole-cache/v1','source_sha256':proof['source_sha256'],'policy_sha256':proof['policy_source_sha256'],'view':'right','ground_boundary':170,'sole_row':169,'sole_offset':-9,'clips':{}}
for clip,ticks,stride in [('walk',60,24),('run',36,40)]:
    record=next(r for r in proof['routes']if r['clip']==clip)
    if not record['passes_0_5px_gate'] or record['full_body_pixel_failures']:raise ValueError('Failed rendered global lock')
    frames=[]
    for tick in range(ticks):
        frame={'tick':tick,'phase':tick/ticks,'sole_xmin':{},'boot_png_sha256':{}}
        for side in ['front','rear']:
            path=HERE/f'{clip}_{side}_tick{tick:03d}.png'
            bound=next(r for r in raw['routes']if r['clip']==clip and r['side']==side)
            if sha(path)!=bound['cache_sha256'][tick]:raise ValueError('Stale boot PNG')
            image=Image.open(path).convert('RGBA');xs=[x for x in range(192)if image.getpixel((x,169))[3]]
            frame['sole_xmin'][side]=min(xs)if xs else None;frame['boot_png_sha256'][side]=sha(path)
        body=HERE/f'{clip}_body_tick{tick:03d}.png'
        if sha(body)!=record['body_cache_sha256'][tick]:raise ValueError('Stale body PNG')
        image=Image.open(body).convert('RGBA');frame['whole_frame_rgba_sha256']=hashlib.sha256(image.tobytes()).hexdigest();frames.append(frame)
    out['clips'][clip]={'duration_ticks':ticks,'fps':60,'root_motion_px_per_cycle':stride,'frames':frames}
(HERE/'held-sole-cache.json').write_text(json.dumps(out,indent=2)+'\n')
historical=json.loads((HERE/'revision-7630ea2/held-sole-cache.json').read_text())
checks=[]
for clip in out['clips']:
    for new,old in zip(out['clips'][clip]['frames'],historical['clips'][clip]['frames']):
        checks.append({'clip':clip,'tick':new['tick'],'whole_rgba_unchanged':new['whole_frame_rgba_sha256']==old['whole_frame_rgba_sha256'],'boot_pngs_unchanged':new['boot_png_sha256']==old['boot_png_sha256']})
refresh={'schema':'copper-scout-contact-cache-refresh/v1','previous_source_sha256':historical['source_sha256'],'current_source_sha256':out['source_sha256'],'all96whole_frames_and192boot_PNGs_unchanged':all(c['whole_rgba_unchanged']and c['boot_pngs_unchanged']for c in checks),'checks':checks,'current_lock_report_sha256':sha(HERE/'contact-lock-report.json'),'current_baseline_report_sha256':sha(HERE/'report.json')}
(HERE/'cache-refresh.json').write_text(json.dumps(refresh,indent=2)+'\n')
print('Exported96 frame sole records; historical locomotion pixels unchanged:',refresh['all96whole_frames_and192boot_PNGs_unchanged'])
