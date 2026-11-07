import math
def involute_points(module,teeth,phase=0,thinning=.06):
 r=module*teeth/2;rb=r*math.cos(math.radians(20));rt=r+module;rr=r-1.25*module
 invp=math.tan(math.radians(20))-math.radians(20);half=(math.pi*module/2-thinning)/(2*r);pts=[]
 def xy(rad,a):return(rad*math.cos(a),rad*math.sin(a))
 def inv(rad):v=math.sqrt(max(0,(rad/rb)**2-1));return v-math.atan(v)
 for i in range(teeth):
  a=2*math.pi*i/teeth+math.radians(phase)
  pts.append(xy(rr,a-math.pi/teeth))
  pts.append(xy(rr,a-half-invp))
  for rad in [max(rr,rb)+(rt-max(rr,rb))*j/3 for j in range(4)]:pts.append(xy(rad,a-half-invp+inv(rad)))
  for rad in [rt-(rt-max(rr,rb))*j/3 for j in range(4)]:pts.append(xy(rad,a+half+invp-inv(rad)))
  pts.append(xy(rr,a+half+invp));pts.append(xy(rr,a+math.pi/teeth))
 clean=[]
 for p in pts:
  if not clean or math.dist(p,clean[-1])>1e-7:clean.append(p)
 if math.dist(clean[0],clean[-1])<1e-7:clean.pop()
 return clean

