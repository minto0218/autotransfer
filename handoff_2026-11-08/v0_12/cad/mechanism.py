"""Two central joint transmissions and two passive parallelograms.
The parallelograms preserve vertical head orientation during 2-DOF translation.
"""
import math
from head import involute_points

def make(b):
 globals().update({n:getattr(b,n) for n in('box','cyl','uni','cut','ring','rx','ry','hexagon','part','P')})
 S=P['support_offset'];baseline={}
 L1,L2,d=P['link1'],P['link2'],P['parallel_offset'];cd=P['joint_module']*(P['root_pin_teeth']+P['root_wheel_teeth'])/2+.12
 def active(L,end_r):
  sh=uni(box(3,L,8,(0,L/2,-4)),cyl(8,3,(-1.5,0,0),'x'),cyl(7,3,(-1.5,L,0),'x'))
  sh=cut(sh,ry(hexagon(5.25,5),90).translate((-2.5,0,0)),cyl(end_r,5,(-2.5,L,0),'x'))
  baseline[L]=sh.Volume()
  slot=uni(box(5,L-24,4,(0,L/2,-2)),cyl(2,5,(-2.5,12,0),'x'),cyl(2,5,(-2.5,L-12,0),'x'))
  return cut(sh,slot)
 part('arm_stage1',active(L1,5.2),'第1段の駆動アーム・根元六角座／先端丸軸受','arm')
 part('arm_stage2',active(L2,3.2),'第2段の駆動アーム・根元六角座／先端丸軸受','arm')
 b.META['arm_stage1']['before_refinement_volume_mm3']=baseline[L1]
 b.META['arm_stage2']['before_refinement_volume_mm3']=baseline[L2]
 for n,L in(('parallel_stage1',L1),('parallel_stage2',L2)):
  sh=uni(box(2.4,L,4,(0,L/2,-2)),cyl(4,2.4,(-1.2,0,0),'x'),cyl(4,2.4,(-1.2,L,0),'x'))
  sh=cut(sh,cyl(2.1,5,(-2.5,0,0),'x'),cyl(2.1,5,(-2.5,L,0),'x'))
  part(n,sh,'姿勢を保つ受動平行リンク '+n,'arm')
 def vertical(ri):
  sh=uni(box(2.4,5,d,(0,0,0)),cyl(7 if ri>4 else 5,2.4,(-1.2,0,0),'x'),cyl(4,2.4,(-1.2,0,d),'x'))
  return cut(sh,cyl(ri,5,(-2.5,0,0),'x'),cyl(2.1,5,(-2.5,0,d),'x'))
 # Elbow stator is a fixed-orientation carrier; M5 housing moves with it, not with arm1 angle.
 elbow=box(107+2*S,6,6,(0,-30,-3))
 for xx in(-52-S,52+S):
  q=uni(vertical(5.2).translate((xx,0,0)),box(3,30,6,(xx,-15,-3)))
  q=cut(q,cyl(5.2,6,(xx-3,0,0),'x'),cyl(2.1,6,(xx-3,0,d),'x'))
  elbow=uni(elbow,q)
 # Outboard support for the M5 input shaft, and vertical Bowden end seats.
 q=uni(box(2,16,4,(37,(-30-cd)/2,-2)),cyl(3.2,2,(36,-cd,0),'x'),box(2,4,26,(37,-30,-2)),box(9,36,2,(33.5,-cd,22)))
 q=cut(q,cyl(2.15,4,(35,-cd,0),'x'))
 for wx,yy in((30,-cd-P['joint_input_r']),(32,-cd+P['joint_input_r'])):
  q=uni(q,cyl(2.5,5,(wx,yy,24)))
  q=cut(q,cyl(1.35,4.1,(wx,yy,25)),cyl(.4,9,(wx,yy,21)))
 elbow=uni(elbow,q)
 for xx in(-3,3):elbow=cut(elbow,cyl(1.1,9,(xx,-35,0),'y'))
 part('elbow_stator',elbow,'垂直を保つ肘キャリア・M5中央ケースを固定する受け','arm')
 # End carrier has stub pins; no shaft crosses the hollow vial-head centres.
 end=box(88+2*S,6,3,(0,-30,10))
 for xx in(-42-S,42+S):
  q=uni(vertical(3.2).translate((xx,0,0)),box(2.4,30,3,(xx,-15,11)))
  q=cut(q,cyl(2.1,6,(xx-3,0,d),'x'))
  end=uni(end,q)
 for hx in(-P['vial_pitch']/2,P['vial_pitch']/2):
  for dx in(-5,5):end=cut(end,cyl(1.1,6,(hx+dx,-30,9)))
 for sg in(-1,1):
  q=uni(cyl(4,2.4,(sg*(54+S)-1.2,0,d),'x'),box(2.4,3,10,(sg*(54+S),0,d)),box(2.4,3,10,(sg*(42+S),0,d)),box(14,3,3,(sg*(48+S),0,21)))
  q=cut(q,cyl(2.1,5,(sg*(54+S)-2.5,0,d),'x'));end=uni(end,q)
 part('head_connector',end,'2独立ユニットをM2ねじで受ける連結台・垂直保持','arm')
 def keyed_shaft(x,L,seats,ro=5,ri=3):
  sh=b.ry(b.hexagon(ro,L),90).translate((x,0,0))
  if ri:sh=cut(sh,cyl(ri,L+2,(x-1,0,0),'x'))
  return sh
 part('root_output_shaft',keyed_shaft(-84-S,168+2*S,[(-59.5-S,-56.5-S),(-8,-2),(56.5+S,59.5+S)]),'中央M4から左右へ出力する共通中空軸','arm')
 part('elbow_output_shaft',keyed_shaft(-61-S,122+2*S,[(-47.5-S,-44.5-S),(-2,4),(44.5+S,47.5+S)]),'中央M5から左右へ出力する共通中空軸','arm')
 part('root_parallel_stub',cyl(2,22,(62+S,0,0),'x'),'根元受動リンクの左右別短軸・主アームと交差させない','hardware')
 part('elbow_parallel_axle',cyl(2,134+2*S,(-67-S,0,0),'x'),'肘受動リンクの共通軸','hardware')
 part('head_main_stub',cyl(3,8.5,axis='x'),'ヘッド主支点の短軸・中央を横切らない','hardware')
 part('head_parallel_stub',cyl(2,8.5,axis='x'),'ヘッド受動リンクの短軸','hardware')
 # Single stage compact transmission for each active joint.
 m=P['joint_module'];z1=P['root_pin_teeth'];z2=P['root_wheel_teeth'];cd=m*(z1+z2)/2+.12
 P['gear_cd']=cd;P['joint_ratio']=z2/z1
 def spur(z,phase=0):return b.cq.Workplane('XY').polyline(involute_points(m,z,phase,.07)).close().extrude(3).val()
 output=uni(ry(spur(z2,180/z2),90).translate((-8,0,0)),cyl(6.2,6,(-8,0,0),'x'))
 output=cut(output,ry(hexagon(5.25,9),90).translate((-9,0,0)))
 part('joint_output_gear',output,'38歯中央出力歯車・共通軸の六角座に結合','joint_gear')
 for tag,angle,sg in(('root',b.HOME_A,1),('elbow',b.HOME_C,-1)):
  hole=cyl(.8,20,(-14,sg*7.4*math.sin(math.radians(angle)),7.4*math.cos(math.radians(angle))),'x')
  part(tag+'_output_gear',cut(output,hole),'段階0の固定穴を持つ中央出力歯車 '+tag,'joint_gear')
 part('joint_home_lock_pin',uni(cyl(.7,16,(-13,0,0),'x'),cyl(2,1.5,(-14.5,0,0),'x')),'電源OFFの関節固定用・着脱ピン','lock')
 pin=ry(spur(z1),90).translate((-8,0,0))
 pin=cut(pin,ry(hexagon(2.2,5),90).translate((-9,0,0)))
 part('joint_input_pinion',pin,'18歯入力ピニオン・別部品として軸へ挿入','joint_gear')
 part('root_input_shaft',keyed_shaft(-96-S,97+S,[(-94-S,-88-S),(-8,-5)],2,0),'M4入力軸・外側巻取り輪から中央歯車へ','joint_gear')
 part('elbow_input_shaft',keyed_shaft(-14,54,[(-2,1),(28,34)],2,0),'M5入力軸・右側巻取り輪から中央歯車へ','joint_gear')
 def capstan():
  r=P['joint_input_r'];sh=cyl(r+.6,6,axis='x')
  for xx in(2,4):sh=cut(sh,ry(ring(r+2,r-P['wire_d']/2,1.2),90).translate((xx-.6,0,0)))
  sh=cut(sh,ry(hexagon(2.2,8),90).translate((-1,0,0)))
  for i,yy in enumerate((r-2,-r+2)):
   sh=cut(sh,cyl(.8,8,(-1,yy,0),'x'))
  return sh
 part('joint_input_drum',capstan(),'小径2溝巻取り輪・入力軸の六角座へ','joint_gear')
 # Both case plates have bearing holes and a pair of spacer holes.
 for name,x in(('joint_case_back',-12),('joint_case_front',-2)):
  sh=box(2,36,23,(x+1,6.5,-11.5))
  sh=cut(sh,cyl(6.4 if name.endswith('front') else 5.2,4,(x-1,0,0),'x'),cyl(2.15,4,(x-1,cd,0),'x'),cyl(2.2,4,(x-1,0,d),'x'))
  for zz in(-11,11):sh=cut(sh,cyl(1.1,4,(x-1,cd/2,zz),'x'))
  part(name,sh,'中央ギアケースの軸受板 '+name,'joint_case')
 part('joint_case_spacer',cut(cyl(2.5,8,axis='x'),cyl(1.1,10,(-1,0,0),'x')),'ケースの前後板をつなぐスペーサー','joint_case')
 # Mount feet meet the frame trays without volume overlap.
 part('root_case_foot',box(14,5,6,(-6,-12.5,-3)),'中央根元ケース取付足・固定フレームの受けへ','joint_case')
 part('elbow_case_foot',box(14,4,6,(-6,-25,-3)),'中央先端ケース取付足・肘キャリアの受けへ','joint_case')
 for tag,backward in(('root',False),('elbow',True)):
  flip=lambda sh:sh.mirror('XZ') if backward else sh
  sh=uni(flip(b.PARTS['joint_case_back']),flip(b.PARTS['joint_case_front']),b.PARTS[tag+'_case_foot'])
  for zz in(-11,11):sh=uni(sh,flip(b.PARTS['joint_case_spacer'].translate((-10,cd/2,zz))))
  if backward:sh=cut(sh,box(30,20,40,(-6,17,-20)))
  sh=cut(sh,cyl(.8,20,(-14,0,7.4),'x'))
  for xx in(-9,-3):sh=cut(sh,cyl(1.1,9,(xx,-30 if backward else -19,0),'y'))
  for xx in(-9,-3):
   yy=-25.5 if backward else -12.5
   pocket=b.rx(hexagon(2.45,1.8),-90).translate((xx,yy,0))
   sh=cut(sh,pocket,box(4.9,1.8,3,(xx,yy+.9,-3)))
  part(tag+'_case_chassis',sh,'中央'+tag+'歯車の一体軸受枠・側方から歯車を入れて軸を挿入','joint_case')
 for tag,start,L,ny in [('root',-21,12,-12.4),('elbow',-33,10,-25.4)]:
  part(tag+'_mount_M2_bolt',uni(cyl(.75,L,(0,start,0),'y'),cyl(1.8,2,(0,start-2,0),'y')),'中央ケース取付M2・ナットは足下面から挿入','hardware')
  nut=cut(b.rx(hexagon(2.3,1.6),-90).translate((0,ny,0)),cyl(1,2,(0,ny-.1,0),'y'))
  part(tag+'_mount_M2_nut',nut,'中央ケース足の下面開放ナットポケットへ','hardware')
 # Bearings for long input shafts are outside the winding grooves.
 part('input_support_bush',cut(cyl(3.2,2,axis='x'),cyl(2.15,4,(-1,0,0),'x')),'入力軸の外側支持ブッシュ','hardware')
 # All pads and holders stay on the inner side of the two vials.
 h=uni(ring(14,11.8,12),cyl(12,1.2,(0,0,-1.2)))
 h=cut(h,box(32,40,16,(-16,0,-2)))
 for yy in(-12,12):h=uni(h,box(5,5,1.2,(8,yy,-1.2)))
 for yy in(-12,12):h=cut(h,cyl(1.1,4,(8,yy,-2)))
 for yy in(-12,12):h=cut(h,cyl(2,2.1,(8,yy,0)))
 part('holder_old_inner',h,'旧側ホルダー：中央側だけ保持・外側から供給','holder')
 part('holder_new_inner',h.mirror('YZ'),'新側ホルダー：中央側だけ保持・外側から供給','holder')

