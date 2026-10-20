from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from fractions import Fraction
import json,hashlib,math,io,struct,zlib,shutil
OUT=Path(__file__).resolve().parent
ROOT=Path('/home/astra/projects/emberwake-demo/art-source/characters-v2')
DIRS=['south','east','north','west'];ACTS=['idle','walk','attack','cast','hurt','dodge'];BG=(25,48,50,255);LIGHT=(211,213,208,255)
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cells(p):
 im=Image.open(p).convert('RGBA');return [im.crop((i%8*128,i//8*128,i%8*128+128,i//8*128+128)) for i in range(im.width//128*(im.height//128))]
def ph(im):return hashlib.sha256(im.tobytes()).hexdigest()
def comp(im,s=1,bg=BG):
 if s!=1:im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.NEAREST)
 o=Image.new('RGBA',im.size,bg);o.alpha_composite(im);return o

def sheet(path,tiles,cols=8,s=1,bg=BG):
 wh=round(128*s);o=Image.new('RGBA',(cols*wh,math.ceil(len(tiles)/cols)*(wh+20)),bg);d=ImageDraw.Draw(o)
 for k,(im,l) in enumerate(tiles):
  x=k%cols*wh;y=k//cols*(wh+20);d.text((x+2,y+2),l if s>=1 else l.split(' ')[0]+' '+l.split(' ')[1] if len(l.split(' '))>1 else l,font=FONT,fill=(32,42,42) if bg==LIGHT else (240,230,195));o.alpha_composite(comp(im,s,bg),(x,y+20))
 o.convert('RGB').save(path)

def pairs(path,ps,s=1,cols=None):
 wh=round(128*s);tw=wh*2+8;th=wh+24;cols=cols or (4 if s==1 else 2);o=Image.new('RGBA',(cols*tw,math.ceil(len(ps)/cols)*th),BG);d=ImageDraw.Draw(o)
 for k,(a,b,l) in enumerate(ps):
  x=k%cols*tw;y=k//cols*th;d.text((x+2,y+2),l,font=FONT,fill=(240,230,195));o.alpha_composite(comp(a,s),(x,y+24));o.alpha_composite(comp(b,s),(x+wh+4,y+24))
 o.convert('RGB').save(path)

def chunks(im):
 x=io.BytesIO();im.save(x,format='PNG');b=x.getvalue();pos=8;out=[]
 while pos<len(b):
  n=struct.unpack('!I',b[pos:pos+4])[0];t=b[pos+4:pos+8];v=b[pos+8:pos+8+n];out.append((t,v));pos+=12+n
 return out

def chunk(t,v):return struct.pack('!I',len(v))+t+v+struct.pack('!I',zlib.crc32(t+v)&0xffffffff)
def apng(p,ims,holds,loop):
 b=bytearray(b'\x89PNG\r\n\x1a\n');b+=chunk(b'IHDR',chunks(ims[0])[0][1]);b+=chunk(b'acTL',struct.pack('!II',len(ims),0 if loop else 1));seq=0
 for k,(im,h) in enumerate(zip(ims,holds)):
  q=Fraction(str(h));b+=chunk(b'fcTL',struct.pack('!IIIIIHHBB',seq,im.width,im.height,0,0,q.numerator,q.denominator,0,0));seq+=1
  for t,v in chunks(im):
   if t==b'IDAT':
    if k==0:b+=chunk(t,v)
    else:b+=chunk(b'fdAT',struct.pack('!I',seq)+v);seq+=1
 b+=chunk(b'IEND',b'');p.write_bytes(b);actual=Image.open(p);assert actual.n_frames==len(ims)
 for k,im in enumerate(ims):actual.seek(k);assert actual.convert('RGBA').tobytes()==im.tobytes()
 pos=8;delays=[]
 while pos<len(b):
  n=struct.unpack('!I',b[pos:pos+4])[0];t=b[pos+4:pos+8];v=b[pos+8:pos+8+n]
  if t==b'fcTL':
   v=struct.unpack('!IIIIIHHBB',v);delays.append(Fraction(v[5],v[6] or 100))
  pos+=12+n
 assert delays==[Fraction(str(h)) for h in holds]
 return {'sha256':sha(p),'duration':str(sum(delays)),'frames':len(ims),'delays':[[d.numerator,d.denominator] for d in delays]}

ledger={'input_hashes':{},'baseline_hashes':{},'comparison_v5':{},'preferred_candidate_matches':{},'clips':{},'counts':{},'joins':{}}
preferred={
 'lyra':{**{k:Path('/home/astra/artifacts/emberwake-dodge-head-v1/candidates')/(di+'.png') for k,di in zip(range(128,132),DIRS)},**{k:Path('/home/astra/artifacts/emberwake-passing-boots-v1/candidate/lyra')/f'passing-{s}.png' for k,s in zip(range(132,136),range(112,116))}},
 'brann':{128:Path('/home/astra/projects/emberwake-demo/art-source/settle-trim-v1/candidate.png'),**{k:Path('/home/astra/artifacts/emberwake-passing-boots-v1/candidate/brann')/f'passing-{s}.png' for k,s in zip(range(129,133),range(112,116))}}}
for name in ['lyra','brann']:
 out=OUT/name;out.mkdir(exist_ok=True)
 for folder in ['frames','pairs','media']:(out/folder).mkdir(exist_ok=True)
 p=ROOT/'bake-v6'/name;prior=ROOT/'bake-v5'/name
 ledger['input_hashes'][name]={fn:sha(p/fn) for fn in ['atlas.png','animations.json','BAKE-RECEIPT.json','GAIT-REPAIR-RECEIPT.json']}
 ledger['baseline_hashes'][name]={fn:sha(prior/fn) for fn in ['atlas.png','animations.json','receipt.json']}
 frozen=json.loads((OUT.parent/'v5'/'EVIDENCE.json').read_text())['input_hashes'][name]
 assert frozen==ledger['baseline_hashes'][name]
 m=json.loads((p/'animations.json').read_text());old=json.loads((prior/'animations.json').read_text());f=cells(p/'atlas.png');ff=cells(prior/'atlas.png')
 assert len(ff)==128 and len(f)==136
 changed=[k for k in range(128) if ph(f[k])!=ph(ff[k])];assert not changed
 ledger['preferred_candidate_matches'][name]={}
 for k,path in preferred[name].items():
  c=Image.open(path).convert('RGBA');match=ph(c)==ph(f[k]);assert match
  ledger['preferred_candidate_matches'][name][str(k)]={'candidate':str(path),'file_sha256':sha(path),'RGBA_sha256':ph(c),'exact':match}
 ledger['counts'][name]={'clips':len(m['animations']),'physical_cells':len(f),'nonempty_cells':sum(bool(im.getchannel('A').getbbox()) for im in f),'declared_repair_cells':len(preferred[name]),'original_128_preserved':not changed,'timeline_presentations':sum(len(c['frames']) for c in m['animations'].values()),'selected_unique':len(set(k for c in m['animations'].values() for k in c['frames']))}
 r={}
 for cid,c in m['animations'].items():
  before=old['animations'][cid];pixels=len(c['frames'])==len(before['frames']) and all(ph(f[n])==ph(ff[o]) for n,o in zip(c['frames'],before['frames']));holds=c['holds']==before['holds'] and c['loop']==before['loop']
  r[cid]={'pixels_match':pixels,'holds_loop_match':holds,'transfer':pixels and holds,'old':before,'new':c}
 ledger['comparison_v5'][name]={'first128_changed':changed,'clip_comparison':r,'transfer_clips':[cid for cid,c in r.items() if c['transfer']],'fresh_clips':[cid for cid,c in r.items() if not c['transfer']],'nonanimation_metadata_unchanged':{k:m[k]==old[k] for k in ['cell','columns','pivot','draw_scale','cast_hand','cast_release_index']}}
 for k,im in enumerate(f):im.save(out/'frames'/f'{k:03d}.png')
 all_joins=[]
 for di in DIRS:
  tile=[];allps=[];joins=[]
  for ac in ACTS:
   cid=f'{di}_{ac}';c=m['animations'][cid];ids=c['frames'];row=[(f[x],f'{ac} p{k}/f{x} {c["holds"][k]:g}s') for k,x in enumerate(ids)];tile+=row+[(Image.new('RGBA',(128,128)),'')]*(8-len(row));ps=[]
   for k,x in enumerate(ids):
    j=(k+1)%len(ids);lab=f'{cid} f{x}>f{ids[j]}'
    if j==0:lab+=' loop' if c['loop'] else ' diagnostic'
    ps.append((f[x],f[ids[j]],lab))
   pairs(out/'pairs'/f'{cid}-2x.png',ps,2);allps+=ps
   ledger['clips'].setdefault(name,{})[cid]={'frames':ids,'holds':c['holds'],'loop':c['loop'],'media':apng(out/'media'/f'{cid}.png',[comp(f[x]) for x in ids],c['holds'],c['loop'])}
   if ac!='idle':
    for ii,oi in zip(m['animations'][f'{di}_idle']['frames'],old['animations'][f'{di}_idle']['frames']):
     for endpoint in [0,-1]:
      jj=ids[endpoint];oj=old['animations'][cid]['frames'][endpoint]
      same=ph(f[ii])==ph(ff[oi]) and ph(f[jj])==ph(ff[oj])
      all_joins.append({'clip':cid,'idle':ii,'endpoint':endpoint,'frame':jj,'pixels_unchanged_v5':same})
     joins.extend([(f[ii],f[ids[0]],f'idle{ii}>{ac} first{ids[0]}'),(f[ids[-1]],f[ii],f'{ac} end{ids[-1]}>idle{ii}')])
  for s,suffix,bg in [(1,'native',BG),(2,'2x',BG),(.66,'drawscale',LIGHT)]:sheet(out/f'{di}-{suffix}.png',tile,8,s,bg)
  pairs(out/'pairs'/f'{di}-all-native.png',allps)
  pairs(out/'pairs'/f'{di}-joins-native.png',joins)
  pairs(out/'pairs'/f'{di}-joins-2x.png',joins,2,4)
  pairs(out/'pairs'/f'{di}-all-drawscale.png',allps,.66,4)
 ledger['joins'][name]=all_joins
 for di in ['south','north']:
  tiles=[]
  for ver,bank,mm in [('v5',ff,old),('v6',f,m)]:
   ids=mm['animations'][f'{di}_walk']['frames'];tiles += [(bank[x],f'{ver} p{k}/f{x}') for k,x in enumerate(ids)]+[(bank[ids[0]],f'{ver} wrap/f{ids[0]}')]
  sheet(out/f'{di}-v5-v6-gait-2x.png',tiles,9,2)
  o=Image.new('RGBA',(8*224,2*190),BG);d=ImageDraw.Draw(o)
  for vi,(ver,bank,mm) in enumerate([('v5',ff,old),('v6',f,m)]):
   for k,x in enumerate(mm['animations'][f'{di}_walk']['frames']):
    im=bank[x].crop((36,78,92,116)).resize((224,152),Image.Resampling.NEAREST);xx=k*224;yy=vi*190;d.text((xx+2,yy+2),f'{ver} p{k}/f{x}',font=FONT,fill='white');o.alpha_composite(comp(im),(xx,yy+25))
  o.convert('RGB').save(out/f'{di}-lower-v5-v6-4x.png')
 recovery=[]
 for di in DIRS:
  for ver,bank,mm in [('v5',ff,old),('v6',f,m)]:
   ids=mm['animations'][f'{di}_dodge']['frames']
   recovery +=[(bank[x],f'{di} {ver} dodge/f{x}') for x in ids[-3:]]
 sheet(out/'dodge-recovery-v5-v6-2x.png',recovery,6,2)
 if name=='brann':
  chest=[]
  for diac in ['south_attack','south_dodge']:
   for ver,bank,mm in [('v5',ff,old),('v6',f,m)]:chest +=[(bank[x],f'{diac} {ver}/f{x}') for x in mm['animations'][diac]['frames'][-3:]]
  sheet(out/'south-settle-v5-v6-2x.png',chest,6,2)
ledger['input_fingerprint']=hashlib.sha256(json.dumps(ledger['input_hashes'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
(OUT/'EVIDENCE.json').write_text(json.dumps(ledger,indent=2)+'\n')
print(json.dumps({'fingerprint':ledger['input_fingerprint'],'counts':ledger['counts'],'transfer':{n:ledger['comparison_v5'][n]['transfer_clips'] for n in ['lyra','brann']},'fresh':{n:ledger['comparison_v5'][n]['fresh_clips'] for n in ['lyra','brann']},'idlejoins_unchanged':{n:sum(j['pixels_unchanged_v5'] for j in js) for n,js in ledger['joins'].items()},'idlejoins_changed':{n:[j for j in js if not j['pixels_unchanged_v5']] for n,js in ledger['joins'].items()}},indent=2))
