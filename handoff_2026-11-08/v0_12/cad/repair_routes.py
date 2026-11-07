"""Try alternative front-facing service loops only for unmet route candidates."""
import json
import numpy as np
from scipy.spatial import cKDTree
import build as b
import routing as r

def run():
 b.make_parts();path=b.OUT/'validation/cable_routes.json';data=json.loads(path.read_text())
 for key,rows in data.items():
  p=b.target('repair',rows[0]['tip_y'],rows[0]['tip_z'],25,30);its,st=b.state(0,override=p);base=r.cloud(its)
  for i,old in enumerate(rows):
   if abs(old['length_error'])<.3 and old['min_bend_r']>=30 and old['sampled_clearance']>=2.5:continue
   spec=next(s for s in r.specs(st) if s['name']==old['name']);others=[np.array(q['points'])[7:-7:2] for j,q in enumerate(rows) if j!=i];cloud=np.concatenate([base]+others);tree=cKDTree(cloud)
   def score(q):return abs(q['length_error'])*20+max(0,30.5-q['min_bend_r'])*5+max(0,3-q['sampled_clearance'])*5
   best=old;sg=spec['side']
   for y,z in((80,220),(120,270)):
    seed=np.array([50,60,-sg*35,y,180,sg*160,y,z],float)
    q=r.solve(spec,cloud,seed);pts=q['points'];row={k:q[k] for k in('name','motor','branch','side','length','length_actual','min_bend_r','length_error')};row.update(state=int(key),tip_y=st['tip_y'],tip_z=st['tip_z'],points=pts.tolist(),controls=q['controls'].tolist(),sampled_clearance=float(tree.query(pts[7:-7])[0].min()))
    if score(row)<score(best):best=row
    if abs(best['length_error'])<.3 and best['min_bend_r']>=30 and best['sampled_clearance']>=3:break
   rows[i]=best;print('REPAIR',key,best['name'],best['length_error'],best['min_bend_r'],best['sampled_clearance'],flush=True)
  path.write_text(json.dumps(data,indent=2))
 metrics=[{k:v for k,v in row.items() if k not in('points','controls')} for rows in data.values() for row in rows]
 (b.OUT/'validation/cable_metrics.json').write_text(json.dumps(metrics,indent=2));print('REPAIRS_DONE',flush=True)
if __name__=='__main__':run()
