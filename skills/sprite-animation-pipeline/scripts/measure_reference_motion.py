"""Source-bound motion measurements. Numbers describe evidence, never an art grade."""
from pathlib import Path
from fractions import Fraction
import argparse,hashlib,json,math
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def observed(sample):
    return sample is not None and sample.get('xy') is not None and sample.get('visible',True)

def stance_fit(phases,points,direction,height):
    """Conditional boundary fit f(phi)+direction*L*phi. Not recovered world motion."""
    x=np.asarray(phases,dtype=float);p=np.asarray(points,dtype=float)
    d=np.asarray(direction,dtype=float);assert len(x)>=3 and p.shape==(len(x),2)
    assert np.linalg.norm(d)>0 and height>0
    d/=np.linalg.norm(d);along=p@d
    slope,intercept=np.polyfit(x,along,1);L=-float(slope)
    world=p+x[:,None]*L*d
    residual=world-world.mean(axis=0)
    return {'hypothesized_direction_unit':d.tolist(),'fitted_root_pixels_per_cycle':L,
            'fit_weighting':'Equal-weight least-squares point estimate; not a probability model; annotation interval uncertainty is not estimated by residuals.',
            'fitted_root_heights_per_cycle':L/height,
            'boundary_residual_rms_px':float(np.sqrt(np.mean(np.sum(residual**2,axis=1)))),
            'boundary_residual_rms_heights':float(np.sqrt(np.mean(np.sum(residual**2,axis=1))))/height,
            'direction_contact_hypothesis_consistent_with_forward_motion':L>0,
            'per_frame_world_witnesses_at_boundaries':world.tolist(),
            'limits':'Conditional fit at observed pose onsets only. Contact tags, projection and uniform root motion are hypotheses. Held frames still drift between onsets; no true world speed/contact recovered.'}

