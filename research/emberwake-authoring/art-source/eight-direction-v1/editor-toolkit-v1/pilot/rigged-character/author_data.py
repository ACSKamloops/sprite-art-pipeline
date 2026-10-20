"""Author shared design/pose data. No per-frame raster redraw or AI asset."""
import json,argparse,copy
from pathlib import Path
HERE=Path(__file__).parent
parser=argparse.ArgumentParser(description='Explicit initializer, never a routine build step')
parser.add_argument('--force-bootstrap',action='store_true',help='Explicitly replace existing authored JSON; normally refused')
args=parser.parse_args()
if not args.force_bootstrap and any((HERE/name).exists()for name in ['design.json','clips.json']):
    parser.error('Authored JSON already exists. Refusing to overwrite edits; this initializer is not a build step.')
palette={'ink':'152C37','cloth':'253C4C','cloth_light':'426073','teal':'237F83','teal_light':'4AB5AE','teal_dark':'19545E','copper':'B96D43','copper_light':'EDAA70','copper_dark':'724737','cream':'F0E4C6','cream_shadow':'C5B697','skin':'D9AB83','skin_shadow':'A66D55','eye':'F8D795'}
design={'schema':'copper-scout-design/v1','name':'Copper Scout','canvas':[192,192],'ground_y':170,'foot_anchor_y':166,'palette':palette,'dimensions':{'upper_leg':29,'lower_leg':28,'upper_arm':22,'lower_arm':23,'leg_widths':[7.5,6,4],'arm_widths':[6,5.5,3.5],'joint_curve_radius':5},'anchors':{'pelvis':[96,116],'head_offset':[2,-49],'front_shoulder':[9,-25],'rear_shoulder':[-10,-24],'front_hip':[5,0],'rear_hip':[-5,0]},'polygons':{
'boot_outer':[[-8,-8],[4,-8],[6,-3],[13,-1],[15,2],[13,4],[-9,4],[-10,1]],'boot_inner':[[-6,-6],[2,-6],[4,-1],[11,0],[12,2],[-7,2]],'boot_plate':[[-5,-7],[3,-7],[4,-3],[-4,-2]],
 'torso_outer':[[-12,-31],[5,-35],[15,-28],[12,-10],[15,5],[4,9],[-12,7],[-15,-8]],'torso_inner':[[-10,-28],[5,-32],[12,-26],[9,-9],[12,3],[3,6],[-10,4],[-12,-8]],'tunic_light':[[3,-31],[11,-26],[8,-9],[11,3],[5,5],[2,-11]],'belt':[[-13,-1],[12,-1],[13,4],[-13,4]],
 'hood_outer':[[-18,-15],[-10,-25],[7,-24],[18,-16],[20,1],[13,16],[-4,20],[-17,11],[-22,-2]],'hood_inner':[[-16,-13],[-9,-22],[6,-21],[15,-14],[17,1],[10,13],[-4,16],[-14,9],[-18,-2]],'face':[[2,-12],[13,-10],[16,-3],[21,0],[16,4],[15,11],[8,15],[0,10],[-1,-3]],'helmet_brim':[[-13,-16],[7,-19],[17,-12],[17,-8],[-12,-10]],'hood_highlight':[[-15,-10],[-7,-20],[-2,-20],[-8,-8],[-10,6],[-15,4]],
 'scarf_neck':[[-14,-36],[12,-36],[16,-29],[9,-25],[-13,-27],[-18,-31]],'scarf_tail':[[-10,-32],[-21,-30],[-30,-23],[-21,-22],[-17,-27],[-9,-26]],
 'shoulder_outer':[[-8,-6],[1,-10],[9,-5],[10,3],[2,7],[-7,4]],'shoulder_inner':[[-5,-5],[1,-7],[6,-4],[7,1],[2,4],[-4,2]],'hand_closed':[[-4,-4],[3,-5],[7,-2],[7,3],[2,5],[-4,3]],'hand_open':[[-4,-3],[1,-4],[7,-6],[9,-5],[5,-1],[10,0],[10,2],[4,2],[6,5],[4,6],[-2,4],[-5,1]],
 'sword_blade':[[4,-3],[31,-3],[39,0],[31,3],[4,3]],'sword_highlight':[[5,-2],[30,-2],[36,0],[5,0]],'sword_guard':[[-1,-7],[3,-7],[5,-4],[5,4],[3,7],[-1,7]],'sword_grip':[[-8,-2],[0,-2],[0,2],[-8,2]],'blaster_body':[[-8,-10],[13,-10],[21,-6],[21,-1],[6,0],[1,6],[-4,6],[-4,-3],[-10,-3]],'blaster_panel':[[-6,-8],[12,-8],[17,-5],[17,-3],[4,-3]],'blaster_grip':[[-3,-1],[3,-1],[1,7],[-4,7]]},'support_matrix':{'right':{'authored':True,'clips':'all12'},'left':{'authored':False,'mirror_of':'right','limitations':'Equipment handedness mirrors; no independent left anatomy.'},'front':{'supported':False},'back':{'supported':False}},'construction':'Original reusable vector polygons and continuous polygon strips; no AI/per-frame redraw, no Skeleton2D skinning claim.','quality_status':'technical_art_pilot_requires_review'}
