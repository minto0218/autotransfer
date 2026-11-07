import json
import cadquery as cq
import build as b
from validate import overlap
b.make_parts();rows=[]
for g0,g1 in((5,35),(35,5)):
 for tw in(-30,0,30):
  A,_=b.state(0,override=b.target('old',0,116,g0,tw,foam='installed'));B,_=b.state(0,override=b.target('new',0,116,g1,tw,foam='installed'))
  x=[q for q in A if q.name.startswith('old_')and not q.reference and q.group!='holder'];y=[q for q in B if q.name.startswith('new_')and not q.reference and q.group!='holder'];hits=[]
  for q in x:
   for r in y:
    v=overlap(q.shape,r.shape)
    if v>.025:hits.append(dict(a=q.name,b=r.name,volume_mm3=v))
  d=cq.Compound.makeCompound([q.shape for q in x]).distance(cq.Compound.makeCompound([q.shape for q in y]));row=dict(old_gap=g0,new_gap=g1,twist=tw,contacts=hits,min_rigid_distance_mm=d);rows.append(row);print('INDEPENDENT',row,flush=True)
(b.OUT/'validation/independent_heads.json').write_text(json.dumps(dict(scope='Cross-unit rigid pairs at six asymmetric grip/twist combinations; foam and wires excluded.',samples=rows),indent=2))
