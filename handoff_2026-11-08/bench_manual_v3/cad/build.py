#!/usr/bin/env python3
"""Standalone single-head manual bench. No vial, servo or machine assembly.
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

def make_parts():
 global BUILT
 if BUILT:return
 import sys,head,prototype
 me=sys.modules[__name__];head.make(me);prototype.apply(me)
 # Manual-only angular stop: the servo is absent, so the spring must meet a stop.
 import numpy as np
 aa=np.radians(np.linspace(-12,40,81));poly=[(16.5*math.cos(a),16.5*math.sin(a))for a in aa]+[(12.3*math.cos(a),12.3*math.sin(a))for a in aa[::-1]]
 guide=cq.Workplane('XY').polyline(poly).close().extrude(1.5).val().translate((0,0,20.3))
 aa=np.radians(np.linspace(0,30,61));poly=[(14*math.cos(a),14*math.sin(a))for a in aa]+[(12.9*math.cos(a),12.9*math.sin(a))for a in aa[::-1]]
 slot=cq.Workplane('XY').polyline(poly).close().extrude(2).val().translate((0,0,20.1))
 for a in(0,30):slot=uni(slot,cyl(.55,2,(13.45*math.cos(math.radians(a)),13.45*math.sin(math.radians(a)),20.1)))
 # Tangent planes make the nominal pin-centre stops exactly 0 and +30 degrees.
 slot=slot.intersect(box(100,100,4,(0,49.65,19.1))).intersect(rz(box(100,100,4,(0,-49.65,19.1)),30))
 guide=cut(guide,slot)
 for a in(-10,38):guide=uni(guide,cyl(1.2,1.5,(15.2*math.cos(math.radians(a)),15.2*math.sin(math.radians(a)),19.3)))
 part('module_case_R',uni(cut(PARTS['module_case_R'],slot.translate((0,0,-1.3))),guide),'ケース右・手動用ねじり端止めガイド一体','head_fixed')
 part('twist_lock_pin',uni(cyl(.35,8,(13.45,0,14.3)),cyl(1.3,1.2,(13.45,0,22.3))),'長い0度固定ピン・ケースと上ドラムを共に貫く','lock')
 part('twist_motion_follower',uni(cyl(.35,5.1,(13.45,0,17.2)),box(2.6,2.6,1.2,(13.45,0,22.3))),'短い動作用ピン・固定ケースに届かず上ドラムと回る','lock')
 part('opening_gauge_5',uni(box(10,5,5),box(18,3,2,(9,0,3))),'5mm開口の確認ゲージ・横の柄を持って入れる','fixture')
 import refinements
 refinements.apply(me)
 mesh_cache.tag(PARTS);BUILT=True

# Manual bench floor is Z0; head datum is 42mm above the floor.
BENCH_STATES=[
 dict(label='初期・開口35mm・固定ピンあり',gap=35,twist=0,push=0,locks=True),
 dict(label='開口25mm・把持の確認',gap=25,twist=0,push=0),
 dict(label='開口5mm・最小開口の確認',gap=5,twist=0,push=0),
 dict(label='開口25mmを保って＋30°ねじり',gap=25,twist=30,push=0),
 dict(label='ねじりを0°の戻り端へ復帰',gap=25,twist=0,push=0),
 dict(label='押込み10mm・60°回転',gap=35,twist=0,push=10),
 dict(label='押込み20mm・120°回転',gap=35,twist=0,push=20),
 dict(label='初期位置へ復帰・ピンを再装着',gap=35,twist=0,push=0,locks=True),
 dict(label='分解図：組立順の確認',gap=35,twist=0,push=0,explode=True),
 dict(label='押込み準備：棒の上端固定ピンを抜く',gap=35,twist=0,push=0,press_lock=False),
]

def state(k=0,override=None):
 make_parts();p=dict(BENCH_STATES[k]if override is None else override);tw=p['twist'];gap=p['gap'];push=p['push'];
 if not -1e-8<=tw<=30+1e-8:raise ValueError('B3 twist range is 0 to +30 degrees')
 delta=-math.degrees((35-gap)/12);its=[]
 def add(n,part,s=None,at=(0,0,0),yaw=0,color=None):
  sh=rz((PARTS[part]if s is None else s).translate(at),yaw)
  if p.get('explode'):
   dx=(-27 if part=='module_case_L'else 27 if part=='module_case_R'else 55 if part in('spring_cassette','return_idler','idler_common_axle','idler_axle_nut','spring_hook_screw','cassette_M2_screw')else 0)
   dz=45 if part in('twist_upper_drum','rotor_M12_screw','twist_return_spool_L','twist_return_spool_R','return_spool_M14_screw')else 25 if part in('grip_drum_pinion','grip_pinion_insert','pinion_M14_screw')else 65 if part.startswith('push_')or part=='pusher_follower_pin'else 0
   sh=sh.translate((dx,0,dz))
  gr=META[part]['group'];its.append(Item(n,part,sh.translate((0,0,42)),gr,color or COL.get(gr,'#83949d')))
 def head(n,part,s=None,at=(0,0,0),yaw=0,group=None,color=None):add('head_'+n,part,s,at,yaw,color)
 head('chassis_L','module_case_L');head('chassis_R','module_case_R')
 head('twist_drum','twist_upper_drum',yaw=tw,color='#2f8999');head('guide_cage','twist_guide_cage',yaw=tw,color='#2f8999')
 for sign in(-1,1):head('rotor_screw_'+str(sign),'rotor_M12_screw',at=(sign*12,0,0),yaw=tw)
 head('grip_drum','grip_drum_pinion',yaw=tw+delta,color='#cd9455')
 head('grip_cable_stop','cable_stop_button',at=(0,-9,13.2),yaw=tw+delta,color='#a18154')
 head('twist_cable_stop','cable_stop_button',at=(0,11.5,18.2),yaw=tw,color='#a18154')
 for sign in(-1,1):head('jaw_'+str(sign),'parallel_jaw_rack',s=PARTS['parallel_jaw_rack']if sign>0 else rz(PARTS['parallel_jaw_rack'],180),at=(0,sign*(gap/2+1.5),0),yaw=tw,color='#7fa4a4')
 for sign in(-1,1):
  a=tw+(0 if sign>0 else 180)
  head('guide_endcap_'+str(sign),'jaw_guide_endcap',at=(0,21.7,0),yaw=a)
  for x in(-10,10):head('guide_endcap_screw_'+str(sign)+'_'+str(x),'guide_endcap_M14_screw',at=(x,22.7,0),yaw=a)
 import prototype
 prototype.place_head(__import__(__name__),head,tw,delta,push)
 head('push_cam_L','push_cam_left');head('push_cam_R','push_cam_right')
 head('push_rod','push_rotating_plunger',at=(0,0,-push),yaw=push/20*120)
 head('push_drum','push_sliding_drive',yaw=push/20*120)
 head('press_cable_stop','cable_stop_button',at=(6,0,28.5),yaw=push/20*120,color='#a18154')
 head('cable_retainer','rear_cable_retainer')
 for xx in(-3,4):head('retainer_screw_'+str(xx),'retainer_M12_screw',at=(xx,-24,0))
 if p.get('locks'):
  for yy in(-19,19):head('jaw_lock_'+str(yy),'jaw_lock_pin',at=(-12.5,yy,5.5))

 if p.get('locks'):head('twist_lock','twist_lock_pin')
 else:head('motion_follower','twist_motion_follower',yaw=tw)
 p['press_lock_on']=p.get('press_lock',push==0)
 if p['press_lock_on']:head('press_home_lock','press_home_lock_pin')
 for y,z in ((-31.8,25.3),(-28.2,32.8)):head('case_key_'+str(z),'case_alignment_key',at=(0,y,z-.45))
 for y,z in ((2.15,18.),(-2.15,22.8)):head('cam_key_'+str(z),'push_cam_alignment_key',at=(0,y,z-.7))
 for dx in(-5,5):
  head('mount_bolt_'+str(dx),'module_M2_bolt',at=(dx,-30,0));head('mount_nut_'+str(dx),'module_M2_nut',at=(dx,-30,0))
 for j,(wx,yy)in enumerate(((10.25,-18),(-13,-18),(-7.3,-15))):head('outer_ferrule_'+str(j),'tube_reducer_25',at=(wx,yy,40.5))
 # No external housing: each main tendon is pulled vertically through a hand tab.
 p['relative']=delta;p['grip_angle']=tw+delta
 p['pull_mm']=[-10.25*math.radians(tw+delta),13*math.radians(tw),7.3*math.radians(push/20*120)]
 for tag,(x,y,z),pull in zip(('G','T','P'),((10.25,-18,70),(-13,-18,80),(-7.3,-15,60)),p['pull_mm']):
  add('handle_'+tag,'manual_pull_tab',at=(x,y,z+pull),color={'G':'#c9913c','T':'#4f8eae','P':'#ba7295'}[tag])
 add('stand','bench_head_stand')
 add('gauge_5','opening_gauge_5',at=(0,0,-16)if k==2 else(0,8,-38),color='#bd9363')
 return its,p

def assembly(items,name):
 ass=cq.Assembly(name=name)
 for q in items:ass.add(q.shape,name=q.name,color=cq.Color(*[int(q.color[i:i+2],16)/255 for i in(1,3,5)]))
 return ass
