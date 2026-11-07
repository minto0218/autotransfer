"""Bare return strands against rigid parts after leaving each winding drum.
Wound arcs, knots and intended spring contacts are excluded from this local check.
"""
import json,numpy as np
import cadquery as cq
import build as b
import prototype

def run():
 b.make_parts();results=[]
 for k in(0,2,11,14,16):
  items,p=b.state(k);bodies=[q for q in items if not q.reference and not q.name.startswith('new_')];bounds=[]
  for q in bodies:
   bb=q.shape.BoundingBox();bounds.append((q,np.array([bb.xmin,bb.ymin,bb.zmin]),np.array([bb.xmax,bb.ymax,bb.zmax])))
  for i,q in enumerate(prototype.RETURN):
   angle=p['twist']+p['old_relative']if i==0 else p['twist']if i==1 else p['push_old']/20*120
   pts=np.array(prototype.return_path(q,angle)['points'])+np.array([-b.P['vial_pitch']/2,p['tip_y'],p['tip_z']]);best=5;nearest=None
   for a,c in zip(pts[:-1],pts[1:]):
    for body,mn,mx in bounds:
     lower=np.linalg.norm(np.maximum(0,np.maximum(mn-np.maximum(a,c),np.minimum(a,c)-mx)))
     if lower>=best:continue
     edge=cq.Edge.makeLine(cq.Vector(*a),cq.Vector(*c));d=body.shape.distance(edge)
     if d<best:best=d;nearest=body.name
   row=dict(state=k,return_tag=q['tag'],surface_gap_mm=best-.15,nearest=nearest);results.append(row);print('LOCAL_RETURN',row,flush=True)
 (b.OUT/'validation/local_return_audit.json').write_text(json.dumps(dict(scope=__doc__,results=results,penetrations=[r for r in results if r['surface_gap_mm']<-.01]),indent=2))
if __name__=='__main__':run()
