"""Fixed-length external housing candidates. Sampled geometry, not a cable dynamics proof."""
import math,json
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
import build as b
from drive import top_ends
P=b.P
P['housing_solve_margin_r']=1.
def specs(st):
 rows=[]
 def add(mid,branch,end,side,L):
  x,y=top_ends(mid)[branch]
  rows.append(dict(name=f'M{mid}_{branch}',motor=mid,branch=branch,start=np.array([x,y,237.]),end=np.array(end),ds=np.array([0.,0.,-1.]),de=np.array([0.,0.,1.]),side=side,length={'M1_0':360,'M3_0':360,'M3_1':400,'M6_0':360}.get(f'M{mid}_{branch}',L)))
 for side,hx,sg in(('old',-P['vial_pitch']/2,-1),('new',P['vial_pitch']/2,1)):
  for mid,branch,x,y,L in((1 if sg<0 else 2,0,10.25,-18,360),(3,0 if sg<0 else 1,-13,-18,280),(6 if sg<0 else 7,0,-7.3,-15,360)):
   add(mid,branch,[hx+x,st['tip_y']+y,st['tip_z']+45.8],sg,L)
 for j,x in enumerate((30,32)):
  add(5,j,[x,st['elbow_y']-P['gear_cd']+(-8.2 if j==0 else 8.2),st['elbow_z']+29],1,240)
 return rows
def bernstein(n,t):return np.array([math.comb(n,k)*t**k*(1-t)**(n-k) for k in range(n+1)]).T
T=np.linspace(0,1,181);B5=bernstein(5,T);B4=bernstein(4,T);B3=bernstein(3,T)
def evaluate(cp):
 pts=B5@cp;d=B4@(5*np.diff(cp,axis=0));dd=B3@(20*np.diff(cp,n=2,axis=0))
 speed=np.linalg.norm(d,axis=1);cross=np.linalg.norm(np.cross(d,dd),axis=1)
 radii=speed**3/np.maximum(cross,1e-8);length=float(np.linalg.norm(np.diff(pts,axis=0),axis=1).sum())
 return pts,radii,length

def solve(spec,cloud=None,seed=None,other_cables=None):
 S=spec['start'];E=spec['end'];ds=spec['ds'];de=spec['de'];sg=spec['side'];L=spec['length']
 # Two free intermediate points and two tangent lengths. Broad external loops avoid the feed lane.
 x0=np.array([60,60,sg*115,-180,200,sg*115,-170,160])
 lane={'M1_0':105,'M3_0':130,'M6_0':155,'M2_0':105,'M3_1':130,'M7_0':155,'M5_0':110,'M5_1':145}.get(spec['name'],170)
 x0[[2,5]]=sg*lane
 if spec['motor']==5:x0[[3,6]]=-160
 else:x0[[3,6]]=[-80,60];x0[[4,7]]=[180,220]
 if seed is not None:x0=np.array(seed,float)
 lo=np.array([25,25,-450,-600,-250,-450,-600,-250],float);hi=np.array([400,400,450,400,700,450,400,700],float)
 if other_cables is not None:
  if sg>0:lo[[2,5]]=5
  else:hi[[2,5]]=-5
 if 'control_z_min' in spec:lo[[4,7]]=spec['control_z_min']
 x0=np.maximum(lo+.01,np.minimum(hi-.01,x0))
 tree=cKDTree(cloud) if cloud is not None and len(cloud) else None
 cable_tree=cKDTree(other_cables) if other_cables is not None else None
 def cp_of(x):return np.array([S,S+x[0]*ds,x[2:5],x[5:8],E+x[1]*de,E])
 def residual(x):
  cp=cp_of(x);pts,R,l=evaluate(cp)
  res=[(l-L)/.03]
  res.extend(300*np.maximum(0,(P['housing_design_bend_r']+P['housing_solve_margin_r'])/np.maximum(R,1)-1))
  res.extend(.0008*(x-x0))
  # The mating sockets are allowed within 10 mm of the endpoints only.
  q=pts[5:-5:3]
  if cable_tree is None:
   if tree is not None:res.extend(40*np.maximum(0,5-tree.query(q)[0]))
  else:
   arc=np.r_[0,np.linalg.norm(np.diff(pts,axis=0),axis=1).cumsum()];mask=(arc>=10)&(arc[-1]-arc>=10)
   if tree is not None:res.extend(40*np.maximum(0,5-tree.query(pts)[0])*mask)
   res.extend(50*np.maximum(0,5-cable_tree.query(pts)[0]))
  res.extend(.5*np.maximum(0,np.abs(q[:,0])-220))
  res.extend(10*np.maximum(0,10-q[:,2]))
  return np.array(res)
 opt=least_squares(residual,x0,bounds=(lo,hi),max_nfev=180,ftol=1e-6,xtol=1e-6,gtol=1e-6)
 cp=cp_of(opt.x);pts,R,l=evaluate(cp)
 if abs(l-L)>.3 or min(R)<P['housing_design_bend_r']+.1:
  # A longer service loop is an explicit alternate cut length, never silent stretching.
  for lift in(100,-60,180):
   xx=x0.copy();xx[[4,7]]=np.clip(xx[[4,7]]+lift,lo[[4,7]]+.1,hi[[4,7]]-.1)
   trial=least_squares(residual,xx,bounds=(lo,hi),max_nfev=180)
   pp,rr,ll=evaluate(cp_of(trial.x))
   if abs(ll-L)+max(0,P['housing_design_bend_r']+.5-min(rr))*5 < abs(l-L)+max(0,P['housing_design_bend_r']+.5-min(R))*5:opt=trial;cp=cp_of(opt.x);pts,R,l=pp,rr,ll
 return dict(**spec,points=pts,controls=cp,seed=opt.x,length_actual=l,min_bend_r=float(min(R)),length_error=l-L)


