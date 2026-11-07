import numpy as np
def segdist(P,Q):
 p=np.array(P);q=np.array(Q);u=np.diff(p,axis=0)[:,None,:];v=np.diff(q,axis=0)[None,:,:];w=p[:-1,None,:]-q[None,:-1,:]
 a=(u*u).sum(2);bb=(u*v).sum(2);c=(v*v).sum(2);d=(u*w).sum(2);e=(v*w).sum(2);D=a*c-bb*bb
 s=(bb*e-c*d)/np.maximum(D,1e-20);t=(a*e-bb*d)/np.maximum(D,1e-20)
 z=w+s[:,:,None]*u-t[:,:,None]*v;dist=np.where((D>1e-12)&(s>=0)&(s<=1)&(t>=0)&(t<=1),(z*z).sum(2),np.inf)
 for k in(0,1):
  ww=w+k*u;tt=np.clip((ww*v).sum(2)/c,0,1);z=ww-tt[:,:,None]*v;dist=np.minimum(dist,(z*z).sum(2))
  ww=w-k*v;ss=np.clip(-(ww*u).sum(2)/a,0,1);z=ww+ss[:,:,None]*u;dist=np.minimum(dist,(z*z).sum(2))
 return float(np.sqrt(dist.min()))
