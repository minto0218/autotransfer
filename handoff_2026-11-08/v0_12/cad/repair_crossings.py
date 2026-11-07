"""Repair only static pair conflicts; dense full cable curves include all end portions."""
import json
import numpy as np
from scipy.spatial import cKDTree
import build as b
import routing as r
from cable_math import segdist

def dense(points,step=.75):
 out=[]
 for a,c in zip(np.array(points)[:-1],np.array(points)[1:]):
  n=max(1,int(np.linalg.norm(c-a)/step)+1);out.extend(a+(c-a)*np.arange(n)[:,None]/n)
 out.append(points[-1]);return np.array(out)
def run():
 b.make_parts();r.P['housing_solve_margin_r']=3.;path=b.OUT/'validation/cable_routes.json';data=json.loads(path.read_text());audit=json.loads((b.OUT/'validation/cable_pair_audit.json').read_text());targets=[]
 for q in audit['results']:
  if q['surface_clearance_mm']>=.5:continue
  names={r['name']for r in data[q['pose']]};name=q['a']if q['a']in names else q['b'];target=(q['pose'],name)
  if target not in targets:targets.append(target)
 for key,rs in data.items():
  for q in rs:
   if abs(q['length_error'])>.3 or q['min_bend_r']<30 or q['sampled_clearance']<2.5 or q.get('segment_rigid_clearance_mm',1)<.5 or q.get('spring_envelope_clearance_mm',1)<.5:
    t=(key,q['name'])
    if t not in targets:targets.append(t)
 cd=b.P['gear_cd'];rr=b.P['joint_input_r'];normals=[]
 for j,x in enumerate((b.P['root_capstan_x']+2,b.P['root_capstan_x']+4)):
  y=b.P['root_y']+cd+(-rr if j==0 else rr);normals.append(dict(name='M4_normal_'+str(j),points=[[x,y,b.P['root_z']],[x,y,b.P['deck_z']+25]],radius=b.P['wire_d']/2))
 for key,name in targets:
  rs=data[key];old=next(q for q in rs if q['name']==name);its,st=b.state(0,override=b.target('crossing_repair',old['tip_y'],old['tip_z'],25,30));rigid=r.cloud(its);others=[dict(q,radius=b.P['housing_od']/2)for q in rs if q['name']!=name]+normals;cloud=np.concatenate([dense(q['points'])for q in others]);ctree=cKDTree(cloud);tree=cKDTree(rigid);spec=next(s for s in r.specs(st)if s['name']==name);cp=np.array(old['controls']);warm=np.r_[np.linalg.norm(cp[1]-cp[0]),np.linalg.norm(cp[4]-cp[5]),cp[2],cp[3]];best=None
  sg=spec['side'];seeds=[warm,np.array([50,80,sg*20,80,180,sg*180,80,300]),np.array([50,100,sg*20,120,200,sg*160,120,320]),np.array([50,80,sg*10,40,170,sg*180,40,290])]
  for seed in seeds:
   q=r.solve(spec,rigid,seed,other_cables=cloud);pts=q['points'];row={k:q[k]for k in('name','motor','branch','side','length','length_actual','min_bend_r','length_error')};row.update(state=int(key),tip_y=st['tip_y'],tip_z=st['tip_z'],points=pts.tolist(),controls=q['controls'].tolist(),sampled_clearance=float(tree.query(pts[7:-7])[0].min()),pair_min_surface_clearance_mm=min(segdist(pts,c['points'])-b.P['housing_od']/2-c['radius']for c in others))
   score=lambda x:abs(x['length_error'])*80+max(0,30.3-x['min_bend_r'])*20+max(0,2.5-x['sampled_clearance'])*10+max(0,.8-x['pair_min_surface_clearance_mm'])*50
   if best is None or score(row)<score(best):best=row
   print('TRY',key,name,row['length_error'],row['min_bend_r'],row['sampled_clearance'],row['pair_min_surface_clearance_mm'],flush=True)
   if abs(best['length_error'])<.3 and best['min_bend_r']>=30 and best['sampled_clearance']>=2.5 and best['pair_min_surface_clearance_mm']>=.8:break
  for i,q in enumerate(rs):
   if q['name']==name:rs[i]=best
  path.write_text(json.dumps(data,indent=2));print('CROSSING_REPAIRED',key,name,flush=True)
 metrics=[{k:v for k,v in q.items()if k not in('points','controls')}for rs in data.values()for q in rs];(b.OUT/'validation/cable_metrics.json').write_text(json.dumps(metrics,indent=2));print('CROSSING_REPAIRS_DONE',flush=True)
if __name__=='__main__':run()
