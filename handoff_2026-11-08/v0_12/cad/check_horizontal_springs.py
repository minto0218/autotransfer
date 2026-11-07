"""Horizontal spring solid stroke envelopes vs rigid geometry at five representative poses.
The fixed spring hook screws are intended contacts and excluded. Springs are represented
by conservative OD2.5 cylinders; knots and exact spring hook clocking remain physical checks.
"""
import json,math,numpy as np
import build as b
from validate import overlap
b.make_parts();rows=[]
for k in(0,2,11,14,16):
 items,p=b.state(k)
 for side,hx in [('old',-b.P['vial_pitch']/2),('new',b.P['vial_pitch']/2)]:
  for tag,z,low in [('grip',14.65,2-4*math.radians(60+math.degrees(2.5))),('twist',21.6,2-4*math.radians(60)),('press',25.1,2-3.6*math.radians(120))]:
   low-=.3  # moving hook extends below its nominal tie point
   s=b.cyl(1.25,18.8-low,(hx+18,p['tip_y']+low,p['tip_z']+z),'y');hits=[];gap=20;nearest=None
   for q in items:
    if q.reference or q.name.startswith(side+'_spring_hook_'):continue
    v=overlap(s,q.shape)
    if v>.025:hits.append(dict(part=q.name,overlap_mm3=v))
    aa=s.BoundingBox();bb=q.shape.BoundingBox()
    lower=math.sqrt(sum(max(0,getattr(aa,t+'min')-getattr(bb,t+'max'),getattr(bb,t+'min')-getattr(aa,t+'max'))**2 for t in 'xyz'))
    if lower<gap:
     d=s.distance(q.shape)
     if d<gap:gap=d;nearest=q.name
   row=dict(state=k,side=side,spring=tag,min_rigid_gap_mm=gap,nearest=nearest,contacts=hits);rows.append(row);print('SPRING_BODY',row,flush=True)
rep=dict(scope=__doc__,rows=rows,contacts=[r for r in rows if r['contacts']],nominal_inter_spring_surface_gap_mm=1.)
(b.OUT/'validation/horizontal_spring_audit.json').write_text(json.dumps(rep,indent=2))