def measure(clip,base):
    height=float(clip['reference_height_px']);assert height>0
    frames=clip['frames'];assert frames
    known=all(f.get('hold') is not None for f in frames)
    durations=[Fraction(*f['hold']) for f in frames] if known else None
    if known:assert all(h>0 for h in durations)
    total=sum(durations,Fraction(0)) if known else None
    phases=np.array([float(sum(durations[:i],Fraction(0))/total) for i in range(len(frames))]) if known else np.arange(len(frames))/len(frames)
    arrays=[];bboxes=[];areas=[]
    for frame in frames:
        relative=Path(frame['image']);assert not relative.is_absolute() and '..' not in relative.parts
        path=(base/relative).resolve();assert path.is_relative_to(base.resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==frame['sha256'],str(path)
        a=np.array(Image.open(path).convert('RGBA'));arrays.append(a)
        y,x=np.where(a[:,:,3]>=128)
        bboxes.append([int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1] if len(x) else None)
        areas.append(int(np.count_nonzero(a[:,:,3]>=128)))
    assert len({a.shape for a in arrays})==1
    pairs=[]
    n=len(frames)
    for i in range(n if clip.get('loop',False) else n-1):
        j=(i+1)%n;aa=arrays[i];bb=arrays[j]
        visible=(aa[:,:,3]>0)|(bb[:,:,3]>0)
        changed=np.any(aa!=bb,axis=2)&visible
        pairs.append({'from':i,'to':j,'kind':'wrap' if j==0 else 'adjacent',
                      'changed_visible_rgba_pixels':int(np.count_nonzero(changed)),
                      'silhouette_xor_alpha128_pixels':int(np.count_nonzero((aa[:,:,3]>=128)^(bb[:,:,3]>=128))),
                      'next_pose_start_phase':float(phases[j]) if j else 1.0})
    tracks={};trace_rows={}
    for name,track in clip.get('landmarks',{}).items():
        samples=track['samples'];assert len(samples)==n
        valid=[i for i,s in enumerate(samples) if observed(s)]
        points=np.array([samples[i]['xy'] for i in valid],dtype=float)
        assert not len(points) or np.isfinite(points).all()
        rows=[]
        for pair in pairs:
            i,j=pair['from'],pair['to']
            if i in valid and j in valid:
                delta=np.asarray(samples[j]['xy'],float)-np.asarray(samples[i]['xy'],float)
                row={'from':i,'to':j,'displacement_px':delta.tolist(),'distance_px':float(np.linalg.norm(delta)),'distance_heights':float(np.linalg.norm(delta))/height}
                if known:row['onset_to_onset_average_speed_heights_per_second']=row['distance_heights']/float(durations[i])
                rows.append(row)
        tracks[name]={'label':track.get('label',name),'proxy_scope':track.get('proxy_scope','Visible drawn feature, not recovered anatomy'),
                     'source_annotations':samples,
                     'annotation_uncertainty':track.get('annotation_uncertainty'),
                     'contact_fit_eligible':track.get('contact_fit_eligible',False),
                     'visible_samples':len(valid),'unknown_samples':n-len(valid),
                     'extent_xy_px':np.ptp(points,axis=0).tolist() if len(points) else None,
                     'extent_xy_heights':(np.ptp(points,axis=0)/height).tolist() if len(points) else None,
                     'observed_adjacent_displacements':rows}
        trace_rows[name]=(valid,points,samples)
    fits=[]
    for h in clip.get('stance_hypotheses',[]):
        name=h['landmark'];track=clip['landmarks'][name];samples=track['samples'];indices=h['indices']
        if not track.get('contact_fit_eligible',False):
            fits.append({'id':h['id'],'status':'not fitted: persistent contact-bearing landmark has not been explicitly established','assumptions':h});continue
        if len(indices)<3 or any(not observed(samples[i]) for i in indices):
            fits.append({'id':h['id'],'status':'not fitted: fewer than3 visible declared samples','assumptions':h});continue
        fit=stance_fit([phases[i] for i in indices],[samples[i]['xy'] for i in indices],h['direction_vector'],height)
        fit.update({'id':h['id'],'assumptions':h,'observed_indices':indices})
        if known:
            fit['conditional_root_pixels_per_second']=fit['fitted_root_pixels_per_cycle']/float(total)
            fit['within_hold_root_drift_px']=[abs(fit['conditional_root_pixels_per_second'])*float(durations[i]) for i in indices]
        fits.append(fit)
    out={'id':clip['id'],'direction':clip.get('direction'),'action':clip.get('action'),'source':clip.get('source'),
         'timing':clip['timing'],'timing_known':known,'holds':[[h.numerator,h.denominator] for h in durations] if known else None,
         'cycle_or_clip_seconds':[total.numerator,total.denominator] if known else None,
         'plot_x_axis':'Actual hold-normalized source phase' if known else 'Uniform pose index ONLY; authored timing unknown',
         'pose_onsets_phase':phases.tolist(),'reference_height_px':height,'height_reference':clip.get('height_reference'),
         'alpha128_bounds_xyxy_exclusive':bboxes,'alpha128_foreground_area':areas,
         'adjacent_pairs':pairs,'tracks':tracks,'conditional_stance_fits':fits,
         'limits':['No art score. Different characters/styles/cameras are not pixel targets.',
                   'Sample confidence is an annotator label, not a calibrated probability. Extents below annotation uncertainty are not meaningful precision or ground-contact evidence.',
                   'RGBA deltas and alpha bounds diagnose changes; neither establishes identity or missing anatomy.',
                   'Landmarks are manual visible paint proxies. Unknown/occluded points are not interpolated into measurements.',
                   'Within-hold sprite paths are discontinuous by construction; onset secants are not continuous painted velocities.']}
    return out,(phases,trace_rows)

def plots(clip,result,data,out):
    phase,traces=data;fig,axes=plt.subplots(1,2,figsize=(12,4.5));h=result['reference_height_px']
    for name,(valid,points,samples) in traces.items():
        if clip.get('plot_landmarks') and name not in clip['plot_landmarks']:continue
        if not len(valid):continue
        p=np.full((len(clip['frames']),2),np.nan);p[valid]=points
        axes[0].plot(p[:,0]/h,p[:,1]/h,'o-',markersize=3,label=name)
        for i in valid:axes[0].annotate(str(i),(p[i,0]/h,p[i,1]/h),fontsize=7)
        axes[1].plot(phase,p[:,1]/h,'o-',markersize=3,label=name)
    axes[0].invert_yaxis();axes[0].set_aspect('equal',adjustable='datalim');axes[0].set_xlabel('Native x / fixed body height');axes[0].set_ylabel('Native y / fixed body height')
    axes[1].invert_yaxis();axes[1].set_xlabel(result['plot_x_axis']);axes[1].set_ylabel('Native y / fixed body height')
    for ax in axes:ax.grid(alpha=.25)
    if traces:axes[1].legend(fontsize=7,loc='best')
    fig.suptitle(clip['id']+' — observed paint landmarks; gaps remain unknown',fontsize=10);fig.tight_layout();fig.savefig(out/(clip['id']+'-traces.png'),dpi=150);plt.close(fig)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('manifest',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    assert not args.out.exists(),'Fresh output required';args.out.mkdir(parents=True)
    m=json.loads(args.manifest.read_text());results=[]
    for clip in m['clips']:
        assert clip['id'].replace('-','').replace('_','').isalnum()
        result,data=measure(clip,args.manifest.parent);plots(clip,result,data,args.out);results.append(result)
    report={'schema':'source-motion-measurements-v1','input_sha256':hashlib.sha256(args.manifest.read_bytes()).hexdigest(),'clips':results,'quality_score':None}
    (args.out/'MEASUREMENTS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'clips':len(results),'output':str(args.out),'quality_score':None}))
if __name__=='__main__':main()
