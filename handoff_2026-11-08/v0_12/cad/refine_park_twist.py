import json
import numpy as np
from scipy.spatial import cKDTree
import build as b
import routing as r
from repair_crossings import dense
from cable_math import segdist

def run():
 b.make_parts();path=b.OUT/'validation/cable_routes.json';data=json.loads(path.read_text());key='5';rows=data[key];old=next(q for q in rows if q['name']=='M3_1');items,st=b.state(0,override=b.target('park_route',old['tip_y'],old['tip_z'],25,30));rigid=r.cloud(items);tree=cKDTree(rigid);others=[dict(q,radius=b.P['housing_od']/2)for q in rows if q['name']!=old['name']];cloud=np.concatenate([dense(q['points'])for q in others]);base=next(q for q in r.specs(st)if q['name']==old['name']);best=None
 for L in(360,400,440):
  for seed in([60,70,180,-180,300,180,-100,300],[50,80,30,-230,280,60,-210,300],[50,80,30,-40,300,130,40,300]):
   spec=dict(base,length=L,control_z_min=base['end'][2]+20)
   q=r.solve(spec,rigid,seed,other_cables=cloud);pts=q['points'];row={k:q[k]for k in('name','motor','branch','side','length','length_actual','min_bend_r','length_error')};row.update(state=5,tip_y=st['tip_y'],tip_z=st['tip_z'],points=pts.tolist(),controls=q['controls'].tolist(),sampled_clearance=float(tree.query(pts[7:-7])[0].min()),pair_min_surface_clearance_mm=min(segdist(pts,z['points'])-b.P['housing_od']/2-z['radius']for z in others));print('PARK_TRY',L,row['length_error'],row['min_bend_r'],row['sampled_clearance'],row['pair_min_surface_clearance_mm'],flush=True)
   if abs(row['length_error'])<.3 and row['min_bend_r']>=30 and row['sampled_clearance']>=2.5 and row['pair_min_surface_clearance_mm']>=.5:best=row;break
  if best:break
 if best:
  rows[rows.index(old)]=best;path.write_text(json.dumps(data,indent=2));print('PARK_SOLVED',best['length'],flush=True)
 else:print('PARK_UNSOLVED',flush=True)
if __name__=='__main__':run()
