"""Reference cable centre-lines. Fine wire is not a rigid interference body."""
import math,json
from functools import lru_cache
@lru_cache(None)
def routes(root):
 p=root/'output/validation/cable_routes.json'
 return json.loads(p.read_text()) if p.exists() else {}
def local_meshes(b,p):
 out=[];ty,tz=p['tip_y'],p['tip_z'];d=b.P['wire_d']
 for side,hx in(('old',-b.P['vial_pitch']/2),('new',b.P['vial_pitch']/2)):
  for tag,r,z,port,start,anchor,seat,phi,direction,exit_angle in(
   ('grip',10.25,12.5,(10.25,-18),10,(0,-9),13.2,p['twist']+p[side+'_relative'],-1,-360),
   ('twist',13,17.5,(-13,-18),10,(0,11.5),18.2,p['twist'],1,180),
   ('press',7.3,27.8,(-7.3,-15),7,(6,0),28.5,p['push_'+side]/20*120,1,180)):
   ph=math.radians(phi);ax=anchor[0]*math.cos(ph)-anchor[1]*math.sin(ph);ay=anchor[0]*math.sin(ph)+anchor[1]*math.cos(ph)
   a0=math.atan2(anchor[1],anchor[0])+ph;ae=math.radians(exit_angle)
   pts=[(ax,ay,seat),(ax,ay,z),(r*math.cos(a0),r*math.sin(a0),z)]
   steps=max(24,int(abs(ae-a0)*18))
   pts.extend((r*math.cos(a0+(ae-a0)*j/steps),r*math.sin(a0+(ae-a0)*j/steps),z)for j in range(1,steps+1))
   x=port[0];sg=-1;pts.append((x,-start,z))
   for j in range(1,17):
    a=-math.pi/2+j*math.pi/32;pts.append((x,-(start+8*math.cos(a)),z+8+8*math.sin(a)))
   pts.append((port[0],port[1],40.5))
   color={'grip':'#d0a142','twist':'#4f8eae','press':'#ba7295'}[tag]
   out.append(b.tube_mesh(side+'_'+tag+'_inner',[(hx+x,ty+y,tz+zz)for x,y,zz in pts],d/2,color,'wire'))
   out.append(b.tube_mesh(side+'_'+tag+'_upward_outer',[(hx+port[0],ty+port[1],tz+40.5),(hx+port[0],ty+port[1],tz+45.8)],b.P['housing_od']/2,color,'cable'))
  # Actual catalog-sized extension springs and local return tendons.
  import prototype
  for i,q in enumerate(prototype.RETURN):
   angle=p['twist']+p[side+'_relative'] if i==0 else p['twist'] if i==1 else p['push_'+side]/20*120
   rr=prototype.return_path(q,angle);sg=1 if q['positive']else-1
   # Anchor angles are selected to keep a winding reserve over the entire operating range.
   end=rr['tangent'];initial=end-sg*math.radians(q['reserve']);a0=initial+math.radians(angle-q['reference'])
   arc=[(q['r']*math.cos(a),q['r']*math.sin(a),q['z'])for a in __import__('numpy').linspace(a0,end,81)]
   points=arc+rr['points'][1:];out.append(b.tube_mesh(side+'_return_'+q['tag'],[(hx+x,ty+y,tz+z)for x,y,z in points],.15,'#80a7a0','wire'))
   moving=rr['hook_y'];fixed=18.;pts=[]
   for j in range(181):
    t=j/180;a=t*2*math.pi*40.5;y=moving+2+(fixed-moving-4)*t
    pts.append((hx+18+1.135*math.cos(a),ty+y,tz+q['z']+1.135*math.sin(a)))
   out.append(b.tube_mesh(side+'_JB14_'+q['tag'],pts,.115,'#b4b6ae','spring_actual'))
   for end,cy in [('fixed',fixed-.47),('moving',moving+.87)]:
    loop=[(hx+18,ty+cy+1.135*math.cos(t),tz+q['z']+1.135*math.sin(t))for t in __import__('numpy').linspace(0,2*math.pi,49)]
    out.append(b.tube_mesh(side+'_JB14_'+q['tag']+'_'+end+'_hook',loop,.115,'#b4b6ae','spring_actual'))
 # M4 normal-wire tangents are outside the columns and remain vertical.
 cy=b.P['root_y']+b.P['gear_cd'];r=b.P['joint_input_r']
 for j,xx in enumerate((-92-b.P['support_offset'],-90-b.P['support_offset'])):
  yy=cy+(-r if j==0 else r)
  out.append(b.tube_mesh('M4_normal_'+str(j),[(xx,yy,b.P['root_z']),(xx,yy,b.P['deck_z']+25)],d/2,'#e2a843','wire'))
 # M5 paired housings terminate on the upright elbow carrier, so parent rotation
 # does not itself change the inner/outer differential at these two sockets.
 for j,x in enumerate((30,32)):
  yy=p['elbow_y']-b.P['gear_cd']+(-r if j==0 else r)
  out.append(b.tube_mesh('M5_inner_'+str(j),[(x,yy,p['elbow_z']),(x,yy,p['elbow_z']+25)],d/2,'#d8a44b','wire'))
  out.append(b.tube_mesh('M5_outer_'+str(j),[(x,yy,p['elbow_z']+25),(x,yy,p['elbow_z']+29)],b.P['housing_od']/2,'#52616e','cable'))
 for rr in routes(b.ROOT).values():
  if abs(rr[0]['tip_y']-ty)>.001 or abs(rr[0]['tip_z']-tz)>.001:continue
  for r in rr:
   ok=abs(r['length_error'])<.3 and r['min_bend_r']>=30 and r['sampled_clearance']>=2.5 and r.get('segment_rigid_clearance_mm',-1)>=.5 and r.get('cable_pair_clearance_mm',-1)>=.5
   group_color='#c69a50' if r['name']in('M1_0','M3_0','M6_0') else '#579bae' if r['name']in('M2_0','M3_1','M7_0') else '#9b82ae'
   out.append(b.tube_mesh('route_'+r['name'],r['points'],b.P['housing_od']/2,group_color if ok else '#c85a54','route_candidate'))
  break
 return out


def envelope_meshes(b,p):
 out=[]
 for side,hx in(('old',-b.P['vial_pitch']/2),('new',b.P['vial_pitch']/2)):
  for z in(-16,3.5,19):
   pts=[(hx+b.P['rotation_envelope_r']*math.cos(j*math.pi/90),p['tip_y']+b.P['rotation_envelope_r']*math.sin(j*math.pi/90),p['tip_z']+z)for j in range(181)]
   out.append(b.tube_mesh(side+'_rotation_bound_'+str(z),pts,.13,'#c7934a','pitch_envelope'))
 return out
