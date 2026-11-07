"""B2 retention and registration improvements, preserving the main mechanism."""
def apply(b):
 box,cyl,uni,cut,ring,part=b.box,b.cyl,b.uni,b.cut,b.ring,b.part
 # The follower ends stay inside the cam OD, clear of the surrounding hollow hub.
 part('pusher_follower_pin',cyl(.5,5.8,(-2.9,0,22),'x'),'Ø1×5.8フォロワ横ピン・先端をカム外径内へ収める','hardware')
 # Direct upper-home lock through fixed guide AND rod, independent of spring tension.
 for n in ('module_case_L','module_case_R','push_rotating_plunger'):
  sh=cut(b.PARTS[n],cyl(.6,14,(-7,0,32),'x'))
  part(n,sh,b.META[n]['description']+'・棒上端の横固定穴',b.META[n]['group'])
 part('press_home_lock_pin',uni(cyl(.5,12,(-6,0,32),'x'),cyl(1.7,1.2,(-7.2,0,32),'x')),'棒を直接固定する上端ピン・押込み前に左へ抜く','lock')
 # The driver stays fixed in height: 0.1 lower / 0.2 upper nominal end float.
 flange=ring(3.3,1.45,.4,24)
 for side,sign in [('left',-1),('right',1)]:
  n='push_cam_'+side;half=flange.intersect(box(10,12,3,(sign*5.02,0,23)))
  sh=uni(b.PARTS[n],half)
  for y,z in ((2.15,18.),(-2.15,22.8)):sh=cut(sh,box(1.9,.9,1.8,(0,y,z-.9)))
  part(n,sh,'位置合わせキー穴・上端受け肩付きの半割カム','pusher_fixed')
 part('push_cam_alignment_key',box(1.6,.6,1.4),'半割カムの位置合わせキー・2個を挟んで閉じる','pusher_fixed')
 # Two short fixed collars keep the split cam from opening radially.
 collar=uni(ring(3.3,3.15,1,19.3),ring(4.2,3.15,1,22.8),box(2,30,1,(0,-15,22.8)))
 collar=cut(collar,cyl(3.15,3,(0,0,21.8)))
 for n,sign in [('module_case_L',-1),('module_case_R',1)]:
  sh=uni(b.PARTS[n],collar.intersect(box(80,100,40,(sign*40,0,0))))
  for y,z in ((-31.8,25.3),(-28.2,32.8)):sh=cut(sh,box(3.4,1.2,1.2,(0,y,z-.6)))
  part(n,sh,b.META[n]['description']+'・半割位置合わせキー座',b.META[n]['group'])
 part('case_alignment_key',box(3,.9,.9),'ケース合わせ面の位置決めキー・2個を先に入れる','head_fixed')

 # Clear the reinforced upper rails under the G fairlead mounting boss.
 clearance=ring(25.5,6.5,.8,10.3)
 for n in('module_case_L','module_case_R','fairlead_cover_G'):
  part(n,cut(b.PARTS[n],clearance),b.META[n]['description'],b.META[n]['group'])

 # The carriages must enter from the two open ends without flexing the retaining lips.
 cage=b.PARTS['twist_guide_cage']
 for sign in(-1,1):
  cage=cut(cage,box(22.4,2.4,3.3,(0,sign*21.7,3.85)))
  for x in(-10,10):
   cage=cut(cage,box(2.3,2.4,3.5,(x,sign*21.7,6.85)),cyl(.55,4,(x,18.5 if sign>0 else-22.5,9),'y'))
 part('twist_guide_cage',cage,'上下のCレール・ラック背面と上ガイド・両端は着脱ストッパー','head')
 end=box(22,2,3,(0,0,4))
 for x in(-10,10):end=uni(end,box(2,2,3.2,(x,0,7)));end=cut(end,cyl(.75,3,(x,-1.5,9),'y'))
 part('jaw_guide_endcap',end,'爪レールの着脱式端止め・片側M1.4×4を2本','head')
 part('guide_endcap_M14_screw',uni(cyl(.5,4,(0,-4,9),'y'),cyl(1,.6,(0,0,9),'y')),'端止め用の小頭M1.4×4','hardware')
