"""Use one constant360mm service-loop length for the old twist branch at all poses."""
import json
import numpy as np
from scipy.spatial import cKDTree
import build as b
import routing as r
from cable_math import segdist
from repair_crossings import dense

def run():
 b.make_parts();path=b.OUT/'validation/cable_routes.json';data=json.loads(path.read_text());normals=[];cd=b.P['gear_cd'];R=b.P['joint_input_r']
 for j in range(2):
  x=b.P['root_capstan_x']+2+2*j;y=b.P['root_y']+cd+(-R if j==0 else R);normals.append(dict(points=[[x,y,b.P['root_z']],[x,y,b.P['deck_z']+25]],radius=b.P['wire_d']/2))
 for key,rs in data.items():
  old=next(q for q in rs if q['name']=='M3_0');its,st=b.state(0,override=b.target('left_twist',old['tip_y'],old['tip_z'],25,30));rigid=r.cloud(its);tree=cKDTree(rigid);others=[dict(q,radius=b.P['housing_od']/2)for q in rs if q['name']!='M3_0']+normals;cloud=np.concatenate([dense(q['points'])for q in others]);spec=next(q for q in r.specs(st)if q['name']=='M3_0');cp=np.array(old['controls']);warm=np.r_[np.linalg.norm(cp[1]-cp[0]),np.linalg.norm(cp[4]-cp[5]),cp[2],cp[3]];best=None
  for seed in(warm,np.array([50,80,-20,80,180,-180,80,300]),np.array([50,100,-20,120,200,-160,120,320])):
   q=r.solve(spec,rigid,seed,other_cables=cloud);pts=q['points'];row={k:q[k]for k in('name','motor','branch','side','length','length_actual','min_bend_r','length_error')};row.update(state=int(key),tip_y=st['tip_y'],tip_z=st['tip_z'],points=pts.tolist(),controls=q['controls'].tolist(),sampled_clearance=float(tree.query(pts[7:-7])[0].min()),pair_min_surface_clearance_mm=min(segdist(pts,c['points'])-b.P['housing_od']/2-c['radius']for c in others))
   score=lambda x:abs(x['length_error'])*100+max(0,30.3-x['min_bend_r'])*30+max(0,2.5-x['sampled_clearance'])*10+max(0,.8-x['pair_min_surface_clearance_mm'])*50
   if best is None or score(row)<score(best):best=row
   if abs(best['length_error'])<.3 and best['min_bend_r']>=30 and best['sampled_clearance']>=2.5 and best['pair_min_surface_clearance_mm']>=.8:break
  for i,q in enumerate(rs):
   if q['name']=='M3_0':rs[i]=best
  path.write_text(json.dumps(data,indent=2));print('EXTENDED_LEFT_TWIST',key,best['length_error'],best['min_bend_r'],best['sampled_clearance'],best['pair_min_surface_clearance_mm'],flush=True)
 metrics=[{k:v for k,v in q.items()if k not in('points','controls')}for rs in data.values()for q in rs];(b.OUT/'validation/cable_metrics.json').write_text(json.dumps(metrics,indent=2));print('EXTENDED_DONE',flush=True)
if __name__=='__main__':run()
