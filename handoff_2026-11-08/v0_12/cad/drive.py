"""Seven fixed upper servos, four compact 2:1 speed-up cartridges and three direct inputs."""
import math
from head import involute_points
POSITIONS=[]
def make(b):
 globals().update({n:getattr(b,n) for n in('box','cyl','uni','cut','ring','ry','hexagon','part','P')})
 global POSITIONS
 S=P['support_offset']
 front=P['root_y']+P['gear_cd']-13.62
 POSITIONS[:]=[(-60,-115),(60,-115),(0,-115),(-112.25-S,front),(72+S,front),(-40,-180),(40,-180)]
 plate=cut(box(3,23,38.5,(11.7,0,-19.25)),box(5,13,23.6,(11.7,0,-11.8)))
 for zz in(-14.2,14.2):plate=cut(plate,cyl(.8,5,(9.5,0,zz),'x'))
 direct=uni(plate,box(36,26,3,(-4,0,-20)))
 for xx in(-12,7):
  for yy in(-8.5,8.5):direct=cut(direct,cyl(1.2,5,(xx,yy,-21)))
 part('servo_direct_mount',direct,'MG90D直接巻取り台・フランジと本体逃げ','drive')
 step=uni(plate,box(49,38,3,(2.5,6,-20)))
 for xx in(12.25,24.25):
  q=box(2,14,32,(xx+1,13.62,-20));q=cut(q,cyl(2.15,4,(xx-1,13.62,0),'x'));step=uni(step,q)
 for xx in(-12,20):
  for yy in(-7,19):step=cut(step,cyl(1.2,5,(xx,yy,-21)))
 part('servo_stepup_mount',step,'小型36/18歯の増速支持台・90度サーボで大きな巻取り角を確保','drive')
 def spur(z):return ry(b.cq.Workplane('XY').polyline(involute_points(.5,z,0,.07)).close().extrude(3).val(),90)
 driver=uni(spur(36).translate((14.25,0,0)),cyl(6,1,(17.25,0,0),'x'))
 driver=cut(driver,cyl(3.2,6,(13.25,0,0),'x'))
 for yy in(-5.5,5.5):driver=cut(driver,cyl(.8,6,(13.25,yy,0),'x'))
 part('upper_driver36',driver,'上部増速用36歯・ホーン取付穴','drive')
 pin=spur(18).translate((14.25,13.62,0));pin=cut(pin,ry(hexagon(2.2,5),90).translate((13.25,13.62,0)))
 part('upper_pinion18',pin,'上部増速用18歯・入力の反対向きに2倍回転','drive')
 shaft=ry(hexagon(2,20),90).translate((8.25,13.62,0))
 part('upper_keyed_shaft',shaft,'増速巻取り輪の六角駆動座・両側ジャーナル','drive')
 def drum(r,h,paired=False,hexhole=True):
  sh=cyl(r+.8,h,axis='x')
  for j,xx in enumerate((2,4) if paired else (h/2,)):
   sh=cut(sh,ry(ring(r+2,r-P['wire_d']/2,1.2),90).translate((xx-.6,0,0)))
   yy=(r-2)*(1 if j==0 else -1);sh=cut(sh,cyl(.8,h+2,(-1,yy,0),'x'))
  sh=cut(sh,ry(hexagon(2.2,h+2),90).translate((-1,0,0)) if hexhole else cyl(3.2,h+2,(-1,0,0),'x'))
  if not hexhole:
   for yy in(-5.5,5.5):sh=cut(sh,cyl(.8,h+2,(-1,yy,0),'x'))
  return sh
 part('upper_grip_drum',drum(12,6),'把持入力の巻取り輪・上部増速軸へ','drive')
 part('upper_joint_drum',drum(P['joint_input_r'],6,True),'引抜き2軸用の2溝輪・下側と同径','drive')
 part('upper_direct_drum',drum(13,5,False,False),'ねじり／押込みの直接巻取り輪','drive')
 duo=uni(drum(13,5,False,False),drum(13,5,False,False).translate((6,0,0)),ry(ring(5.3,3.2,1),90).translate((5,0,0)))
 for yy in(-5.5,5.5):duo=cut(duo,cyl(.8,13,(-1,yy,0),'x'))
 part('upper_twist_dual_drum',duo,'共通ねじりの2溝輪を一体化・空回りする接続軸を廃止','drive')
 deck=box(260+2*S,190,5,(0,-115,P['deck_z']))
 deck=cut(deck,box(90+2*S,100,8,(0,-35,P['deck_z']-1)))
 for i,(mx,my) in enumerate(POSITIONS):
  stepped=i in(0,1,3,4)
  for xx in((-12,20) if stepped else (-12,7)):
   for yy in((-7,19) if stepped else (-8.5,8.5)):deck=cut(deck,cyl(1.2,8,(mx+xx,my+yy,P['deck_z']-1)))
  if i==3:continue
  for xx,yy in top_ends(i+1):
   q=cyl(2.5,5,(xx,yy,P['deck_z']-3));deck=uni(deck,q)
   deck=cut(deck,cyl(1.35,4.1,(xx,yy,P['deck_z']-3.1)),cyl(.4,8,(xx,yy,P['deck_z'])))
 # Ordinary root wires use aligned, equal-radius tangents on both winding wheels.
 for xx in(-92-S,-90-S):
  for yy in(P['root_y']+P['gear_cd']-P['joint_input_r'],P['root_y']+P['gear_cd']+P['joint_input_r']):deck=cut(deck,cyl(.5,8,(xx,yy,P['deck_z']-1)))
 part('upper_deck',deck,'2＋3＋2配置・退避頭上の開口・配線貫通穴','frame')

 # Right bracket: a diagonal upper rib above the moving carriers and a short stop.
 z=P['reaction_brace_z'];A=(70+S,P['root_y']);B=(39.5+S,-30);dx,dy=B[0]-A[0],B[1]-A[1];L=math.hypot(dx,dy);nx,ny=-dy/L*2,dx/L*2
 beam=b.cq.Workplane('XY').polyline([(A[0]+nx,A[1]+ny),(B[0]+nx,B[1]+ny),(B[0]-nx,B[1]-ny),(A[0]-nx,A[1]-ny)]).close().extrude(3).val().translate((0,0,z))
 bracket=uni(beam,box(2,12,22,(69+S,P['root_y'],z-10)),box(1.2,4,z-148.2,(B[0],B[1],148.2)))
 bracket=cut(bracket,box(12,16,245,(76+S,P['root_y'],0)))
 for zz in(z-6,z+8):bracket=cut(bracket,cyl(1.1,5,(66.5+S,P['root_y'],zz),'x'))
 part('column_reaction_bracket',bracket,'柱に固定する反力ブラケット・縦部56.8mm・上板吊り棒を置換','frame')
 part('reaction_M2_screw',uni(cyl(.85,10,(68+S,0,0),'x'),cyl(1.8,1.5,(66.5+S,0,0),'x')),'柱側反力ブラケットのM2ねじ・ねじ山省略','hardware')

