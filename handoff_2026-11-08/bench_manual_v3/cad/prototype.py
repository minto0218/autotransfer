"""Assembly and FDM provisions for V0.12. All dimensions mm.
The rear extension-spring cassette is removable and uses local PE return tendons.
"""
import math
import numpy as np
SPLITS={}
RETURN=[dict(tag='grip',r=4.,z=14.65,lane=-12,positive=True,reference=30.,reserve=30.),dict(tag='twist',r=4.,z=21.6,lane=-4,positive=False,reference=0.,reserve=105.),dict(tag='press',r=3.6,z=25.1,lane=4,positive=False,reference=0.,reserve=45.)]

def return_path(q,angle=0):
 # Common tangent to a free idler; its +Y exit aligns with the horizontal spring.
 r=q['r'];R=4.;C=np.array([14.,-24.]);d=np.linalg.norm(C);phi=math.atan2(C[1],C[0])
 th=phi-math.acos((r-R)/d)if q['positive']else phi+math.acos((r+R)/d)
 n=np.array([math.cos(th),math.sin(th)]);T=r*n;U=C+R*n if q['positive']else C-R*n
 beta=math.atan2(U[1]-C[1],U[0]-C[0]);end=0.
 while end<beta:end+=2*math.pi
 points=[(*T,q['z']),(*U,q['z'])]
 points.extend((C[0]+R*math.cos(t),C[1]+R*math.sin(t),q['z'])for t in np.linspace(beta,end,49)[1:])
 travel=r*math.radians((q['reference']-angle)if q['positive']else(angle-q['reference']))
 hook=2-travel;points.append((18.,hook,q['z']))
 return dict(points=points,tangent=th,hook_y=hook,spring_length=18-hook,travel=travel,idler_center=[14.,-24.,q['z']],guide_points=points[1:-1])

