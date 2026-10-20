#!/usr/bin/env python3
"""Original deterministic little forest score and synthesized action cues.
No downloaded samples, no model, no credentials. ffmpeg encodes final Vorbis.
"""
from pathlib import Path
import json
import subprocess
import wave
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SR=32000
RNG=np.random.default_rng(90214)

def save(path, samples):
    path.parent.mkdir(parents=True,exist_ok=True)
    samples=np.clip(samples,-.98,.98)
    with wave.open(str(path),'wb') as f:
        channels=1 if samples.ndim==1 else samples.shape[1]
        f.setnchannels(channels);f.setsampwidth(2);f.setframerate(SR)
        f.writeframes((samples*32767).astype('<i2').tobytes())

def freq(note):return 440*2**((note-69)/12)
def tone(note,dur,voice='bell'):
    t=np.arange(int(dur*SR))/SR;f=freq(note)
    if voice=='bell':
        y=(np.sin(2*np.pi*f*t)*np.exp(-2.8*t)+.27*np.sin(2*np.pi*2*f*t)*np.exp(-4*t)+.08*np.sin(2*np.pi*3*f*t)*np.exp(-7*t))
        y*=np.minimum(t/.008,1)
    elif voice=='flute':
        phase=2*np.pi*f*t+0.012*np.sin(2*np.pi*4.7*t)
        y=np.sin(phase)+.12*np.sin(2*phase)
        y*=np.minimum(t/.15,1)*np.minimum((dur-t)/.22,1)*.72
    else:
        y=(np.sin(2*np.pi*f*t)+.16*np.sin(2*np.pi*2*f*t))
        y*=np.minimum(t/.7,1)*np.minimum((dur-t)/.9,1)*.3
    return y

beat=60/84;bars=16;duration=bars*4*beat
score=np.zeros((round(duration*SR),2),dtype=np.float64)
def add(at,y,gain=.1,pan=0):
    start=round(at*SR);idx=(start+np.arange(len(y)))%len(score)
    score[idx,0]+=y*gain*np.sqrt((1-pan)/2)
    score[idx,1]+=y*gain*np.sqrt((1+pan)/2)

chords=[(50,57,62,65),(46,53,58,62),(53,60,65,69),(48,55,60,64)]
melodies=[[74,77,76,74,69,72],[77,74,70,69,65,69],[72,77,81,79,77,76],[76,72,67,69,72,69]]
for bar in range(bars):
    chord=chords[bar%4];base=bar*4*beat
    for i,n in enumerate(chord):add(base,tone(n,4*beat,'pad'),.14,(i-1.5)/2)
    for i,offset in enumerate([0,.5,1,1.5,2,2.5,3,3.5]):
        add(base+offset*beat,tone(chord[[0,2,1,3,2,1,3,2][i]]+12,1.65),.075,(-.5 if i%2 else .5))
    melody=melodies[bar%4]
    # Two repeated phrases, sparse flute comes in after the opening fourbars.
    if bar>=4:
        for i,(pos,length) in enumerate([(0,.7),(.8,.6),(1.5,.8),(2.5,.5),(3.1,.5)]):
            add(base+pos*beat,tone(melody[i]+(0 if bar<12 else -12),length*beat+.15,'flute'),.10,.12)
    add(base,tone(chord[0]-12,2.0,'flute'),.095,-.1)
# Wrapped delays keep loop seamless; soft saturation prevents harsh peaks.
dry=score.copy()
for delay,gain in [(.13,.16),(.277,.13),(.43,.09),(.69,.06)]:
    score+=np.roll(dry,round(delay*SR),axis=0)*gain
score=np.tanh(score*1.15)
music=ROOT/'assets/audio/music.wav';save(music,score)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(music),'-c:a','libvorbis','-q:a','4',str(music.with_suffix('.ogg'))],check=True)
music.unlink()

def cue(name,dur,kind):
    t=np.arange(int(dur*SR))/SR
    noise=RNG.normal(0,1,len(t))
    noise=np.convolve(noise,np.ones(9)/9,mode='same')
    if kind=='attack':
        phase=2*np.pi*(400*t-300*t*t/dur)
        y=(noise*.6+np.sin(phase)*.18)*np.sin(np.pi*t/dur)**1.7
    elif kind=='hit':
        y=(noise*.5+np.sin(2*np.pi*(130*t-50*t*t/dur))*.55)*np.exp(-22*t)*np.minimum(t/.003,1)
    elif kind=='dodge':
        y=noise*np.sin(np.pi*t/dur)**2*.65
    elif kind=='death':
        y=(np.sin(2*np.pi*(240*t-150*t*t/dur))*.45+noise*.08)*np.minimum(t/.02,1)*np.exp(-4*t)
    else:
        notes={'cast':[74,81,86],'nova':[62,69,74,81],'ward':[62,69,74,78,81],'pickup':[81,86],'ui':[81]}[kind]
        y=np.zeros_like(t)
        for i,n in enumerate(notes):
            start=int(i*.07*SR);voice=tone(n,max(.05,dur-i*.07))
            take=min(len(voice),len(y)-start)
            if take>0:y[start:start+take]+=voice[:take]*.3
        if kind=='nova':y+=noise*np.exp(-t*5)*.3
    y*=np.minimum((dur-t)/.035,1)
    save(ROOT/f'assets/sfx/{name}.wav',y*.62)

for name,dur in [('attack',.16),('cast',.50),('hit',.24),('nova',.65),('dodge',.23),('death',.8),('ward',1.2),('pickup',.4),('ui',.16)]:cue(name,dur,name)
(ROOT/'art-source/AUDIO-SOURCES.json').write_text(json.dumps({'origin':'Original algorithmically composed/synthesized in scripts/compose_audio.py. No samples or generative model.','sample_rate':SR,'music_seconds':duration,'bpm':84,'bars':bars,'key':'D minor / modal','seed':90214,'loop':'All score events and reverberation wrap in same buffer.'},indent=2)+'\n')
print(f'Composed{duration:.2f}s stereo loop and9SFX.')
