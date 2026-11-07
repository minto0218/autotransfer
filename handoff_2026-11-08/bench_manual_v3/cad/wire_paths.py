"""Line and spring reference geometry for a static single-head manual bench."""
import math,numpy as np
import prototype
PORTS={'G':(10.25,-18,70),'T':(-13,-18,80),'P':(-7.3,-15,60)}
def lines(p):
 out=[]
 def add(name,pts,color,kind):out.append(dict(name=name,points=np.array(pts).round(4).tolist(),color=color,kind=kind))
 for i,(tag,r,z,start,anchor,seat,exit_angle)in enumerate([
  ('G',10.25,12.5,10,(0,-9),13.2,-360),('T',13,17.5,10,(0,11.5),18.2,180),('P',7.3,27.8,7,(6,0),28.5,180)]):
  angle=p['grip_angle']if i==0 else p['twist']if i==1 else p['push']/20*120
  ph=math.radians(angle);ax=anchor[0]*math.cos(ph)-anchor[1]*math.sin(ph);ay=anchor[0]*math.sin(ph)+anchor[1]*math.cos(ph)
  a0=math.atan2(anchor[1],anchor[0])+ph;ae=math.radians(exit_angle)
  pts=[(ax,ay,seat),(ax,ay,z),(r*math.cos(a0),r*math.sin(a0),z)];pts.extend((r*math.cos(a),r*math.sin(a),z)for a in np.linspace(a0,ae,97)[1:])
  x,yy,handle=PORTS[tag];pts.append((x,-start,z))
  pts.extend((x,-(start+8*math.cos(a)),z+8+8*math.sin(a))for a in np.linspace(-math.pi/2,0,25)[1:])
  pts.extend([(x,yy,40.5),(x,yy,handle+p['pull_mm'][i]+4)])
  add(tag+' 主糸',[(x,y,zz+42)for x,y,zz in pts],{'G':'#c9913c','T':'#4185a5','P':'#b5618a'}[tag],'main')
 for i,q in enumerate(prototype.RETURN):
  angle=p['grip_angle']if i==0 else p['twist']if i==1 else p['push']/20*120;rr=prototype.return_path(q,angle);sg=1 if q['positive']else-1;end=rr['tangent'];a0=end-sg*math.radians(q['reserve'])+math.radians(angle-q['reference'])
  arc=[(q['r']*math.cos(a),q['r']*math.sin(a),q['z'])for a in np.linspace(a0,end,81)];pts=arc+rr['points'][1:]
  add(q['tag']+' 戻し糸',[(x,y,z+42)for x,y,z in pts],'#558d7d','return')
  moving=rr['hook_y'];fixed=18.;pts=[]
  for t in np.linspace(0,1,405):
   a=t*2*math.pi*40.5;pts.append((18+1.135*math.cos(a),moving+2+(fixed-moving-4)*t,q['z']+42+1.135*math.sin(a)))
  add(q['tag']+' JB-14',pts,'#8c959d','spring')
  for label,cy in [('固定端',fixed-.47),('可動端',moving+.87)]:add(q['tag']+label,[(18,cy+1.135*math.cos(t),q['z']+42+1.135*math.sin(t))for t in np.linspace(0,2*math.pi,41)],'#8c959d','spring')
 return out