def apply(b):
 global SPLITS
 box,cyl,uni,cut,ring,part=b.box,b.cyl,b.uni,b.cut,b.ring,b.part
 # Jaws and contact pads are one printable part; no unsupported butt joint.
 part('parallel_jaw_rack',uni(b.PARTS['parallel_jaw_rack'],b.PARTS['contact_pad_5mm']),'爪ラックと5mmパッドを一体化・Cガイド端から挿入','grip_link')
 # Separate the gear from the drum without changing the 24-tooth envelope.
 whole=b.PARTS['grip_drum_pinion'];gear=whole.intersect(box(40,40,3,(0,0,7.3)))
 hub=b.cq.Workplane('XY').polygon(6,7.9).extrude(3.5).val().translate((0,0,7.1))
 gear=cut(gear,hub)
 drum=whole.cut(box(40,40,3.3,(0,0,7.0)))
 key=b.cq.Workplane('XY').polygon(6,7.5).extrude(3.0).val().translate((0,0,7.3));key=cut(key,cyl(3.2,5,(0,0,6.5)))
 drum=uni(drum,key)
 # A lower retaining washer is screwed to two pilot holes in the hub from below.
 for x in(-4.1,4.1):
  gear=cut(gear,cyl(.7,4,(x,0,7)),cyl(1.05,1.1,(x,0,7.2)))
  drum=cut(drum,cyl(.55,8,(x,0,6.5)),cyl(1.05,1.1,(x,0,7.2)))
  # Clearance holes lie outside the central hex; screw shoulders retain the insert.
 drum=uni(drum,ring(4.4,3.2,1.4,14))
 drum=cut(drum,ring(4.7,3.65,.6,14.35))
 part('grip_drum_pinion',drum,'専用把持ドラム・六角座で別体24歯ピニオンを駆動','head')
 part('grip_pinion_insert',gear,'m0.5/24歯/幅3・試作用印刷ピニオン・市販品は穴と厚みの追加加工が必要','head')
 part('pinion_M14_screw',uni(cyl(.5,5.3,(0,0,8.3)),cyl(.95,1,(0,0,7.3))),'別体ピニオン抜け止めM1.4×6・印刷下穴をさらってねじ込む','hardware')
 # Main pusher enters from below; the removable top drive and cross pin avoid trapping.
 rod=b.PARTS['push_rotating_plunger'];rod=cut(rod,cyl(.58,8,(-4,0,22),'x'))
 part('push_rotating_plunger',rod,'押し足一体棒・上ドラム別体・Ø1横ピンを後挿しする','pusher')
 part('pusher_follower_pin',cyl(.5,6.3,(-3.15,0,22),'x'),'Ø1×6.3フォロワ横ピン・金属丸棒推奨／印刷試験片も同梱','hardware')
 # Twist return spool above the bearing clamp, connected to the upper drum by risers.
 top=b.PARTS['twist_upper_drum']
 hub=ring(4.65,3.4,2,20.6);hub=cut(hub,ring(5,3.65,.8,21.2))
 for sg in(-1,1):
  hub=uni(hub,box(2.5,3,3.1,(sg*10.5,0,19)),box(7.6,2,.55,(sg*7.4,0,20.6)))
  hub=cut(hub,cyl(.8,4.5,(sg*10.5,0,18.8)))
  top=cut(top,cyl(.55,3,(sg*10.5,0,16.5)))
 hub=cut(hub,ring(5,3.65,.8,21.2))
 part('twist_upper_drum',top,'上中空ドラム・戻し溝はケースを閉じた後に別体で装着','head')
 part('twist_return_spool',hub,'着脱式ねじり戻し溝・前方から入れてM1.4×5で固定','head')
 part('return_spool_M14_screw',uni(cyl(.5,5,(0,0,17.1)),cyl(1,1,(0,0,22.1))),'ねじり戻し溝を後組みする小頭M1.4×5','hardware')
 p=b.PARTS['push_sliding_drive'];p=uni(p,ring(4.15,1.5,1.2,24.5));p=cut(p,ring(4.4,3.25,.6,24.8))
 part('push_sliding_drive',p,'着脱式押込みドラム・主糸と戻し糸を別溝へ','pusher')
 # Knot pockets for local return tendons. Accessible before closing the clamshell.
 for name,q in zip(('grip_drum_pinion','twist_return_spool','push_sliding_drive'),RETURN):
  th=return_path(q)['tangent'];base=th-math.radians(q['reserve'])-math.radians(q['reference'])if q['positive']else th+math.radians(q['reserve'])-math.radians(q['reference'])
  x,y=q['r']*math.cos(base),q['r']*math.sin(base);z=q['z']
  p=b.PARTS[name]
  if name=='grip_drum_pinion':p=cut(p,cyl(.4,2,(x,y,z-.3)),cyl(.6,.8,(x,y,z+.1)))
  else:p=cut(p,cyl(.4,5,(x,y,z-1.5)),cyl(.8,.8,(x,y,z+.1)))
  part(name,p,b.META[name]['description'],b.META[name]['group'])
 # The return ring itself must open around the central cam; a closed ring cannot enter sideways.
 spool=b.PARTS['twist_return_spool']
 for sg in(-1,1):part('twist_return_spool_'+('L'if sg<0 else'R'),spool.intersect(box(60,60,20,(sg*30,0,10))),'後組みする半割ねじり戻し溝・上ドラムへ各1本で留める','head')
 # Rear cross-bolts close the two case halves; the case is not a closed captive ring.
 case=b.PARTS['module_chassis']
 for z in(27,34.5):
  case=uni(case,box(19,6,4,(0,-30,z-2.5)))
  case=cut(case,cyl(1.1,22,(-11,-30,z),'x'),cyl(2,2.5,(-10.5,-30,z),'x'),b.ry(b.hexagon(2.45,2.4),90).translate((6.5,-30,z)))
 for xx in(-5,5):case=cut(case,cyl(1.1,12,(xx,-30,12.5)),b.hexagon(2.45,2.1,16).translate((xx,-30,0)))
 # Lay-in main PTFE-lined fairleads with screw-on covers; no buried support channel.
 for tag,xx,yy,zz,sg in [('G',10.25,-10,20.5,1),('T',-13,-10,25.5,-1),('P',-7.3,-7,35.8,-1)]:
  by=yy-11/math.sqrt(2);bz=zz-11/math.sqrt(2)
  boss=cyl(2,3,(xx-1.5,by,bz),'x')
  bridge=box(3,4,4,(xx,by+1,bz))
  case=uni(case,boss,bridge)
  # Broaden the liner channel and open it toward the removable cover.
  tool=cut(cyl(8.9,5,(xx-.9 if sg>0 else xx-4.1,yy,zz),'x'),cyl(7.1,7,(xx-5,yy,zz),'x'))
  tool=tool.intersect(box(8,12,12,(xx,yy-6,zz-12)))
  case=cut(case,tool,cyl(.6,6,(xx-3,by,bz),'x'))
  face=xx+1 if sg>0 else xx-2
  cover=cut(cyl(9.5,1,(face,yy,zz),'x'),cyl(6.5,3,(face-1,yy,zz),'x')).intersect(box(8,12,12,(xx,yy-6,zz-12)))
  cover=uni(cover,cyl(2,1,(face,by,bz),'x'),box(1,4,4,(face+.5,by+1,bz)))
  cover=cut(cover,cyl(.8,3,(face-1,by,bz),'x'))
  case=cut(case,cover,cover.translate((-sg*.12,0,0)))
  part('fairlead_cover_'+tag,cover,'可開式'+tag+'糸案内の蓋・PTFEライナーを後から置ける','head_fixed')
  bolt=uni(cyl(.5,4,(xx-2,by,bz),'x'),cyl(1.3,1,(xx+2,by,bz),'x'))
  if sg<0:bolt=bolt.mirror('YZ',(xx,0,0))
  part('fairlead_screw_'+tag,bolt,'案内蓋M1.4×4・ケース下穴をさらって締結','hardware')
 # Positive anti-rotation key for both split cam halves.
 case=uni(case,box(1.4,.8,.6,(0,-3.2,19.7)))
 for n in('push_cam_left','push_cam_right'):
  sh=cut(b.PARTS[n],box(6,1.2,.9,(0,-3.2,19.55)))
  part(n,sh,b.META[n]['description']+'・固定キー溝','pusher_fixed')
 # Increase the push-rod upper guide clearance for FDM and remove narrow blind passages.
 case=cut(case,cyl(1.6,9,(0,0,28.5)))
 for x,y in((10.25,-18),(-13,-18),(-7.3,-15)):case=cut(case,cyl(.55,11,(x,y,31.5)))
 for zz in(24,32):case=cut(case,cyl(.85,9,(0,-35,zz),'y'))
 for sg in(-1,1):
  sh=case.intersect(box(100,150,120,(sg*50,0,-25)))
  part('module_case_'+('L'if sg<0 else'R'),sh,'開いて回転部・カム・棒を挟むケース半割','head_fixed')
 part('case_M2_bolt',uni(cyl(.75,16,(-8,-30,0),'x'),cyl(1.8,2,(-10,-30,0),'x')),'ケース横締めM2×16・工具は側方から','hardware')
 part('case_M2_nut',cut(b.ry(b.hexagon(2.3,1.6),90).translate((6.6,-30,0)),cyl(1,3,(6,-30,0),'x')),'ケース横締めM2ナット・側面六角ポケットへ','hardware')
 # One common side plate for all three horizontal extension springs.
 # Rounded mount, curved rib, and contoured common spring plate.
 rail=b.cq.Workplane('XZ').center(0,39.5).slot2D(24,5).extrude(2).val().translate((0,-34,0))
 ts=np.linspace(0,1,41);p0=np.array([8.5,-35.]);p1=np.array([17.,-35.]);p2=np.array([23.,-31.]);p3=np.array([23.,-12.]);path=[];left=[];right=[]
 for t in ts:
  pt=(1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3
  tangent=3*(1-t)**2*(p1-p0)+6*(1-t)*t*(p2-p1)+3*t*t*(p3-p2);n=np.array([-tangent[1],tangent[0]])/np.linalg.norm(tangent)
  path.append(pt);left.append(tuple(pt+1.5*n));right.append(tuple(pt-1.5*n))
 beam=b.cq.Workplane('XY').polyline(left+right[::-1]).close().extrude(3).val().translate((0,0,35.5))
 for pt in(path[0],path[-1]):beam=uni(beam,cyl(1.5,3,(*pt,35.5)))
 plate=(b.cq.Workplane('YZ').moveTo(-18,14).lineTo(-18,35)
  .threePointArc((-16.8,38),(-14,38.5)).threePointArc((-11,38),(-10,35))
  .lineTo(-10,31.5).threePointArc((-8.8,29),(-6,28.5)).lineTo(17.5,28.5)
  .threePointArc((22,26),(22,23)).lineTo(22,16).threePointArc((20,12),(16,12))
  .lineTo(-14,12).threePointArc((-17,12.5),(-18,14)).close().extrude(3).val().translate((21.5,0,0)))
 rail=uni(rail,beam,plate)
 def paddle(zz):
  disk=cyl(5.2,.8,(14,-24,zz))
  neck=b.cq.Workplane('XY').polyline([(16,-27),(24.5,-19),(24.5,-16),(22,-15),(15.5,-21)]).close().extrude(.8).val().translate((0,0,zz))
  return uni(disk,neck)
 for q in RETURN:
  zz=q['z']
  # Open-front wheel slots: place the wheels laterally, then insert one common axle.
  shelf=paddle(zz-1.6)
  roof=paddle(zz+.8)
  rail=uni(rail,shelf,roof)
  rail=cut(rail,cyl(1.05,4,(14,-24,zz-2)))
  rail=cut(rail,cyl(.65,11,(15,18,zz),'x'))
 for x in(-10,10):
  rail=cut(rail,cyl(1.1,14,(x,-40,39),'y'))
  pilot=cyl(.85,8,(x,-35,39),'y')
  for name in('module_case_L','module_case_R'):
   sh=b.PARTS[name]
   if (x<0 and name.endswith('L'))or(x>0 and name.endswith('R')):sh=uni(sh,box(4,6,7,(x,-30,34.5)))
   sh=cut(sh,pilot);part(name,sh,b.META[name]['description'],'head_fixed')
 # Wheel clearance only removes fixed-case material and preserves the upper webs.
 for name in('module_case_L','module_case_R'):
  sh=b.PARTS[name]
  for q in RETURN:sh=cut(sh,cyl(5.4,3.8,(14,-24,q['z']-1.9)))
  sh=cut(sh,rail)
  for zz in(27,34.5):sh=cut(sh,cyl(1.1,22,(-11,-30,zz),'x'),cyl(2,2.5,(-10.5,-30,zz),'x'),b.ry(b.hexagon(2.45,2.4),90).translate((6.5,-30,zz)))
  part(name,sh,b.META[name]['description']+'・水平戻し案内輪の逃げ','head_fixed')
 # Leave clearance for the existing grip guide cover and its screw.
 for name in('fairlead_cover_G','fairlead_screw_G'):
  bb=b.PARTS[name].BoundingBox();pad=.3
  rail=cut(rail,box(bb.xlen+2*pad,bb.ylen+2*pad,bb.zlen+2*pad,((bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,bb.zmin-pad)))
 # The expanded G-guide notch leaves a 0.14mm3 corner chip; omit that disconnected scrap.
 rail=max(rail.Solids(),key=lambda sh:sh.Volume())
 part('spring_cassette',rail,'曲線リブと輪郭に沿う共通側板・水平JB-14×3・丸い案内輪台','head_fixed')
 wheel=cut(cyl(4.6,1.2,(0,0,-.6)),cyl(1.05,2,(0,0,-1)),ring(5,3.8,.6,-.3))
 part('return_idler',wheel,'戻し糸の自由回転案内輪・印刷ジャーナル・転がり軸受は未使用','idler')
 part('idler_common_axle',uni(cyl(.65,16,(14,-24,13.05)),cyl(1.6,1.3,(14,-24,11.75))),'案内輪3個を通す共通M1.6×16軸・下から最後に挿す','hardware')
 part('idler_axle_nut',cut(b.hexagon(1.85,1.3,26.7).translate((14,-24,0)),cyl(.85,2,(14,-24,26.4))),'共通案内軸のM1.6ナット・上から留める','hardware')
 part('cassette_M2_screw',uni(cyl(.75,8,(0,-37,0),'y'),cyl(1.8,2,(0,-39,0),'y')),'共通ばね板を留めるM2×8','hardware')
 part('spring_hook_screw',uni(cyl(.55,7,(16,18,0),'x'),cyl(1.2,1,(15,18,0),'x')),'水平ばねの固定フック・M1.4×8・頭径2.4以上','hardware')
 # Prototype PTFE1.6/0.8 adapters have a positive tube-end shoulder.
 ferrule=cut(uni(cyl(1.8,4,(0,0,-4)),cyl(2.4,.8)),cyl(.9,4,(0,0,-3)),cyl(.4,6,(0,0,-4.5)))
 part('tube_reducer_25',ferrule,'試作PTFE外径1.6／内径0.8用・端面肩付き交換フェルール','hardware')
 upper=cut(uni(cyl(1.25,4),cyl(2.3,.8,(0,0,-.8))),cyl(.9,3.1,(0,0,-.1)),cyl(.4,5,(0,0,-.5)))
 part('upper_PTFE_adapter',upper,'上部／肘側のPTFE1.6取付アダプタ・アウター端面を肩で受ける','hardware')
 # Independent head bench jig uses the same two M2 mounting bolts as the carrier.
 jig=box(60,70,4,(0,-20,-42))
 for xx in(-20,20):jig=uni(jig,box(5,8,48,(xx,-40,-38)))
 jig=uni(jig,box(50,16,3,(0,-35,10)))
 for xx in(-5,5):jig=cut(jig,cyl(1.1,6,(xx,-30,9)))
 part('bench_head_stand',jig,'独立ヘッド1個の卓上治具・共通連結台と同じM2×2','fixture')
 tab=cut(box(8,4,3),cyl(.6,5,(0,0,-1)))
 part('manual_pull_tab',tab,'手動糸引き確認用つまみ・1ヘッド3個','fixture')
 # Matched clearance coupons are part of the print pack, not moving assembly.
 coupon=box(36,12,3,(0,0,0))
 for i,c in enumerate((.15,.2,.25,.3)):
  x=-13.5+9*i;coupon=uni(coupon,cut(cyl(3.5,5,(x,0,3)),cyl(2+c,8,(x,0,1))))
 part('fit_coupon',coupon,'Ø4ピン用の半径隙間0.15/0.20/0.25/0.30・左から順','coupon')
 part('fit_coupon_pin',uni(cyl(2,9),cyl(3,2)),'Ø4嵌合確認ピン','coupon')

def place_head(b,head,tw,delta,push):
 for side in('L','R'):head('return_spool_'+side,'twist_return_spool_'+side,yaw=tw)
 for xx in(-10.5,10.5):head('return_spool_screw_'+str(xx),'return_spool_M14_screw',at=(xx,0,0),yaw=tw)
 head('pinion_insert','grip_pinion_insert',yaw=tw+delta,color='#d5b46e')
 for x in(-4.1,4.1):head('pinion_screw_'+str(x),'pinion_M14_screw',at=(x,0,0),yaw=tw+delta)
 head('follower_pin','pusher_follower_pin',at=(0,0,-push),yaw=push/20*120)
 for tag in('G','T','P'):
  head('fairlead_cover_'+tag,'fairlead_cover_'+tag);head('fairlead_screw_'+tag,'fairlead_screw_'+tag)
 head('spring_cassette','spring_cassette')
 for xx in(-10,10):head('cassette_screw_'+str(xx),'cassette_M2_screw',at=(xx,0,39))
 for z in(27,34.5):
  head('case_bolt_'+str(z),'case_M2_bolt',at=(0,0,z));head('case_nut_'+str(z),'case_M2_nut',at=(0,0,z))
 for i,q in enumerate(RETURN):
  a=tw+delta if i==0 else tw if i==1 else push/20*120;rr=return_path(q,a)
  head('spring_hook_'+str(i),'spring_hook_screw',at=(0,0,q['z']))
  head('return_idler_'+str(i),'return_idler',at=(14,-24,q['z']),yaw=0)

 head('idler_common_axle','idler_common_axle')
 head('idler_axle_nut','idler_axle_nut')
