"""A split clamp adds three manual Bowden endpoints to the head bench stand.
This fixture does not modify the machine mechanism or its geometry audits.
"""
def make(b):
 box,cyl,cut,uni=b.box,b.cyl,b.cut,b.uni
 back=box(60,9.2,8,(0,-45.4,0));front=box(60,9.2,8,(0,-34.6,0))
 for x in(-20,20):
  tool=box(5.5,8.4,10,(x,-40,-1));back=cut(back,tool);front=cut(front,tool)
 for x in(-25,-15,15,25):
  tool=cyl(1.1,24,(x,-52,4),'y');back=cut(back,tool);front=cut(front,tool)
 for x in(-25,25):back=uni(back,box(4,6,9,(x,-50,8)))
 back=uni(back,box(60,4,6,(0,-52,17)))
 for x in(-16,0,16):back=cut(back,cyl(1.35,8,(x,-56,20),'y'))
 b.part('bench_anchor_back',back,'卓上治具の支柱を挟む後側クランプ・3本のアウター端を固定','fixture')
 b.part('bench_anchor_front',front,'卓上治具の支柱を挟む前側クランプ・M2×25とナット4組','fixture')
