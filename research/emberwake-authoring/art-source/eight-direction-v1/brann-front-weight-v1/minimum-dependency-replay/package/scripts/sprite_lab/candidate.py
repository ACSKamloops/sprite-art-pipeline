from PIL import Image
from .core import validate_project,render_cel,project_hash,cel_hash,_mask,require

def candidate_transaction(project,cel_id,image,mask,reason='Candidate patch through explicit mask'):
    validate_project(project);require(cel_id in project['cels'],'Unknown cel');image=image.convert('RGBA');require(image.size==(project['canvas']['width'],project['canvas']['height']),'Candidate must retain canvas dimensions');indices=_mask(project,mask);original=project['cels'][cel_id]['pixels'];rgba=list(image.getdata());baseline=list(render_cel(project,cel_id).getdata());require(all(rgba[i]==baseline[i]for i in range(len(rgba))if i not in indices),'Candidate RGBA changes outside mask')
    pixels=list(original);palette={tuple(color):i for i,color in reversed(list(enumerate(project['palette'])))};operations=[];next_index=len(project['palette'])
    for i in sorted(indices):
        color=rgba[i]
        if color not in palette:palette[color]=next_index;next_index+=1;operations.append({'op':'palette_add','rgba':list(color)})
        pixels[i]=original[i]if color==baseline[i]else palette[color]
    operations.append({'op':'candidate_patch','cel_id':cel_id,'mask':mask,'candidate_pixels':pixels,'expected_cel_sha256':cel_hash(project,cel_id)})
    return {'schema':'sprite-edit-transaction/v1','expected_project_sha256':project_hash(project),'reason':reason,'operations':operations}
