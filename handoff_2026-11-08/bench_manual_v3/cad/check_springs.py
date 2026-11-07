"""Full-stroke OD2.5 spring envelopes against bench rigid parts at 8 poses.
Fixed hook screws are intended spring contacts. Exact hook clocking and knots need hands-on checks.
"""
import json,math
import build as b
from validate import overlap
b.make_parts();rows=[]
for k in range(8):
 its,p=b.state(k)
 for tag,z,low in [('G',14.65,-10.4),('T',21.6,-.4),('P',25.1,-5.9)]:
  s=b.cyl(1.25,18.8-low,(18,low,z+42),'y');bb=s.BoundingBox();best=20;near=None;hits=[]
  for q in its:
   if q.part=='spring_hook_screw':continue
   cc=q.shape.BoundingBox();d0=math.sqrt(sum(max(0,getattr(bb,a+'min')-getattr(cc,a+'max'),getattr(cc,a+'min')-getattr(bb,a+'max'))**2 for a in 'xyz'))
   v=overlap(s,q.shape)
   if v>.025:hits.append(dict(part=q.name,volume=v))
   if d0<best:
    d=s.distance(q.shape)
    if d<best:best=d;near=q.name
  rows.append(dict(state=k,spring=tag,min_gap_mm=best,nearest=near,contacts=hits))
rep=dict(scope=__doc__,rows=rows,contacts=[r for r in rows if r['contacts']],minimum_gap_mm=min(r['min_gap_mm']for r in rows));(b.OUT/'validation/springs.json').write_text(json.dumps(rep,indent=2));print('SPRINGS',rep['minimum_gap_mm'],rep['contacts'],flush=True)
if rep['contacts']:raise SystemExit(1)
