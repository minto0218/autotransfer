"""Additional constant-length candidates for the right twist service loop."""
import json
import numpy as np
from scipy.spatial import cKDTree
import build as b
import routing as r

def run():
 b.make_parts();path=b.OUT/'validation/cable_routes.json';data=json.loads(path.read_text());r.P['housing_solve_margin_r']=3.
 for key,rs in data.items():
  old=next(q for q in rs if q['name']=='M3_1')
  if abs(old['length_error'])<.3 and old['min_bend_r']>=30.5 and old['sampled_clearance']>=3:continue
  its,st=b.state(0,override=b.target('right_twist',old['tip_y'],old['tip_z'],25,30));cloud=np.concatenate([r.cloud(its)]+[np.array(q['points'])[7:-7:2]for q in rs if q['name']!='M3_1']);tree=cKDTree(cloud);spec=next(s for s in r.specs(st)if s['name']=='M3_1');cp=np.array(old['controls']);warm=np.r_[np.linalg.norm(cp[1]-cp[0]),np.linalg.norm(cp[4]-cp[5]),cp[2],cp[3]];best=old
  for seed in(warm,np.array([50,80,-40,80,180,180,80,300]),np.array([40,100,-20,120,180,180,120,320])):
   q=r.solve(spec,cloud,seed);pts=q['points'];row={k:q[k]for k in('name','motor','branch','side','length','length_actual','min_bend_r','length_error')};row.update(state=int(key),tip_y=st['tip_y'],tip_z=st['tip_z'],points=pts.tolist(),controls=q['controls'].tolist(),sampled_clearance=float(tree.query(pts[7:-7])[0].min()))
   score=lambda x:abs(x['length_error'])*100+max(0,30.5-x['min_bend_r'])*20+max(0,3-x['sampled_clearance'])*10
   if score(row)<score(best):best=row
   if abs(best['length_error'])<.3 and best['min_bend_r']>=30.5 and best['sampled_clearance']>=3:break
  for i,q in enumerate(rs):
   if q['name']=='M3_1':rs[i]=best
  path.write_text(json.dumps(data,indent=2));print('RIGHT_TWIST',key,best['length_error'],best['min_bend_r'],best['sampled_clearance'],flush=True)
 metrics=[{k:v for k,v in q.items()if k not in('points','controls')}for rs in data.values()for q in rs];(b.OUT/'validation/cable_metrics.json').write_text(json.dumps(metrics,indent=2));print('RIGHT_TWIST_DONE',flush=True)
if __name__=='__main__':run()
