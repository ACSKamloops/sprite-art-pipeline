"""Actual sourceUV feature-domain pass through the same rig/cameras, with no indirect illumination."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;scene=bpy.context.scene
marks=json.loads((ROOT/'descriptor-before.json').read_text())['marks']+json.loads((ROOT/'descriptor-after.json').read_text())['marks']
for mat in bpy.data.materials:
 nodes=mat.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');em=nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(0,0,0,1);mat.node_tree.links.new(em.outputs[0],out.inputs[0])
 if 'Bow' in mat.name:continue
 uv=nodes.new('ShaderNodeTexCoord');last=None
 for mark in marks:
  sub=nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(*mark['center'],0);mat.node_tree.links.new(uv.outputs['UV'],sub.inputs[0])
  scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1/mark['radius'][0],1/mark['radius'][1],0);mat.node_tree.links.new(sub.outputs[0],scale.inputs[0])
  length=nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';mat.node_tree.links.new(scale.outputs[0],length.inputs[0]);mask=nodes.new('ShaderNodeMath');mask.operation='LESS_THAN';mask.inputs[1].default_value=1;mat.node_tree.links.new(length.outputs['Value'],mask.inputs[0])
  if last is not None:
   union=nodes.new('ShaderNodeMath');union.operation='MAXIMUM';mat.node_tree.links.new(last,union.inputs[0]);mat.node_tree.links.new(mask.outputs[0],union.inputs[1]);last=union.outputs[0]
  else:last=mask.outputs[0]
 mat.node_tree.links.new(last,em.inputs[0])
scene.cycles.max_bounces=0;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0
out=ROOT/'feature-masks';out.mkdir(exist_ok=False)
views={'front':(0,-8,3.15),'right':(-8,0,3.15),'back':(0,8,3.15),'left':(8,0,3.15)}
for view,loc in views.items():
 scene.camera.location=loc;scene.camera.rotation_euler=(Vector((0,0,1.45))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
 for i,f in enumerate([0,10,20]):scene.frame_set(f);scene.render.filepath=str(out/f'{view}-{i}.png');bpy.ops.render.render(write_still=True)
