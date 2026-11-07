#!/usr/bin/env python3
"""V0.12 rear-routed skeletal heads, central joint drives, parallel-link orientation and 20mm press.
mm / degrees. Metal production assumed. No bevel transmission in the heads.
No firmware or manufacturing readiness is implied by CAD generation.
"""
import json,math,base64,gzip,csv,hashlib
from pathlib import Path
from dataclasses import dataclass
import cadquery as cq
from cadquery import exporters
import mesh_cache
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
P=json.loads((ROOT/'cad/parameters.json').read_text())
def box(x,y,z,at=(0,0,0)):return cq.Workplane('XY').box(x,y,z,centered=(True,True,False)).val().translate(at)
def cyl(r,h,at=(0,0,0),axis='z'):
 s=cq.Workplane('XY').circle(r).extrude(h).val()
 if axis=='x':s=s.rotate((0,0,0),(0,1,0),90)
 if axis=='y':s=s.rotate((0,0,0),(1,0,0),-90)
 return s.translate(at)
def uni(*ss):
 s=ss[0]
 for t in ss[1:]:s=s.fuse(t)
 return s.clean()
def cut(s,*tt):
 for t in tt:s=s.cut(t)
 return s.clean()
def ring(ro,ri,h,z=0):return cut(cyl(ro,h,(0,0,z)),cyl(ri,h+2,(0,0,z-1)))
def rx(s,a):return s.rotate((0,0,0),(1,0,0),a)
def ry(s,a):return s.rotate((0,0,0),(0,1,0),a)
def rz(s,a):return s.rotate((0,0,0),(0,0,1),a)
def hexagon(r,h,z=0):return cq.Workplane('XY').polygon(6,2*r).extrude(h).val().translate((0,0,z))
def axle(ro,ri,L,x):return ring(ro,ri,L).rotate((0,0,0),(0,1,0),90).translate((x,0,0))
def cone(r0,r1,h):return cq.Solid.makeCone(r0,r1,h)
def spur(r,z=0,h=3,teeth=24):
 pts=[]
 for i in range(teeth):
  for a,rr in ((-.48,r-.625),(-.24,r+.5),(.24,r+.5),(.48,r-.625)):
   t=2*math.pi*(i+a)/teeth;pts.append((rr*math.cos(t),rr*math.sin(t)))
 return cq.Workplane('XY').polyline(pts).close().extrude(h).val().translate((0,0,z))
def drum(r,h=3):
 return uni(ring(r+.4,3.2,.6),ring(r-.3,3.2,h-.8,.4),ring(r+.4,3.2,.6,h-.6))
COL={'frame':'#526c80','arm':'#6c9b80','head':'#338a9d','head_fixed':'#688e9d','grip_link':'#d3a04a','drive':'#ca8b45','joint_gear':'#cf9b56','joint_case':'#7d93a2','pusher':'#bb7095','pusher_fixed':'#7a85aa','lock':'#e46b58','holder':'#92a2ae','reference':'#c9dbe1','wire':'#e1ac4c','cable':'#4b5966','spring':'#dbb858','pitch_envelope':'#deac65'}
PARTS={};META={};BUILT=False
def part(n,s,desc,group):
 solids=s.Solids()
 if len(solids)>1 and sum(v.Volume()for v in solids if v.Volume()<.001)<.01:
  keep=[v for v in solids if v.Volume()>=.001]
  if len(keep)==1:s=keep[0]
 if not s.isValid():raise ValueError(n+' invalid')
 PARTS[n]=s;META[n]={'description':desc,'group':group,'solids':len(s.Solids())}
 return s
@dataclass
class Item:
 name:str;part:str;shape:object;group:str;color:str;reference:bool=False

COL.update(hardware='#7e8b96',datum='#a2b7c5')
def ik(y,z):
 dy=y-P['root_y'];dz=z-P['root_z'];L1,L2=P['link1'],P['link2'];r=math.hypot(dy,dz)
 if not abs(L1-L2)<r<L1+L2:raise ValueError('Outside the nonsingular arm workspace')
 a=math.atan2(dz,dy)+math.acos((L1*L1+r*r-L2*L2)/(2*L1*r))
 ey=P['root_y']+L1*math.cos(a);ez=P['root_z']+L1*math.sin(a)
 c=math.atan2(z-ez,y-ey)
 return math.degrees(a),math.degrees(c)