def make(b):
 globals().update({n:getattr(b,n) for n in('box','cyl','uni','cut','ring','rx','ry','rz','part','P','PARTS')})
 def rib(a,c,w,z,h):
  dx,dy=c[0]-a[0],c[1]-a[1];L=math.hypot(dx,dy)
  nx,ny=-dy/L*w/2,dx/L*w/2
  poly=b.cq.Workplane('XY').polyline([(a[0]+nx,a[1]+ny),(c[0]+nx,c[1]+ny),(c[0]-nx,c[1]-ny),(a[0]-nx,a[1]-ny)]).close().extrude(h).val().translate((0,0,z))
  return uni(poly,cyl(w/2,h,(a[0],a[1],z)),cyl(w/2,h,(c[0],c[1],z)))
 def cable_seat(sh,x,y,z,axis):
  # End button bears on a shoulder inside the drum; no external anchor tower.
  sh=cut(sh,cyl(.45,5,(x,y,z-3)),cyl(1.2,1.1,(x,y,z)))
  if axis=='neg_y':sh=cut(sh,cyl(.3,3.5,(x,y-2.5,z-.7),'y'))
  if axis=='pos_y':sh=cut(sh,cyl(.3,3.5,(x,y,z-.7),'y'))
  if axis=='pos_x':sh=cut(sh,cyl(.3,3.5,(x,y,z-.7),'x'))
  return sh
 # Lower hollow winding drum, with only a small internal pinion for linear jaw motion.
 pin=b.cq.Workplane('XY').polyline(involute_points(.5,24,7.5,.07)).close().extrude(3).val().translate((0,0,7.3))
 drum=ring(10.9,3.2,3,11)
 drum=cut(drum,ring(12,10.1,1.1,11.95))
 drum=uni(drum,ring(4.4,3.2,6.7,7.3),cut(pin,cyl(3.2,5,(0,0,6))))
 drum=cable_seat(drum,0,-9,13.2,'neg_y')
 part('grip_drum_pinion',drum,'下側：実際にワイヤを巻く中空把持ドラム・小型内側ピニオン','head')
 rotor=cut(box(22,4,2,(0,0,3)),cyl(3.4,4,(0,0,2)))
 for xx in(-10,10):
  rotor=uni(rotor,box(2,P['cage_rail_length'],7,(xx,0,3.5)),box(2.6,P['cage_rail_length'],.5,(xx,0,3.5)),box(2.6,P['cage_rail_length'],1,(xx,0,7.2)),box(3,2,1,(xx*1.05,0,9.5)))
 for sg in(-1,1):
  rotor=uni(rotor,box(1.6,3,6.5,(sg*12,0,9.5)),box(3.4,3,1,(sg*11,0,9.5)))
  rotor=cut(rotor,cyl(.55,8,(sg*12,0,9)))
 for yy in(-21.45,21.45):rotor=uni(rotor,box(22,1.5,3,(0,yy,4)))
 upper=ring(14,5,3,16);upper=cut(upper,ring(15,12.85,1,17))
 for yy in(-19,19):rotor=cut(rotor,cyl(1.,26,(-13,yy,5.5),'x'))
 upper=cut(upper,cyl(.4,6,(13.45,0,15)));upper=cable_seat(upper,0,11.5,18.2,'pos_y')
 for sg in(-1,1):upper=cut(upper,cyl(.65,5,(sg*12,0,15)),cyl(1.1,2,(sg*12,0,17.8)))
 for a in(90,210,330):
  upper=uni(upper,cyl(.8,2.3,(8*math.cos(math.radians(a)),8*math.sin(math.radians(a)),14.2)))
 part('twist_guide_cage',rotor,'下側ガイド籠：上ドラムとはM1.2ねじ2本で締結して組み立てる','head')
 part('twist_upper_drum',upper,'上側中空ねじりドラム：下ドラムを挿入後に上から装着','head')
 part('rotor_M12_screw',uni(cyl(.55,7.3,(0,0,10.5)),cyl(1,1.1,(0,0,17.8))),'上ドラムの皿座ねじ・ねじ山省略','hardware')
 carrier=uni(box(17.6,3,3,(0,0,4)),box(1.5,27,3,(7.35,-9.5,7.3)),box(1.5,2,2,(7.35,0,6)))
 for xx in(-7.2,7.2):carrier=uni(carrier,box(1.2,2,15,(xx,0,-11)))
 for k in range(17):
  yy=-19+(k-2)*math.pi*.5;h=.392699;fl=math.tan(math.radians(20))
  q=b.cq.Workplane('XY').polyline([(5.5,yy-h+.5*fl),(6.68,yy-h-.68*fl),(6.68,yy+h+.68*fl),(5.5,yy+h-.5*fl)]).close().extrude(3).val().translate((0,0,7.3));carrier=uni(carrier,q)
 carrier=cut(carrier,cyl(1.,22,(-11,0,5.5),'x'),box(4,1.,3.2,(0,-1.2,3.9)))
 part('parallel_jaw_rack',carrier,'爪の支持部と内側ラック・接触パッドとは別部品','grip_link')
 part('contact_pad_5mm',box(16,3,5,(0,0,-16)),'高さ5mmのスポンジ接触パッド','grip_link')
 # Short central pusher, independent from both hollow drums.
 cam=uni(ring(3,1.45,24,0),ring(3.4,1.45,.2,7.05))
 for phase in(0,180):
  for j in range(25):cam=cut(cam,rz(cyl(.8,3,(1.1,0,22-20*j/24),'x'),phase+120*j/24))
 part('push_cam_left',cam.intersect(box(10,12,26,(-5.02,0,-1))),'中央カム左半割・フォロワを挟んで組み立てる','pusher_fixed')
 part('push_cam_right',cam.intersect(box(10,12,26,(5.02,0,-1))),'中央カム右半割・120度で20mm下降','pusher_fixed')
 stem=cyl(1.25,57,(0,0,-7));stem=cut(stem,box(3,6,51,(2.4,0,-.5)),box(3,6,51,(-2.4,0,-.5)))
 push=uni(cyl(6,1.5,(0,0,-8)),stem,cyl(.5,2.35,(.8,0,22),'x'),cyl(.5,2.35,(-3.15,0,22),'x'))
 part('push_rotating_plunger',push,'20mm押込み・二面幅押し棒・押し足Ø12','pusher')
 d=b.cut(cyl(1.35,10,(0,0,23.5)),box(3,6,11,(2.5,0,23.5)),box(3,6,11,(-2.5,0,23.5)))
 coupler=uni(cyl(3.8,4.8,(0,0,24.5)),ring(8.1,0.01,3,26.3));coupler=cut(coupler,d,ring(9,7.1222,1.1,27.25))
 coupler=cable_seat(coupler,6,0,28.5,'pos_x')
 part('push_sliding_drive',coupler,'押込み用小径直巻きドラム・かさ歯車なし','pusher')
 # One complete independent fixed chassis per vial; the other unit is a separate instance.
 fixed=box(26,6,3,(0,-30,13))
 q=uni(ring(15.5,14.2,5.2,14.9),ring(15.5,13,.8,14.9),ring(15.5,13,.8,19.3),box(4,21,3,(-10,-23.5,14.9)),box(4,21,3,(10,-23.5,14.9)))
 fixed=uni(fixed,q)
 for xx in(-10,10):fixed=uni(fixed,box(2,6,20.3,(xx,-30,15.2)))
 fixed=uni(fixed,box(26,6,2,(0,-30,31.5)),box(3,30,2,(0,-15,31.5)))
 guide=ring(4.8,1.5,4,29.5);fixed=uni(fixed,guide)
 fixed=cut(fixed,cyl(1.5,9,(0,0,28.5)))
 # Cam sleeve clamp clears both hollow drums and the two moving follower pins.
 q=uni(ring(4.2,3.3,1,19.3),box(2,30,1,(0,-15,19.3)),box(3,5,14.2,(0,-30,19.3)))
 q=cut(q,cyl(3.3,4,(0,0,17.5)))
 fixed=uni(fixed,q)
 # Open-backed rib structure replaces the rectangular roof and its four windows.
 roof=uni(rib((-10,-30),(10,-30),6,33.5,2),rib((0,-30),(0,0),4,33.5,2),ring(5.8,1.5,2,33.5),rib((-13,-18),(10.25,-18),6,33.5,2),rib((-10,-30),(-13,-18),4,33.5,2),rib((10,-30),(10.25,-18),4,33.5,2),rib((-7.3,-15),(0,-15),4,33.5,2),cyl(3,2,(-7.3,-15,33.5)))
 fixed=uni(fixed,roof)
 fixed=cut(fixed,cyl(1.5,5,(0,0,32.5)))
 fixed=cut(fixed,cyl(.4,9,(13.45,0,13)))
 # Large-radius bare-wire fairleads, followed by vertical guide channels.
 # The guide grooves are reference metal/liner geometry, not printed Bowden outer.
 channels=[]
 for xx,yy,zz,sg in((10.25,-10,20.5,-1),(-13,-10,25.5,-1),(-7.3,-7,35.8,-1)):
  shoe=cut(cyl(9.5,3,(xx-1.5,yy,zz),'x'),cyl(6.5,5,(xx-2.5,yy,zz),'x'))
  keep=box(5,12,12,(xx,yy+sg*6,zz-12));shoe=shoe.intersect(keep)
  groove=cut(cyl(8.4,.9,(xx-.45,yy,zz),'x'),cyl(7.6,2,(xx-1,yy,zz),'x'))
  shoe=cut(shoe,groove);channels.append(groove)
  ey=yy+sg*8
  tube=cut(cyl(1.2,max(.2,35.5-zz),(xx,ey,zz)),cyl(.35,max(2,37.5-zz),(xx,ey,zz-1)))
  fixed=uni(fixed,shoe,tube);channels.append(cyl(.35,43-zz,(xx,ey,zz)))
 # Tangential exit through the upper drum's surrounding journal.
 fixed=cut(fixed,box(1.1,11,1.2,(-13,-5.5,16.9)))
 for xx,yy in((10.25,-18),(-13,-18),(-7.3,-15)):
  socket=cut(cyl(3,5,(xx,yy,35.5)),cyl(1.9,4.1,(xx,yy,36.5)),cyl(.35,9,(xx,yy,32.5)))
  fixed=uni(fixed,socket);fixed=cut(fixed,cyl(.35,9,(xx,yy,32.5)))
 for xx in(-5,5):fixed=cut(fixed,cyl(1.1,9,(xx,-30,12.5)))
 ferrule=cut(uni(cyl(1.8,4,(0,0,-4)),cyl(2.4,.8)),cyl(1.3,5.2,(0,0,-4.1)))
 part('tube_reducer_25',ferrule,'外径2.5アウター用交換フェルール・3.5用へ交換可能','hardware')
 fixed=cut(fixed,cyl(.8,3.1,(-7.3,-15,32.5)))
 # Two small retaining screws secure one three-port comb above the ferrules.
 for xx in(-3,4):
  fixed=uni(fixed,cyl(1.8,7,(xx,-24,33.5)),rib((xx,-24),(xx,-18),3.6,33.5,2))
  fixed=cut(fixed,cyl(.6,7.4,(xx,-24,33.3)))
 fixed=cut(fixed,*channels)
 part('module_chassis',fixed,'バイアル1本分の独立ケース・ドラム軸受・押込み・配線固定・M2連結穴','head_fixed')
 b.META['module_chassis']['before_refinement_volume_mm3']=6207.455186253335
 b.META['module_chassis']['comparison_baseline']='V0.9 complete chassis'
 cap=uni(rib((-13,-18),(10.25,-18),6,40.5,1.5),cyl(3,1.5,(-7.3,-15,40.5)),rib((-7.3,-15),(-7.3,-18),5,40.5,1.5))
 for xx in(-3,4):
  cap=uni(cap,rib((xx,-24),(xx,-18),3.6,40.5,1.5))
  cap=cut(cap,cyl(.65,2.5,(xx,-24,40)),cyl(1.1,1.5,(xx,-24,40.8)))
 for xx,yy in((10.25,-18),(-13,-18),(-7.3,-15)):
  cap=cut(cap,cyl(2.6,.9,(xx,yy,40.45)),cyl(1.4,2,(xx,yy,41.2)))
 part('rear_cable_retainer',cap,'後側3本をそろえフェルールを押さえる着脱コーム','head_fixed')
 part('retainer_M12_screw',uni(cyl(.5,5.8,(0,0,35)),cyl(1,1.1,(0,0,40.8))),'後側3線コームのM1.2ねじ・ねじ山省略','hardware')
 part('cable_stop_button',cut(cyl(1.05,.6),cyl(.4,.8,(0,0,-.1))),'PE糸の止め結びを受ける印刷エンドビーズ・穴Ø0.8をさらう','hardware')
 # Flange screws are actual separate parts. Threads are represented by nominal cylinders.
 bolt=uni(cyl(.95,8,(0,0,10)),cyl(1.8,2,(0,0,8)))
 nut=cut(b.hexagon(2.3,1.6,16),cyl(1.05,3,(0,0,15.5)))
 part('module_M2_bolt',bolt,'ユニット支持台のM2ボルト・ねじ山省略','hardware')
 part('module_M2_nut',nut,'ユニット支持台のM2ナット・ねじ山省略','hardware')
 part('jaw_lock_pin',uni(cyl(.8,25,axis='x'),cyl(2.2,1.5,(-1.5,0,0),'x')),'開放姿勢の着脱固定ピン','lock')
 part('twist_lock_pin',uni(cyl(.35,7,(13.45,0,14.3)),cyl(1.3,1.2,(13.45,0,21.3))),'上ドラムの回転を固定する着脱ピン','lock')
 part('cam_M16_setscrew',cyl(.65,1.2,(0,3,19.4),'y'),'カム半割を固定するM1.6止めねじ・先端位置は接触公称','hardware')
