"""Reuse local tessellations under exact tracked rigid transforms.
CAD geometry still uses CadQuery's original transforms; this only accelerates HTML.
"""
import numpy as np
import cadquery as cq
_translate=cq.Shape.translate
_rotate=cq.Shape.rotate
CACHE={}
def _v(p):return np.array(p.toTuple() if hasattr(p,'toTuple') else p,float)
def translate(self,vector):
 out=_translate(self,vector)
 if hasattr(self,'_mesh_key'):
  T=np.eye(4);T[:3,3]=_v(vector);out._mesh_key=self._mesh_key;out._mesh_pose=T@self._mesh_pose
 return out
def rotate(self,start,end,deg):
 out=_rotate(self,start,end,deg)
 if hasattr(self,'_mesh_key'):
  p=_v(start);u=_v(end)-p;u/=np.linalg.norm(u);t=np.radians(deg)
  K=np.array([[0,-u[2],u[1]],[u[2],0,-u[0]],[-u[1],u[0],0]])
  R=np.eye(3)*np.cos(t)+(1-np.cos(t))*np.outer(u,u)+np.sin(t)*K
  T=np.eye(4);T[:3,:3]=R;T[:3,3]=p-R@p
  out._mesh_key=self._mesh_key;out._mesh_pose=T@self._mesh_pose
 return out
cq.Shape.translate=translate
cq.Shape.rotate=rotate
def tag(parts):
 CACHE.clear()
 for n,s in parts.items():s._mesh_key=n;s._mesh_pose=np.eye(4)
def mesh(item,parts):
 q=item;s=q.shape
 if hasattr(s,'_mesh_key'):
  n=s._mesh_key
  if n not in CACHE:
   v,f=parts[n].tessellate(.24,.25);CACHE[n]=(np.array([[p.x,p.y,p.z] for p in v]),f)
  v,f=CACHE[n];T=s._mesh_pose;v=v@T[:3,:3].T+T[:3,3]
 else:
  vv,f=s.tessellate(.24,.25);v=np.array([[p.x,p.y,p.z] for p in vv])
 return dict(name=q.name,part=q.part,group=q.group,color=q.color,reference=q.reference,v=v.round(4).tolist(),f=f)