HOME_A,HOME_C=ik(0,P['head_home_z'])
def make_parts():
 global BUILT
 if BUILT:return
 import sys,head,mechanism,drive
 me=sys.modules[__name__]
 head.make(me);mechanism.make(me);S=P['support_offset']
 # Main frame and two rear supports. All column feet meet the base at z=-1.2.
 frame=box(180+2*S,230,4.8,(0,-85,-6))
 for xx in(-76-S,76+S):
  frame=uni(frame,box(12,16,241.2,(xx,P['root_y'],-1.2)),box(10,10,241.2,(xx,-180,-1.2)),box(6,18,6,(xx,P['root_y']-9,P['root_z']-3)))
 frame=uni(frame,box(152+2*S,6,6,(0,P['root_y']-18,P['root_z']-3)))
 # Input journal wing is part of the fixed frame; the normal wires remain outside it.
 cd=P['gear_cd'];ry0=P['root_y'];rz0=P['root_z']
 frame=uni(frame,box(4,cd,6,(-73-S,ry0+cd/2,rz0-3)),cyl(3.2,2,(-74-S,ry0+cd,rz0),'x'))
 frame=cut(frame,cyl(2.15,6,(-76-S,ry0+cd,rz0),'x'))
 for xx in(-76-S,76+S):
  frame=cut(frame,cyl(5.2,20,(xx-10,ry0,rz0),'x'),cyl(2.1,20,(xx-10,ry0,rz0+P['parallel_offset']),'x'))
 for sg in(-1,1):
  for zz in(P['reaction_brace_z']-6,P['reaction_brace_z']+8):frame=cut(frame,cyl(.9,11,(67.5+S,P['root_y'],zz),'x') if sg>0 else cyl(.9,11,(-78.5-S,P['root_y'],zz),'x'))
 for xx in(-9,-3):frame=cut(frame,cyl(1.1,10,(xx,ry0-22,rz0),'y'))
 for hx,sg in((-P['vial_pitch']/2,1),(P['vial_pitch']/2,-1)):
  for yy in(-12,12):frame=cut(frame,cyl(1.1,8,(hx+sg*8,yy,-7)))
 part('fixed_frame',frame,'固定ベース・左右根元支持・背面支柱・M4軸受ウィング','frame')
 # Reference bodies are separate from hard-part interference tests.
 part('ref_vial',uni(ring(11.5,10.5,96),cyl(11.5,1)),'Ø23×96バイアル','reference')
 part('ref_sponge',cyl(15,30),'柔軟なスポンジの参考外形','reference')
 part('ref_servo',uni(box(28.5,12.2,22.8,(0,0,-11.4)),box(2,12.2,32.5,(8,0,-16.25)),cyl(3,4,(14.25,0,0),'x')),'MG90D仮外形・現物適合未検証','reference')
 drive.make(me)
 import prototype
 prototype.apply(me)
 import retention
 retention.make(me)
 mesh_cache.tag(PARTS)
 BUILT=True

def target(label,y,z,g=25,tw=0,p0=0,p1=0,foam='held',angles=None,explain=None):
 a,c=angles if angles is not None else ik(y,z)
 if angles is not None:y=P['root_y']+P['link1']*math.cos(math.radians(a))+P['link2']*math.cos(math.radians(c));z=P['root_z']+P['link1']*math.sin(math.radians(a))+P['link2']*math.sin(math.radians(c))
 return dict(label=label,a=a,c=c,gap=g,twist=tw,push_old=p0,push_new=p1,foam_mode=foam,tip_y=y,tip_z=z,explanatory=explain)