D={'pelvis':[96,116],'lean':0,'front_foot':[105,166],'rear_foot':[87,166],'front_hand':[128,110],'rear_hand':[80,111],'weapon_angle':.55,'head_tilt':0}
def knots(*pairs):return [[t,copy.deepcopy(v)]for t,v in pairs]
def make(ticks,loop=False,equipment='none',events=(),tracks=None,**kwargs):return {'duration_ticks':ticks,'loop':loop,'equipment':equipment,'events':[{'tick':t,'type':kind}for t,kind in events],'interpolation':'smoothstep','defaults':copy.deepcopy(D),'tracks':tracks or{},**kwargs}
clips={}
clips['idle']=make(90,True,tracks={'pelvis':knots((0,[96,116]),(.5,[96,115]),(1,[96,116])),'front_hand':knots((0,[128,110]),(.5,[129,109]),(1,[128,110]))})
clips['walk']=make(60,True,gait={'stance_fraction':.5,'root_motion_px_per_cycle':24,'lift_px':7,'bob_px':1.2,'arm_swing_px':6},events=[(0,'front_step'),(30,'rear_step')])
clips['run']=make(36,True,gait={'stance_fraction':.38,'root_motion_px_per_cycle':40,'lift_px':14,'bob_px':3,'arm_swing_px':13},tracks={'lean':knots((0,.13),(1,.13))},events=[(0,'front_step'),(18,'rear_step')])
clips['slash']=make(54,equipment='sword',events=[(0,'anticipation'),(21,'strike_pose'),(31,'recovery')],tracks={
'pelvis':knots((0,[96,116]),(.26,[92,117]),(.42,[107,118]),(.53,[108,118]),(.8,[100,116]),(1,[96,116])),
'lean':knots((0,0),(.26,-.18),(.42,.23),(.53,.18),(1,0)),
'front_hand':knots((0,[128,110]),(.26,[96,70]),(.39,[139,85]),(.48,[143,95]),(.58,[136,117]),(1,[128,110])),
'rear_hand':knots((0,[80,111]),(.26,[80,103]),(.42,[93,110]),(1,[80,111])),
'front_foot':knots((0,[105,166]),(.3,[114,166]),(.6,[114,166]),(1,[105,166])),
'rear_foot':knots((0,[87,166]),(.3,[82,166]),(.45,[85,163]),(.67,[87,166]),(1,[87,166])),
'weapon_angle':knots((0,.55),(.26,-2.0),(.39,-.35),(.48,.2),(.6,1.05),(1,.55))})
clips['thrust']=make(48,equipment='sword',events=[(0,'anticipation'),(17,'thrust_pose'),(25,'recovery')],tracks={
'pelvis':knots((0,[96,116]),(.22,[91,118]),(.38,[107,119]),(.53,[107,119]),(1,[96,116])),
'lean':knots((0,0),(.22,-.12),(.38,.17),(.53,.17),(1,0)),
'front_hand':knots((0,[126,108]),(.22,[112,105]),(.36,[145,103]),(.53,[145,103]),(1,[126,108])),
'front_foot':knots((0,[105,166]),(.34,[117,166]),(.7,[117,166]),(1,[105,166])),
'weapon_angle':knots((0,.1),(.22,-.05),(.36,0),(.7,0),(1,.1))})
clips['shoot']=make(48,equipment='blaster',events=[(0,'aim'),(18,'projectile_emit'),(22,'recoil'),(32,'recovery')],tracks={
'front_hand':knots((0,[125,108]),(.28,[136,99]),(.37,[139,99]),(.46,[134,97]),(.64,[139,99]),(1,[125,108])),
'rear_hand':knots((0,[80,111]),(.3,[124,105]),(.62,[125,105]),(1,[80,111])),
'lean':knots((0,0),(.3,.1),(.46,-.07),(.64,.06),(1,0)),
'weapon_angle':knots((0,.3),(.3,0),(.46,-.12),(.64,0),(1,.3))})
clips['charge']=make(90,True,equipment='sword',events=[(0,'charge_begin'),(60,'charge_ready')],tracks={'pelvis':knots((0,[96,119]),(.5,[96,118]),(1,[96,119])),'front_hand':knots((0,[120,100]),(.5,[120,98]),(1,[120,100])),'weapon_angle':knots((0,-1.05),(1,-1.05))})
clips['cast']=make(72,events=[(0,'anticipation'),(29,'cast_emit'),(44,'sustain'),(57,'recovery')],hand_state='open',tracks={
'front_hand':knots((0,[126,110]),(.23,[112,76]),(.4,[136,83]),(.61,[137,84]),(1,[126,110])),
'rear_hand':knots((0,[80,111]),(.23,[102,109]),(.61,[107,111]),(1,[80,111])),
'lean':knots((0,0),(.23,-.08),(.4,.09),(.61,.09),(1,0))})
clips['hurt']=make(36,events=[(0,'impact_pose'),(10,'recoil'),(24,'recover')],tracks={'pelvis':knots((0,[96,116]),(.15,[89,118]),(.45,[91,118]),(1,[96,116])),'lean':knots((0,0),(.15,-.2),(.45,-.14),(1,0)),'front_hand':knots((0,[128,110]),(.15,[111,105]),(.45,[112,107]),(1,[128,110])),'head_tilt':knots((0,0),(.15,-.13),(1,0))})
fallen={'pelvis':[101,147],'lean':-1.27,'front_hand':[74,156],'rear_hand':[111,155],'front_foot':[139,166],'rear_foot':[113,166],'head_tilt':-.1}
clips['knockdown']=make(66,events=[(0,'impact'),(27,'fall'),(48,'floor_settle')],tracks={k:knots((0,D.get(k,v)),(.25,D.get(k,v)),(.65,v),(.82,v),(1,v))for k,v in fallen.items()})
clips['recover']=make(78,events=[(0,'floor_start'),(23,'hand_support'),(48,'stand'),(70,'settle')],tracks={k:knots((0,v),(.2,v),(.55,{'pelvis':[95,131],'lean':-.38,'front_hand':[119,141],'rear_hand':[83,139],'front_foot':[112,166],'rear_foot':[91,166],'head_tilt':0}[k]),(.85,D.get(k,0)),(1,D.get(k,0)))for k,v in fallen.items()})
clips['celebrate']=make(90,True,tracks={'front_hand':knots((0,[124,65]),(.45,[127,58]),(.75,[124,64]),(1,[124,65])),'rear_hand':knots((0,[76,72]),(.45,[73,66]),(.75,[76,71]),(1,[76,72])),'pelvis':knots((0,[96,116]),(.45,[96,114]),(1,[96,116]))})
# Revision 2: taller leg reach beneath the same coat, authored weight changes.
design['dimensions'].update(upper_leg=30,lower_leg=30)
design['anchors'].update(pelvis=[96,108],body_offset=[0,8],head_offset=[2,-41],front_shoulder=[9,-17],rear_shoulder=[-10,-16])
D['pelvis']=[96,108]
for spec in clips.values():
    spec['defaults']['pelvis']=[96,108]
    if 'pelvis' in spec['tracks']:
        for knot in spec['tracks']['pelvis']:knot[1][1]-=8