def place(b,add,pose):
 P=b.P;S=P['support_offset'];ry,rz=P['root_y'],P['root_z'];a,c=pose['a'],pose['c'];ey,ez=pose['elbow_y'],pose['elbow_z'];ty,tz=pose['tip_y'],pose['tip_z'];d=P['parallel_offset'];L1,L2=P['link1'],P['link2'];ratio=P['joint_ratio'];cd=P['gear_cd']
 def at(n,p,point,ang=0):add(n,p,s=b.rx(b.PARTS[p],ang),at=point)
 for sg in(-1,1):
  at('stage1_main_'+str(sg),'arm_stage1',(sg*(58+S),ry,rz),a)
  at('stage1_parallel_'+str(sg),'parallel_stage1',(sg*(64+S),ry,rz+d),a)
  at('stage2_main_'+str(sg),'arm_stage2',(sg*(46+S),ey,ez),c)
  at('stage2_parallel_'+str(sg),'parallel_stage2',(sg*(49.3+S),ey,ez+d),c)
  if sg>0:
   at('head_main_pin_R','head_main_stub',(40.5+S,ty,tz));at('head_parallel_pin_R','head_parallel_stub',(47.5+S,ty,tz+d))
  else:
   add('head_main_pin_L','head_main_stub',s=b.PARTS['head_main_stub'].mirror('YZ'),at=(-40.5-S,ty,tz));add('head_parallel_pin_L','head_parallel_stub',s=b.PARTS['head_parallel_stub'].mirror('YZ'),at=(-47.5-S,ty,tz+d))
 at('root_main_shaft','root_output_shaft',(0,ry,rz),a)
 at('elbow_main_shaft','elbow_output_shaft',(0,ey,ez),c)
 at('root_parallel_pin_R','root_parallel_stub',(0,ry,rz+d))
 add('root_parallel_pin_L','root_parallel_stub',s=b.PARTS['root_parallel_stub'].mirror('YZ'),at=(0,ry,rz+d))
 at('elbow_parallel_shaft','elbow_parallel_axle',(0,ey,ez+d))
 at('elbow_vertical_carrier','elbow_stator',(0,ey,ez))
 at('head_vertical_carrier','head_connector',(0,ty,tz))
 for tag,y,z,theta,backward in(('M4',ry,rz,a,False),('M5',ey,ez,c,True)):
  def put(s):return s.mirror('XZ') if backward else s
  gp='elbow_output_gear' if backward else 'root_output_gear'
  add(tag+'_output',gp,s=b.rx(put(b.PARTS[gp]),theta),at=(6 if backward else 0,y,z))
  if pose.get('lock_on'):at(tag+'_home_lock','joint_home_lock_pin',(6 if backward else 0,y,z+7.4))
  add(tag+'_pinion','joint_input_pinion',s=b.rx(put(b.PARTS['joint_input_pinion']),-ratio*theta),at=(6 if backward else 0,y+(-cd if backward else cd),z))
  p='elbow_case_chassis' if backward else 'root_case_chassis';at(tag+'_case',p,(6 if backward else 0,y,z))
  for xx in(-9,-3):
   pre='elbow'if backward else'root'
   at(tag+'_mountbolt_'+str(xx),pre+'_mount_M2_bolt',(xx+(6 if backward else 0),y,z))
   at(tag+'_mountnut_'+str(xx),pre+'_mount_M2_nut',(xx+(6 if backward else 0),y,z))
  p='elbow_input_shaft' if backward else 'root_input_shaft'
  add(tag+'_input_shaft',p,s=b.rx(b.PARTS[p],-ratio*theta),at=(0,y+(-cd if backward else cd),z))
  xx=28 if backward else -94-S
  add(tag+'_input_drum','joint_input_drum',s=b.rx(b.PARTS['joint_input_drum'],-ratio*theta),at=(xx,y+(-cd if backward else cd),z))