STATES=[
 target('初期：爪100〜105mm／栓上端107mm',0,116,35,foam='installed'),
 target('旧・新を把持',0,116,25,foam='installed'),
 target('把持の相対角を保って30度ねじり',0,116,25,30,foam='installed'),
 target('斜め引抜き：後方8mm・上方19mm',-8,135,25,30),
 target('完全引抜き：栓下面115mm',-8,154,25,30),
 target('両側を同じ後方へ退避',0,0,25,30,angles=(121,35)),
 target('復帰：押込み受けの後方から進入',-8,135,25,30),
 target('再装着：栓下面を口縁96mmへ戻す',0,135,25,30),
 target('ねじりを戻す・栓を口縁に仮置き',0,135,25,0),
 target('爪を開く：押し足127mm／栓上端126mm',0,135,35,foam='seating'),
 target('旧側だけ押込み10mm',0,135,35,p0=10,foam='seating'),
 target('両側20mm押込み：押し足107mm',0,135,35,p0=20,p1=20,foam='seating'),
 target('押し棒を127mmへ戻す・栓は107mm',0,135,35,foam='installed'),
 target('ヘッドを初期高さへ戻す',0,116,35,foam='installed'),
 target('5mm閉口の機械範囲確認',0,116,5,foam='installed'),
 target('旧5mm・新35mmの独立把持確認',0,116,35,foam='installed',explain='independent'),
 target('逆方向30度ねじり',0,116,25,-30,foam='installed'),
 target('説明：旧ユニットをねじで取り外す',0,116,35,foam='installed',explain='detached'),
 target('説明：旧ユニットの分解表示（動作ではない）',0,116,35,foam='installed',explain='exploded')]

for angle in range(0,360,45):
 p=target(f'一周の外形確認 {angle}°（実機指令ではない）',0,116,35,angle,foam='installed',explain='sweep');p['envelope_only']=True;STATES.append(p)
critical=math.degrees(math.atan2(P['cage_rail_length']/2,11.3))
p=target(f'最接近角の外形確認 {critical:.2f}°（実機指令ではない）',0,116,35,critical,foam='installed',explain='sweep');p['envelope_only']=True;STATES.append(p)

def foam_shape(top,installed=False):
 bottom=top-P['sponge_length'];r0=10.4;r1=P['sponge_d']/2
 if installed:
  sh=cyl(r0,max(.01,96-bottom),(0,0,bottom))
  if top>96:
   h=min(2,top-96);sh=uni(sh,cone(r0,r1,h).translate((0,0,96)))
   if top>98:sh=uni(sh,cyl(r1,top-98,(0,0,98)))
  return sh
 return uni(cone(r0,r1,2).translate((0,0,bottom)),cyl(r1,28,(0,0,bottom+2)))