clips['walk']['gait'].update(lift_px=10,bob_px=1.2,arm_swing_px=12,hand_drop_px=22,body_sway_radians=.025)
clips['run']['gait'].update(arm_swing_px=18,hand_drop_px=20,pelvis_drop_px=3,body_sway_radians=.025)
clips['slash']['tracks'].update(
 pelvis=knots((0,[96,108]),(.26,[88,113]),(.42,[112,113]),(.58,[116,115]),(.78,[104,110]),(1,[96,108])),
 lean=knots((0,0),(.26,-.22),(.42,.34),(.58,.42),(.78,.16),(1,0)),
 front_hand=knots((0,[128,110]),(.26,[90,68]),(.39,[144,83]),(.48,[147,99]),(.6,[137,122]),(.78,[132,124]),(1,[128,110])),
 rear_hand=knots((0,[80,111]),(.26,[75,106]),(.42,[94,117]),(.6,[102,122]),(1,[80,111])),
 front_foot=knots((0,[105,166]),(.26,[108,164]),(.39,[124,166]),(.65,[124,166]),(1,[105,166])),
 rear_foot=knots((0,[87,166]),(.26,[82,166]),(.55,[86,166]),(.78,[87,166]),(1,[87,166])),
 weapon_angle=knots((0,.55),(.26,-2),(.39,-.4),(.48,.25),(.6,1.25),(.78,1.1),(1,.55)))
