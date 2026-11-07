"""Longer constant-length loop for the left grip branch, including the high park pose."""
import json
import numpy as np
from scipy.spatial import cKDTree
import build as b
import routing as r

def run():
 b.make_parts();path=b.OUT/'validation/cable_routes.json';data=json.loads(path.read_text())
 for key,rows in data.items():
  old=next(q for q in rows if q['name']=='M1_0');p=b.target('old_loop',old['tip_y'],old['tip_z'],25,30);its,st=b.state(0,override=p);cloud=np.concatenate([r.cloud(its)]+[np.array(q['points'])[7:-7:2]for q in rows if q['name']!='M1_0']);tree=cKDTree(cloud);spec=next(s for s in r.specs(st)if s['name']=='M1_0');spec['length']=360
  best=None
  for seed in([50,80,40,100,210,-160,100,290],[40,100,60,120,220,-180,120,320],[50,60,-20,70,210,-140,120,250]):
   q=r.solve(spec,cloud,np.array(seed,float));pts=q['points'];row={k:q[k]for k in('name','motor','branch','side','length','length_actual','min_bend_r','length_error')};row.update(state=int(key),tip_y=st['tip_y'],tip_z=st['tip_z'],points=pts.tolist(),controls=q['controls'].tolist(),sampled_clearance=float(tree.query(pts[7:-7])[0].min()))
   score=lambda x:abs(x['length_error'])*50+max(0,30.5-x['min_bend_r'])*8+max(0,4-x['sampled_clearance'])*10
   if best is None or score(row)<score(best):best=row
   if abs(best['length_error'])<.1 and best['min_bend_r']>=30.5 and best['sampled_clearance']>=4:break
  for i,q in enumerate(rows):
   if q['name']=='M1_0':rows[i]=best
  path.write_text(json.dumps(data,indent=2));print('OLD_GRIP',key,best['length_error'],best['min_bend_r'],best['sampled_clearance'],flush=True)
 metrics=[{k:v for k,v in q.items()if k not in('points','controls')}for rs in data.values()for q in rs];(b.OUT/'validation/cable_metrics.json').write_text(json.dumps(metrics,indent=2));print('OLD_GRIP_DONE',flush=True)
if __name__=='__main__':run()