def state(k=0,override=None):
 import mechanism,drive,wires
 pose=dict(STATES[k] if override is None else override);pose['lock_on']=k in(0,13) and override is None;a,c=pose['a'],pose['c']
 ey=P['root_y']+P['link1']*math.cos(math.radians(a));ez=P['root_z']+P['link1']*math.sin(math.radians(a));pose.update(elbow_y=ey,elbow_z=ez)
 ty,tz=pose['tip_y'],pose['tip_z'];its=[]
 def add(n,p,s=None,at=(0,0,0),ref=False,group=None,color=None):
  gr=group or META[p]['group'];its.append(Item(n,p,(PARTS[p] if s is None else s).translate(at),gr,color or COL.get(gr,'#8998a2'),ref))
 add('fixed_frame','fixed_frame')
 for side in ('L','R'):add('upper_deck_'+side,'upper_deck_'+side)
 import prototype
 prototype.place_frame(__import__(__name__),add)
 mechanism.place(__import__(__name__),add,pose)
 prototype.place_adapters(__import__(__name__),add,pose)
 for side,hx,sg,push in(('old',-P['vial_pitch']/2,1,pose['push_old']),('new',P['vial_pitch']/2,-1,pose['push_new'])):
  gap=5 if k==15 and side=='old' else pose['gap'];delta=-math.degrees((35-gap)/12);tw=pose['twist']
  pose[side+'_gap']=gap;pose[side+'_relative']=delta
  add(side+'_holder','holder_old_inner' if side=='old' else 'holder_new_inner',at=(hx,0,0));add(side+'_vial','ref_vial',at=(hx,0,0),ref=True)
  def head(n,p,s=None,at=(0,0,0),yaw=0,group=None,color=None):
   sh=rz((PARTS[p] if s is None else s).translate(at),yaw)
   offset=(hx,ty,tz)
   if side=='old' and pose['explanatory']=='detached':offset=(hx-60,ty,tz+15)
   if side=='old' and pose['explanatory']=='exploded':
    dz={'module_chassis':0,'twist_guide_cage':15,'parallel_jaw_rack':15,'contact_pad_5mm':15,'rotor_M12_screw':55,'cam_M16_setscrew':70,'grip_drum_pinion':35,'twist_upper_drum':55,'push_cam_left':70,'push_cam_right':70,'push_rotating_plunger':87,'push_sliding_drive':100,'rear_cable_retainer':110,'retainer_M12_screw':115}.get(p,0)
    dx=-25 if p=='module_case_L' else 25 if p=='module_case_R' else 48 if p=='spring_cassette' else -10 if p=='push_cam_left' else 10 if p=='push_cam_right' else 0
    if p.startswith('twist_return_spool_'):dx=-10 if p.endswith('L')else 10;dz=25
    if p=='return_spool_M14_screw':dz=30
    if p=='grip_pinion_insert':dz=-8
    if p=='pusher_follower_pin':dx=18;dz=87
    sh=sh.translate((dx,0,dz))
   add(side+'_'+n,p,s=sh,at=offset,group=group,color=color)
  head('chassis_L','module_case_L');head('chassis_R','module_case_R')
  head('twist_drum','twist_upper_drum',yaw=tw,color='#2f8999')
  head('guide_cage','twist_guide_cage',yaw=tw,color='#2f8999')
  for sign in(-1,1):head('rotor_screw_'+str(sign),'rotor_M12_screw',at=(sign*12,0,0),yaw=tw)
  head('grip_drum','grip_drum_pinion',yaw=tw+delta,color='#cd9455')
  head('grip_cable_stop','cable_stop_button',at=(0,-9,13.2),yaw=tw+delta,color='#a18154')
  head('twist_cable_stop','cable_stop_button',at=(0,11.5,18.2),yaw=tw,color='#a18154')
  for sign in(-1,1):
   jaw=PARTS['parallel_jaw_rack'] if sign>0 else rz(PARTS['parallel_jaw_rack'],180)
   head('jaw_'+str(sign),'parallel_jaw_rack',s=jaw,at=(0,sign*(gap/2+1.5),0),yaw=tw,color='#7fa4a4')

  prototype.place_head(__import__(__name__),head,tw,delta,push)
  head('push_cam_L','push_cam_left');head('push_cam_R','push_cam_right')
  head('push_rod','push_rotating_plunger',at=(0,0,-push),yaw=push/20*120)
  head('push_drum','push_sliding_drive',yaw=push/20*120)
  head('press_cable_stop','cable_stop_button',at=(6,0,28.5),yaw=push/20*120,color='#a18154')
  head('cable_retainer','rear_cable_retainer')
  for xx in(-3,4):head('retainer_screw_'+str(xx),'retainer_M12_screw',at=(xx,-24,0))
  if pose['lock_on']:
   for yy in(-19,19):head('jaw_lock_'+str(yy),'jaw_lock_pin',at=(-12.5,yy,5.5))
   head('twist_lock','twist_lock_pin')
  for dx in(-5,5):
   head('mount_bolt_'+str(dx),'module_M2_bolt',at=(dx,-30,0))
   head('mount_nut_'+str(dx),'module_M2_nut',at=(dx,-30,0))
  for j,(wx,yy) in enumerate(((10.25,-18),(-13,-18),(-7.3,-15))):head('outer_ferrule_'+str(j),'tube_reducer_25',at=(wx,yy,40.5))
  mode=pose['foam_mode'];top=(max(107,127-push) if push>=1 else 126) if mode=='seating' else (107 if mode=='installed' else tz-9)
  y=0 if mode in('installed','seating') else ty
  add(side+'_sponge','ref_sponge',s=foam_shape(top,mode in('installed','seating')),at=(hx,y,0),ref=True,group='reference',color='#d8bd91')
  pose[side+'_foam_top']=top;pose[side+'_foot_z']=tz-8-push
 if pose.get('envelope_only'):
  demo=dict(pose,twist=0,old_relative=0,new_relative=0);drive.place(__import__(__name__),add,demo);pose['servo_commands_valid']=False
 else:drive.place(__import__(__name__),add,pose)
 import retention
 its=retention.append(__import__(__name__),its)
 if pose['explanatory']=='exploded':its=[q for q in its if q.name.startswith('old_') and q.group not in('holder','reference')]
 pose['jaw_z_low']=tz-16;pose['jaw_z_high']=tz-11
 return its,pose

