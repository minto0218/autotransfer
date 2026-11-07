"""Refine remaining static candidates with explicit length/curvature constraints.
Does not prove continuous deformation of one physical housing between poses.
"""
import json
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
import build as b
import routing as r
from repair_crossings import dense
from cable_math import segdist

def run():
 b.make_parts();path=b.OUT/'validation/cable_routes.json';data=json.loads(path.read_text());cd=b.P['gear_cd'];R=b.P['joint_input_r'];normals=[]
 for j in range(2):
  x=b.P['root_capstan_x']+2+2*j;y=b.P['root_y']+cd+(-R if j==0 else R);normals.append(dict(points=[[x,y,b.P['root_z']],[x,y,b.P['deck_z']+25]],radius=b.P['wire_d']/2))
 for key,rows in data.items():
  targets=[q for q in rows if q['min_bend_r']<30 or abs(q['length_error'])>.3 or q['sampled_clearance']<2.5]
  if not targets:continue
  its,st=b.state(0,override=b.target('constraint_refine',rows[0]['tip_y'],rows[0]['tip_z'],25,30));rigid=cKDTree(r.cloud(its))
  for old in targets:
   spec=next(q for q in r.specs(st)if q['name']==old['name']);S=spec['start'];E=spec['end'];L=spec['length'];cp=np.array(old['controls']);warm=np.r_[np.linalg.norm(cp[1]-cp[0]),np.linalg.norm(cp[4]-cp[5]),cp[2],cp[3]]
   others=[dict(q,radius=b.P['housing_od']/2)for q in rows if q['name']!=old['name']]+normals;ct=cKDTree(np.concatenate([dense(q['points'])for q in others]));bounds=[(25,400),(25,400),(5,450)if spec['side']>0 else(-450,-5),(-600,400),(-250,700),(5,450)if spec['side']>0 else(-450,-5),(-600,400),(-250,700)]
   def control(x):return np.array([S,S+x[0]*spec['ds'],x[2:5],x[5:8],E+x[1]*spec['de'],E])
   def cons(x):
    pts,rr,ll=r.evaluate(control(x));arc=np.r_[0,np.linalg.norm(np.diff(pts,axis=0),axis=1).cumsum()];mask=(arc>=10)&(arc[-1]-arc>=10)
    return np.r_[(.15-abs(ll-L)),rr/30.4-1,(rigid.query(pts)[0]-3.1)*mask,ct.query(pts)[0]-4.1]
   opt=minimize(lambda x:np.sum(((x-warm)/100)**2),warm,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=cons)],options=dict(maxiter=400,ftol=1e-8))
   pts,rr,ll=r.evaluate(control(opt.x));row=dict(old);row.update(length=spec['length'],length_actual=ll,length_error=ll-L,min_bend_r=float(min(rr)),sampled_clearance=float(rigid.query(pts[7:-7])[0].min()),points=pts.tolist(),controls=control(opt.x).tolist(),pair_min_surface_clearance_mm=min(segdist(pts,q['points'])-b.P['housing_od']/2-q['radius']for q in others))
   print('CONSTRAINT_REFINE',key,row['name'],opt.success,opt.message,row['length_error'],row['min_bend_r'],row['sampled_clearance'],row['pair_min_surface_clearance_mm'],flush=True)
   if abs(row['length_error'])<=.3 and row['min_bend_r']>=30 and row['sampled_clearance']>=2.5 and row['pair_min_surface_clearance_mm']>=.5:
    rows[rows.index(old)]=row;path.write_text(json.dumps(data,indent=2))
 metrics=[{k:v for k,v in q.items()if k not in('points','controls')}for rs in data.values()for q in rs];(b.OUT/'validation/cable_metrics.json').write_text(json.dumps(metrics,indent=2));print('CONSTRAINT_DONE',flush=True)
if __name__=='__main__':run()
