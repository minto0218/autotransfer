"""Conservative solid envelopes of all spring coils/hooks over their operating strokes."""
import json,math
import numpy as np
import cadquery as cq
import build as b
routes=json.loads((b.OUT/'validation/cable_routes.json').read_text());rows=[]
for pose,rs in routes.items():
 ty,tz=rs[0]['tip_y'],rs[0]['tip_z'];obstacles=[]
 for hx in(-b.P['vial_pitch']/2,b.P['vial_pitch']/2):
  for zz,low in[(14.65,-12.5),(21.6,-2.5),(25.1,-5.9)]:
   s=b.cyl(1.4,18.8-low,(hx+18,ty+low,tz+zz),'y');bb=s.BoundingBox();obstacles.append((s,np.array([bb.xmin,bb.ymin,bb.zmin]),np.array([bb.xmax,bb.ymax,bb.zmax])))
 for r in rs:
  pts=np.array(r['points']);arc=np.r_[0,np.linalg.norm(np.diff(pts,axis=0),axis=1).cumsum()];best=15.
  for i,(a,c)in enumerate(zip(pts,pts[1:])):
   if arc[i]<10 or arc[-1]-arc[i+1]<10:continue
   for s,mn,mx in obstacles:
    lower=np.linalg.norm(np.maximum(0,np.maximum(mn-np.maximum(a,c),np.minimum(a,c)-mx)))
    if lower>=best:continue
    edge=cq.Edge.makeLine(cq.Vector(*a),cq.Vector(*c));best=min(best,s.distance(edge))
  rows.append(dict(pose=pose,name=r['name'],spring_envelope_surface_gap_mm=best-b.P['housing_od']/2))
rep=dict(scope='Housing segments against solid cylinder envelopes containing spring bodies/hooks throughout their strokes; 10mm socket lead-ins excluded.',results=rows,minimum_gap_mm=min(q['spring_envelope_surface_gap_mm']for q in rows),contacts=[q for q in rows if q['spring_envelope_surface_gap_mm']<0])
(b.OUT/'validation/cable_spring_audit.json').write_text(json.dumps(rep,indent=2));print('SPRING_CABLE',rep['minimum_gap_mm'],rep['contacts'],flush=True)