def tube_mesh(name,pts,r,color,group='cable'):
 import numpy as np
 pts=[np.array(p,float) for p in pts];v=[];f=[];N=8
 for i,p in enumerate(pts):
  t=pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)];t=t/max(1e-9,np.linalg.norm(t));u=np.cross(t,[0,0,1])
  if np.linalg.norm(u)<.01:u=np.cross(t,[1,0,0])
  u/=np.linalg.norm(u);w=np.cross(t,u)
  for j in range(N):v.append((p+r*(u*math.cos(j*2*math.pi/N)+w*math.sin(j*2*math.pi/N))).round(4).tolist())
 for i in range(len(pts)-1):
  for j in range(N):
   a=i*N+j;bb=i*N+(j+1)%N;cc=(i+1)*N+j;d=(i+1)*N+(j+1)%N;f.extend([[a,bb,cc],[bb,d,cc]])
 return dict(name=name,part=name,group=group,color=color,reference=False,v=v,f=f)
def mesh_items(its):return[mesh_cache.mesh(q,PARTS) for q in its]
def assembly(items,name):
 ass=cq.Assembly(name=name)
 for q in items:ass.add(q.shape,name=q.name,color=cq.Color(*[int(q.color[i:i+2],16)/255 for i in(1,3,5)]))
 return ass
def publish():
 import wires
 make_parts();data={};poses={};tpl=(ROOT/'cad/viewer_template.html').read_text()
 for k in(0,5,11,19,1,2,3,4,6,7,8,9,10,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27):
  its,st=state(k);mm=mesh_items(its)
  if st.get('envelope_only'):mm.extend(wires.envelope_meshes(__import__(__name__),st))
  if not st['explanatory']:mm.extend(wires.local_meshes(__import__(__name__),st))
  data[k]=mm;poses[k]=st;(OUT/'previews'/f'state_{k}.json').write_text(json.dumps(mm,separators=(',',':')))
  if len(data) not in (1,5,28):
   print('MESH_READY',len(data),'states',flush=True);continue
  order=sorted(data);payload=base64.b64encode(gzip.compress(json.dumps([data[j] for j in order],separators=(',',':')).encode(),5)).decode()
  html=tpl.replace('__PAYLOAD__',payload).replace('__NAMES__',json.dumps([poses[j]['label'] for j in order],ensure_ascii=False)).replace('__POSES__',json.dumps([poses[j] for j in order],ensure_ascii=False))
  for n in('viewer.html','progress_now.html'):
   tmp=OUT/(n+'.tmp');tmp.write_text(html);tmp.replace(OUT/n)
  print('HTML_READY',len(data),'states',flush=True)
 (OUT/'validation/states.json').write_text(json.dumps([poses[j] for j in sorted(poses)],ensure_ascii=False,indent=2))
 counts={}
 for q in state(0)[0]:
  if not q.reference:counts[q.part]=counts.get(q.part,0)+1
 cat={}
 for old in (OUT/'stl').glob('*.stl'):
  if old.stem not in counts:old.unlink()
 for n,cnt in counts.items():
  s=PARTS[n];bb=s.BoundingBox();cat[n]=dict(META[n],count=cnt,bbox_mm=[bb.xlen,bb.ylen,bb.zlen],valid=s.isValid())
  exporters.export(s,str(OUT/'stl'/f'{n}.stl'),tolerance=.1,angularTolerance=.2)
 with (OUT/'parts.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['part','count','description','group','solids']);w.writerows([[n,cnt,META[n]['description'],META[n]['group'],META[n]['solids']] for n,cnt in sorted(counts.items())])
 (OUT/'validation/catalogue.json').write_text(json.dumps(cat,ensure_ascii=False,indent=2))
 for old in (OUT/'step').glob('assembly_*.step'):old.unlink()
 for k in(0,5,11,18):
  assembly(state(k)[0],'TF_V012_'+str(k)).export(str(OUT/'step'/f'assembly_{k}.step'));print('STEP',k,flush=True)
 for side in('old','new'):
  sub=[q for q in state(0)[0] if q.name.startswith(side+'_') and q.group not in('reference','holder')]
  assembly(sub,'Independent_'+side).export(str(OUT/'step'/('module_'+side+'.step')))
 print('DONE',len(counts),'active CAD parts',flush=True)
if __name__=='__main__':publish()
