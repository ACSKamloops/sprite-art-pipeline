"""Measured CMU ankle→ball sagittal direction; not recovered sole contact."""
import argparse, hashlib, json, math
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():raise FileExistsError('Preserve measurements')
a.output.mkdir(parents=True);data=json.loads(a.source.read_text());rows=[]
for side,heel,stance in [('r',33,78),('l',98,82)]:
    for offset in range(stance+1):
        index=(heel+offset)%130;frame=data['frames'][index]
        # Acclaim points store segment ends: tibia-end is ankle; foot-end is ball.
        ankle=frame['points_m'][side+'tibia'];ball=frame['points_m'][side+'foot']
        delta=[ball[i]-ankle[i]for i in range(3)]
        rows.append({'side':side,'cycle_index':index,'stance_offset':offset,'declared_stance_fraction':offset/stance,'ankle_height_m':ankle[1],'ankle_to_ball_vector_m':delta,'sagittal_direction_degrees':math.degrees(math.atan2(delta[1],delta[2]))})
receipt={'state':'CAPTURED_BONE_DIRECTION_MEASUREMENT_NOT_SHOE_PHYSICS','source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'coordinate_system':'CMU Y-up,+Zforward in this selectedwalk; pitch atan2(verticalY,forwardZ)','episode_bounds':'R33/78samples;L98/82samples from separately inferred prototypeepisodes, not native measuredcontactflags','rows':rows,'limits':['Ankle-to-ball bone anatomically descends even when bare sole is flat; raw angle cannot directly drive a horizontal boot sole','A flat reference and target rest basis must be calibrated explicitly','Capture was cyclic channel conditioned with declared10.732degree max toe correction; these are not untouched originalchannels','End-foot direction roughly-68/-66degrees contrasts with authored18degree toeoff, but target animation must be rendered/reviewed again','No foot-force, shoe-collision or animation approval']}
(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
summary = {}
for side in ['r', 'l']:
    offsets = [0, 10, 40, 64, 78 if side == 'r' else 82]
    summary[side] = [
        {key: row[key] for key in ['stance_offset', 'sagittal_direction_degrees', 'ankle_height_m']}
        for row in rows if row['side'] == side and row['stance_offset'] in offsets
    ]
print(json.dumps(summary))
