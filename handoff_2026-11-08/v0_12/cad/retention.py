"""Removable FDM C-clips on exposed ends. Strength/durability intentionally unqualified."""
from math import *
from scipy.spatial.transform import Rotation
import numpy as np
SPECS={}
def make(b):
 global SPECS
 S=b.P['support_offset']
 SPECS={
 'root_output_shaft':(5,3,[-83-S,82.2+S]),
 'elbow_output_shaft':(5,3,[-56-S,55.2+S]),
 'root_parallel_stub':(2,0,[83+S]),
 'elbow_parallel_axle':(2,0,[-66-S,65.2+S]),
 'head_main_stub':(3,0,[7.6]),'head_parallel_stub':(2,0,[-1.6]),
 'upper_keyed_shaft':(2,0,[8.5,27]),
 'root_input_shaft':(2,0,[-95-S,.1]),'elbow_input_shaft':(2,0,[-13,39]),
 }
 for ro in(2,3,5):
  ri=ro-.4;sh=b.cut(b.cyl(ro+1.8,.75,axis='x'),b.cyl(ri,.95,(-.1,0,0),'x'),b.box(2,10,ri*1.55,(.3,-5,-ri*.775)))
  b.part('shaft_clip_'+str(ro),sh,'横から着脱するCクリップ・軸端溝に入れる・予備も印刷','hardware')
 for n,(ro,ri,xx) in SPECS.items():
  sh=b.PARTS[n]
  if n=='head_parallel_stub':sh=b.uni(sh,b.cyl(2,2,(-2,0,0),'x'))
  if n=='head_main_stub':sh=b.uni(sh,b.cyl(3,2,(8.5,0,0),'x'))
  cy=13.62 if n=='upper_keyed_shaft'else 0
  for x in xx:
   tool=b.cut(b.cyl(ro+.3,.85,(x,cy,0),'x'),b.cyl(ro-.5,1.1,(x-.1,cy,0),'x'))
   sh=sh.cut(tool)
  b.part(n,sh.clean(),b.META[n]['description']+'・端部抜け止め溝',b.META[n]['group'])

def append(b,items):
 # Derive each clip's exact world pose from the transform tracked by mesh_cache.
 # Explicit mirrored stubs are handled through their named placement below.
 new=[]
 for q in items:
  if q.part not in SPECS:continue
  ro,_,xx=SPECS[q.part]
  T=getattr(q.shape,'_mesh_pose',None)
  if T is not None:
   for i,x in enumerate(xx):
    sh=b.PARTS['shaft_clip_'+str(ro)].translate((x+.05,13.62 if q.part=='upper_keyed_shaft'else 0,0))
    rv=Rotation.from_matrix(T[:3,:3]).as_rotvec();angle=np.linalg.norm(rv)
    if angle>1e-10:sh=sh.rotate((0,0,0),tuple(rv/angle),degrees(angle))
    sh=sh.translate(tuple(T[:3,3]))
    new.append(b.Item(q.name+'_clip_'+str(i),'shaft_clip_'+str(ro),sh,'hardware','#83949d'))
  else:
   # Left stubs are mirrored before translation, so recover the exact mirror/translation.
   if q.name in ('root_parallel_pin_L','head_main_pin_L','head_parallel_pin_L'):
    bb=q.shape.BoundingBox();base=b.PARTS[q.part].BoundingBox();dy=(bb.ymin+bb.ymax-base.ymin-base.ymax)/2;dz=(bb.zmin+bb.zmax-base.zmin-base.zmax)/2
    dx=bb.xmin+base.xmax
    for i,x in enumerate(xx):new.append(b.Item(q.name+'_clip_'+str(i),'shaft_clip_'+str(ro),b.PARTS['shaft_clip_'+str(ro)].translate((x+.05,0,0)).mirror('YZ').translate((dx,dy,dz)),'hardware','#83949d'))
 return items+new
