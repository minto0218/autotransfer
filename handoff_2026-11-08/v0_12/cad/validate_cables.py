"""Distance from sampled candidate centreline segments to current BReps.
Endpoints within 10mm are excluded (intended socket fits). Not a moving cable proof.
"""
import json,math
import numpy as np
import cadquery as cq
import build as b

def run():
 b.make_parts();routes=json.loads((b.OUT/'validation/cable_routes.json').read_text());report=[]
 for key,rs in routes.items():
  # Match pose by actual head target, not historical state index.
  p=b.target('cable_check',rs[0]['tip_y'],rs[0]['tip_z'],25,30,foam='held')
  its,_=b.state(0,override=p);parts=[q for q in its if not q.reference or q.part in('ref_vial','ref_servo')]
  bb=[]
  for q in parts:
   r=q.shape.BoundingBox();bb.append((q,np.array([r.xmin,r.ymin,r.zmin]),np.array([r.xmax,r.ymax,r.zmax])))
  radius=b.P['housing_od']/2
  for route in rs:
   pts=np.array(route['points']);dist=np.linalg.norm(np.diff(pts,axis=0),axis=1);arcs=np.r_[0,dist.cumsum()];best=8.;pair=None;checked=0
   for i,(s,t) in enumerate(zip(pts,pts[1:])):
    if arcs[i]<10 or arcs[-1]-arcs[i+1]<10:continue
    lo=np.minimum(s,t);hi=np.maximum(s,t);edge=None
    for q,mn,mx in bb:
     lower=np.linalg.norm(np.maximum(0,np.maximum(mn-hi,lo-mx)))
     if lower>=best:continue
     if edge is None:edge=cq.Edge.makeLine(cq.Vector(*s),cq.Vector(*t))
     d=q.shape.distance(edge);checked+=1
     if d<best:best=d;pair=q.name
   route['segment_rigid_clearance_mm']=best-radius;route['nearest_part']=pair
   row=dict(pose=key,name=route['name'],surface_clearance_mm=best-radius,nearest_part=pair,brep_distance_tests=checked,length_error_mm=route['length_error'],min_bend_r_mm=route['min_bend_r'])
   report.append(row);print('CABLE_CLEARANCE',row,flush=True)
  (b.OUT/'validation/cable_routes.json').write_text(json.dumps(routes,indent=2))
  (b.OUT/'validation/cable_segment_audit.json').write_text(json.dumps(dict(scope='BRep distance of piecewise-linear candidate housing centre lines, minus prototype housing radius0.8mm; 10mm socket lead-in at each end excluded. No cable-cable, continuous curvature shape, friction, force or moving-path proof.',results=report),indent=2))
 print('CABLE_AUDIT_DONE',len(report),flush=True)
if __name__=='__main__':run()