def cloud(its):
 pts=[];rng=np.random.default_rng(8)
 for item in its:
  if item.reference:continue
  m=b.mesh_cache.mesh(item,b.PARTS);v=np.array(m['v']);f=np.array(m['f'],int)
  pts.extend(v[::max(1,len(v)//400)])
  tri=v[f];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
  for t,A in zip(tri,area):
   if A<5:continue
   n=min(2000,max(1,int(A/15)));uv=rng.random((n,2));uv[uv.sum(1)>1]=1-uv[uv.sum(1)>1]
   pts.extend(t[0]+uv[:,0,None]*(t[1]-t[0])+uv[:,1,None]*(t[2]-t[0]))
 # Fill the known solid frame boxes as well as their surfaces. Surface-only
 # samples can miss a path that passes through the centre of a thick column.
 def solid_box(lo,hi,step=3):
  axes=[np.linspace(lo[i],hi[i],max(2,int((hi[i]-lo[i])/step)+1)) for i in range(3)]
  g=np.array(np.meshgrid(*axes,indexing='ij')).reshape(3,-1).T
  pts.extend(g)
 S=P['support_offset']
 for x in(-76-S,76+S):
  solid_box([x-6,-78,-1.2],[x+6,-62,240])
  solid_box([x-5,-185,-1.2],[x+5,-175,240])
 solid_box([-90-S,-200,-6],[90+S,30,-1.2])
 # Two strips and the back of the deck avoid sampling its open head window.
 solid_box([-130-S,-210,240],[-45-S,-20,245]);solid_box([45+S,-210,240],[130+S,-20,245]);solid_box([-45-S,-210,240],[45+S,-85,245])
 for x in(-39.5-S,39.5+S):solid_box([x-.6,-32,148.2],[x+.6,-28,P['reaction_brace_z']],2)
 for sg in(-1,1):
  A=np.array([sg*85.,-70.]);B=np.array([sg*(39.5+S),-30.]);delta=B-A;normal=np.array([-delta[1],delta[0]])/np.linalg.norm(delta)
  for t in np.linspace(0,1,35):
   for d in(-1.5,0,1.5):
    xy=A+t*delta+d*normal
    for zz in(P['reaction_brace_z'],P['reaction_brace_z']+1.5,P['reaction_brace_z']+3):pts.append([xy[0],xy[1],zz])
 # Full horizontal spring-body/hook corridors for local return strokes.
 for item in its:
  if item.name not in('old_chassis_L','new_chassis_L'):continue
  T=getattr(item.shape,'_mesh_pose',None)
  if T is None:continue
  hx,ty,tz=T[:3,3]
  for zz,low in[(14.65,-12.5),(21.6,-2.5),(25.1,-5.9)]:
   for dx in np.arange(-1.4,1.41,.7):
    for dz in np.arange(-1.4,1.41,.7):
     if dx*dx+dz*dz>1.4**2:continue
     for yy in np.arange(low,18.81,1):pts.append([hx+18+dx,ty+yy,tz+zz+dz])
 return np.array(pts)
def run():
 b.make_parts();cache={};allroutes={};metrics=[]
 prior_path=b.ROOT.parent/'v0_9/output/validation/cable_routes.json'
 prior=json.loads(prior_path.read_text()) if prior_path.exists() else {}
 for k in(0,3,4,5,7):
  its,st=b.state(k);obstacles=cloud(its);rows=[]
  for spec in specs(st):
   seed=None
   for oldrows in prior.values():
    if abs(oldrows[0]['tip_y']-st['tip_y'])>.001 or abs(oldrows[0]['tip_z']-st['tip_z'])>.001:continue
    old=next(q for q in oldrows if q['name']==spec['name']);cp=np.array(old['controls']);ds=spec['start']-cp[0];de=spec['end']-cp[5]
    seed=np.r_[np.linalg.norm(cp[1]-cp[0]),np.linalg.norm(cp[4]-cp[5]),cp[2]+.6*ds+.4*de,cp[3]+.4*ds+.6*de];break
   route=solve(spec,obstacles,seed);cache[spec['name']]=route['seed'];pts=route['points']
   q={key:route[key] for key in('name','motor','branch','side','length','length_actual','min_bend_r','length_error')}
   q.update(state=k,tip_y=st['tip_y'],tip_z=st['tip_z'],points=pts.tolist(),controls=route['controls'].tolist(),sampled_clearance=float(cKDTree(obstacles).query(pts[7:-7])[0].min()))
   metrics.append({key:v for key,v in q.items() if key not in('points','controls')});rows.append(q);obstacles=np.concatenate((obstacles,pts[7:-7:2]))
   print('ROUTE',k,spec['name'],round(q['length_actual'],2),round(q['min_bend_r'],2),round(q['sampled_clearance'],2),flush=True)
  allroutes[str(k)]=rows
  (b.OUT/'validation/cable_routes.json').write_text(json.dumps(allroutes,indent=2))
  (b.OUT/'validation/cable_metrics.json').write_text(json.dumps(metrics,indent=2))
 print('ROUTES_DONE',len(metrics),flush=True)
if __name__=='__main__':run()
