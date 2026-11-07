"""Rigid BRep audit, including all active parts. No blanket gear/fit exclusions."""
import json,math,hashlib
import numpy as np
import build as b

def overlap(s,t):
 x=s.BoundingBox();y=t.BoundingBox()
 if any(min(getattr(x,k+'max'),getattr(y,k+'max'))-max(getattr(x,k+'min'),getattr(y,k+'min'))<.0005 for k in 'xyz'):return 0
 return abs(s.intersect(t).Volume())

def run():
 b.make_parts();rows=[];mesherrors=[];cache={}
 digest=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((b.ROOT/'cad').glob('*.py')))).hexdigest()
 def hit(q,r):
  if hasattr(q.shape,'_mesh_pose') and hasattr(r.shape,'_mesh_pose'):
   T=np.linalg.inv(q.shape._mesh_pose)@r.shape._mesh_pose
   key=(q.part,r.part,tuple(np.round(T,6).ravel()))
   if key not in cache:cache[key]=overlap(q.shape,r.shape)
   return cache[key]
  return overlap(q.shape,r.shape)
 cases=[(0,None),(2,None),(3,None),(5,None),(11,None),(14,None),(16,None)]
 for n,(k,t) in enumerate(cases):
  its,st=b.state(k or 0,override=t);pp=[q for q in its if not q.reference and q.part!='ref_sponge']
  for i,q in enumerate(pp):
   for r in pp[i+1:]:
    v=hit(q,r)
    if v>.025:
     row=dict(sample=n,state=k,a=q.name,b=r.name,volume_mm3=round(v,5));rows.append(row);print('OVERLAP',row,flush=True)
  # Glass is checked separately. Foam is intentionally compressible and is not rigid glass.
  for vial in [q for q in its if q.part=='ref_vial']:
   for q in pp:
    if q.group=='holder':continue
    v=hit(vial,q)
    if v>.025:rows.append(dict(sample=n,state=k,a=vial.name,b=q.name,volume_mm3=round(v,5)))
  if n in(0,2,4):
   for q in pp:
    m=b.mesh_cache.mesh(q,b.PARTS);v=np.array(m['v']);bb=q.shape.BoundingBox();expected=np.array([[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax]])
    err=float(np.max(np.abs(np.array([v.min(0),v.max(0)])-expected)))
    if err>.6:mesherrors.append(dict(name=q.name,sample=n,bbox_error_mm=err))
  print('RIGID_CHECKED',n,'contacts',len(rows),flush=True)
 used={q.part for q in b.state(0)[0]}
 report={'source_sha256':digest,'scope':'All active non-reference rigid pairs, including gears and locks; glass separate; threshold .025 mm^3. Foam, wire and springs excluded. No elastic/dynamic/force qualification.','samples':len(cases),'contacts':rows,'mesh_pose_errors':mesherrors,'parts':{n:{'valid':s.isValid(),'solids':len(s.Solids())} for n,s in b.PARTS.items() if n in used}}
 (b.OUT/'validation/rigid_audit_current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print('AUDIT_DONE',len(rows),'contacts',len(mesherrors),'mesh mismatches',flush=True)
if __name__=='__main__':run()