clips['cast']['tracks'].update(
 pelvis=knots((0,[96,108]),(.23,[92,111]),(.4,[103,110]),(.61,[103,110]),(1,[96,108])),
 front_hand=knots((0,[126,110]),(.23,[108,67]),(.4,[140,77]),(.61,[141,78]),(1,[126,110])),
 rear_hand=knots((0,[80,111]),(.23,[82,82]),(.4,[100,83]),(.61,[101,84]),(1,[80,111])),
 lean=knots((0,0),(.23,-.14),(.4,.17),(.61,.17),(1,0)))
clips['hurt']['tracks'].update(
 pelvis=knots((0,[96,108]),(.15,[82,113]),(.45,[85,112]),(.75,[92,110]),(1,[96,108])),
 lean=knots((0,0),(.15,-.32),(.45,-.24),(.75,-.08),(1,0)),
 front_hand=knots((0,[128,110]),(.15,[105,101]),(.45,[108,103]),(1,[128,110])),
 rear_hand=knots((0,[80,111]),(.15,[68,116]),(.45,[73,116]),(1,[80,111])),
 front_foot=knots((0,[105,166]),(.15,[96,166]),(.45,[96,166]),(1,[105,166])),
 rear_foot=knots((0,[87,166]),(.15,[77,166]),(.45,[79,166]),(1,[87,166])),
 head_tilt=knots((0,0),(.15,-.18),(.45,-.13),(1,0)))
clips['celebrate']['tracks']['pelvis']=knots((0,[96,108]),(.45,[96,106.5]),(1,[96,108]))
# Grounded fall/recovery repair: explicit mass and palm support, no whole-sprite shift.
design['anchors']['scarf_tail_pivot']=[-10,-32]
D.update(front_hand_angle=-.130769044160843,rear_hand_angle=2.94425415992737,scarf_tail_angle=0)
for name in ['knockdown','recover']:clips[name]['defaults'].update(front_hand_angle=D['front_hand_angle'],rear_hand_angle=D['rear_hand_angle'],scarf_tail_angle=0)
rest={'front_hand_angle':0,'rear_hand_angle':0,'scarf_tail_angle':.1,'pelvis':[101,154.7],'lean':-1.45,'front_hand':[72,164.8],'rear_hand':[111,164.8],'front_foot':[139,166],'rear_foot':[113,166],'head_tilt':-.1}
clips['knockdown']['tracks']={k:knots((0,D.get(k,v)),(.15,D.get(k,v)),(.68,v),(.82,v),(1,v))for k,v in rest.items()}
clips['recover']['tracks']={k:knots((0,v),(.18,v),(.4,{'front_hand_angle':0,'rear_hand_angle':0,'scarf_tail_angle':-.85,'pelvis':[102,141],'lean':-.85,'front_hand':[103,164.8],'rear_hand':[85,164.8],'front_foot':[139,166],'rear_foot':[113,166],'head_tilt':-.05}[k]),(.65,{'front_hand_angle':1,'rear_hand_angle':1,'scarf_tail_angle':-.35,'pelvis':[103,125],'lean':-.35,'front_hand':[126,138],'rear_hand':[87,136],'front_foot':[123,166],'rear_foot':[99,166],'head_tilt':0}[k]),(.9,D.get(k,0)),(1,D.get(k,0)))for k,v in rest.items()}
(HERE/'design.json').write_text(json.dumps(design,indent=2)+'\n');(HERE/'clips.json').write_text(json.dumps({'schema':'copper-scout-clips/v1','fps':60,'phase_unit':'normalized','clips':clips,'event_scope':'Authored visual landmarks/hooks, not native gameplay damage windows. Projectile/magic FX rendered separately.'},indent=2)+'\n')