def top_ends(mid):
 mx,my=POSITIONS[mid-1]
 if mid in(1,2):return[(mx+21.25,my+13.62-12)]
 if mid==3:return[(mx+20.75,my+13),(mx+26.75,my+13)]
 if mid==5:return[(mx+20.25,my+13.62-P['joint_input_r']),(mx+22.25,my+13.62+P['joint_input_r'])]
 if mid==4:return[]
 return[(mx+20.75,my+13)]

def commands(b,pose):
 d0=pose.get('old_relative',-math.degrees((35-pose['gap'])/12));d1=pose.get('new_relative',d0);tw=pose['twist'];r=b.P['joint_ratio']
 rel=[-(tw+d0)*10.25/24,-(tw+d1)*10.25/24,tw,(pose['a']-b.HOME_A)*r/2,(pose['c']-b.HOME_C)*r/2,pose['push_old']/20*120*7.3/13,pose['push_new']/20*120*7.3/13]
 offsets=[14,14,45,2,6,10,10]
 return rel,[a+o for a,o in zip(rel,offsets)]

def place(b,add,pose):
 for sg in(-1,1):
  q=b.PARTS['column_reaction_bracket'];add('reaction_bracket_'+str(sg),'column_reaction_bracket',s=q if sg>0 else q.mirror('YZ'))
  for zz in(P['reaction_brace_z']-6,P['reaction_brace_z']+8):
   q=b.PARTS['reaction_M2_screw'];add('reaction_screw_'+str(sg)+'_'+str(zz),'reaction_M2_screw',s=q if sg>0 else q.mirror('YZ'),at=(0,P['root_y'],zz))
 rel,cmd=commands(b,pose);pose['servo_relative']=rel;pose['servo_nominal_90']=cmd;z=P['deck_z']+25
 for i,((mx,my),a) in enumerate(zip(POSITIONS,rel)):
  at=(mx,my,z);tag='M'+str(i+1)
  add(tag+'_servo','ref_servo',at=at,ref=True)
  if i in(0,1,3,4):
   add(tag+'_mount','servo_stepup_mount',at=at)
   add(tag+'_driver','upper_driver36',s=b.rx(b.PARTS['upper_driver36'],a),at=at)
   # The output axis is offset in Y. Rotate around its own axis before translating.
   for p in('upper_pinion18','upper_keyed_shaft'):
    sh=b.PARTS[p].translate((0,-13.62,0));sh=b.rx(sh,-2*a).translate((0,13.62,0));add(tag+'_'+p,p,s=sh,at=at)
   p='upper_grip_drum' if i in(0,1) else 'upper_joint_drum'
   add(tag+'_drum',p,s=b.rx(b.PARTS[p],-2*a),at=(mx+18.25,my+13.62,z))
  else:
   add(tag+'_mount','servo_direct_mount',at=at)
   pp='upper_twist_dual_drum' if i==2 else 'upper_direct_drum'
   add(tag+'_drum',pp,s=b.rx(b.PARTS[pp],a),at=(mx+18.25,my,z))
