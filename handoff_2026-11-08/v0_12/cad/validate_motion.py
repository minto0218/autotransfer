"""Additional discrete path samples, not swept-volume or contact dynamics."""
import json,hashlib
import numpy as np
import build as b
from validate import overlap
from control_model import interpolate

def run():
 b.make_parts();cache={};rows=[];samples=[]
 def hit(q,r):
  if hasattr(q.shape,'_mesh_pose') and hasattr(r.shape,'_mesh_pose'):
   key=(q.part,r.part,tuple(np.round(np.linalg.inv(q.shape._mesh_pose)@r.shape._mesh_pose,6).ravel()))
   if key not in cache:cache[key]=overlap(q.shape,r.shape)
   return cache[key]
  return overlap(q.shape,r.shape)
 for i,j in((0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(9,11),(11,12),(12,13)):
  for t in(.5,):samples.append((f'{i}->{j} t={t}',interpolate(i,j,t)))
 for gap in(5,35):
  for tw in(-30,30):samples.append((f'gap{gap} twist{tw}',b.target('range',0,116,gap,tw,foam='installed')))
 for n,(label,p) in enumerate(samples):
  its,st=b.state(0,override=p);rigid=[q for q in its if not q.reference]
  for i,q in enumerate(rigid):
   for r in rigid[i+1:]:
    v=hit(q,r)
    if v>.025:rows.append(dict(sample=n,label=label,a=q.name,b=r.name,volume_mm3=v));print('OVERLAP',rows[-1],flush=True)
  for glass in[q for q in its if q.part=='ref_vial']:
   for q in rigid:
    if q.group=='holder':continue
    v=hit(glass,q)
    if v>.025:rows.append(dict(sample=n,label=label,a=glass.name,b=q.name,volume_mm3=v))
  print('PATH_CHECKED',n,label,'contacts',len(rows),flush=True)
 report=dict(source_sha256=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((b.ROOT/'cad').glob('*.py')))).hexdigest(),scope='14 discrete intermediate/range samples; active rigid pairs and glass; threshold .025mm3. Soft foam, wire, return springs excluded. Not a continuous sweep proof.',samples=len(samples),contacts=rows)
 (b.OUT/'validation/motion_audit.json').write_text(json.dumps(report,indent=2));print('MOTION_DONE',len(rows),flush=True)
if __name__=='__main__':run()
