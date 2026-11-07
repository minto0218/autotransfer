#!/usr/bin/env python3
"""Independent manual bench generation. Run: python cad/bench.py"""
import json,csv,math,gzip,base64,hashlib,collections
from pathlib import Path
import numpy as np
import build as b
R=b.ROOT;O=b.OUT
PRINT_HARDWARE={'tube_reducer_25','cable_stop_button','pusher_follower_pin','jaw_lock_pin','twist_lock_pin','twist_motion_follower'}
FINE={'module_case_R','grip_drum_pinion','grip_pinion_insert','parallel_jaw_rack','twist_upper_drum','twist_return_spool_L','twist_return_spool_R','push_cam_left','push_cam_right','push_sliding_drive','return_idler','spring_cassette','cable_stop_button','tube_reducer_25','twist_lock_pin','twist_motion_follower','push_rotating_plunger','press_home_lock_pin','push_cam_alignment_key','case_alignment_key','jaw_guide_endcap'}
NAMES={'bench_head_stand':'卓上支持台','module_case_L':'ケース左半割','module_case_R':'ケース右半割','parallel_jaw_rack':'5mm爪付きラック','twist_guide_cage':'爪のガイド籠','twist_upper_drum':'上ねじりドラム','grip_drum_pinion':'下把持ドラム','grip_pinion_insert':'別体24歯ピニオン','twist_return_spool_L':'戻し輪左半割','twist_return_spool_R':'戻し輪右半割','push_cam_left':'押込みカム左半割','push_cam_right':'押込みカム右半割','push_sliding_drive':'押込みドラム','push_rotating_plunger':'押し足一体棒','spring_cassette':'水平ばね共通側板','return_idler':'戻し糸の自由案内輪','manual_pull_tab':'手引きつまみ・G/T/P','fit_coupon':'嵌合確認片','fit_coupon_pin':'嵌合確認ピン','pusher_follower_pin':'フォロワピン・印刷比較用','cable_stop_button':'糸端のビーズ','tube_reducer_25':'縦出口のフェルール','rear_cable_retainer':'3線押えコーム','jaw_lock_pin':'爪開放固定ピン','twist_lock_pin':'0度固定ピン・長軸', 'twist_motion_follower':'動作確認ピン・短軸','opening_gauge_5':'5mm開口ゲージ','jaw_guide_endcap':'爪レールの着脱端止め','guide_endcap_M14_screw':'端止めねじ M1.4×4','press_home_lock_pin':'棒の上端固定ピン','push_cam_alignment_key':'半割カムの合わせキー','case_alignment_key':'ケースの合わせキー','fairlead_cover_G':'G糸案内蓋','fairlead_cover_T':'T糸案内蓋','fairlead_cover_P':'P糸案内蓋'}

def generate():
 b.make_parts();items,p=b.state(0);counts=collections.Counter(q.part for q in items)
 counts.update({'fit_coupon':1,'fit_coupon_pin':1,'twist_motion_follower':1});rows=[]
 for n,c in sorted(counts.items()):
  if b.META[n]['group']=='hardware'and n not in PRINT_HARDWARE:continue
  sh=b.PARTS[n];notes='接地面と支持をスライサーで確認'
  if n in('module_case_L','module_case_R'):sh=b.ry(sh,90 if n.endswith('L')else-90);notes='半割面をベッド側。内部ガイドへ支持を埋めない'
  elif n.startswith('fairlead_cover_'):sh=b.ry(sh,90);notes='平らな面をベッドへ。糸溝への支持なし'
  elif n.startswith('push_cam_'):sh=b.ry(sh,90 if n.endswith('left')else-90);notes='半割面をベッド側。カム溝の支持なし'
  elif n in('press_home_lock_pin','jaw_lock_pin'):sh=b.ry(sh,-90);notes='頭を下にして軸を立てる・小さなブリム・穴と軸を現物合わせ'
  elif n in('push_cam_alignment_key','case_alignment_key'):notes='平らな面をベッドへ・小キー用のブリムは除去して組む'
  elif n=='spring_cassette':sh=b.ry(sh,90);notes='側板外面をベッド側。曲線リブも同じ外面へ収まる。輪の隙間と軸穴は空ける'
  elif n=='push_rotating_plunger':notes='押し足を下。ブリム。Ø1.1横穴を仕上げる'
  bb=sh.BoundingBox();sh=sh.translate((-bb.xmin,-bb.ymin,-bb.zmin));bb=sh.BoundingBox()
  b.exporters.export(sh,str(O/'print'/(n+'.stl')),tolerance=.025,angularTolerance=.1)
  rows.append(dict(part=n,name=NAMES.get(n,n),quantity=c,nozzle_mm='0.2推奨'if n in FINE else'0.4可',layer_mm='0.06〜0.08'if n in FINE else'0.12〜0.16',bbox_mm=[round(bb.xlen,3),round(bb.ylen,3),round(bb.zlen,3)],solids=len(sh.Solids()),valid=sh.isValid(),fits_A1=bb.xlen<=246 and bb.ylen<=246 and bb.zlen<=250,notes=notes))
 with(O/'印刷部品一覧.csv').open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.writer(f);w.writerow(['STL名','部品名','印刷個数','推奨ノズル','積層mm','外形mm','印刷方向・仕上げ'])
  for q in rows:w.writerow([q['part']+'.stl',q['name'],q['quantity'],q['nozzle_mm'],q['layer_mm'],q['bbox_mm'],q['notes']])
 (O/'validation/print_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 for k,filename in [(0,'卓上手動治具_組立.step'),(6,'卓上手動治具_押込み20mm.step'),(8,'卓上手動治具_分解.step')]:
  b.assembly(b.state(k)[0],'Manual_bench_'+str(k)).export(str(O/'step'/filename));print('STEP',filename,flush=True)
 export_viewer()
 sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((R/'cad').glob('*'))if p.suffix in('.py','.json')}
 (O/'validation/source_hashes.json').write_text(json.dumps(sources,indent=2))
 print('GENERATED',len(rows),'types',sum(q['quantity']for q in rows),'pieces',flush=True)

def export_viewer():
 import wire_paths
 meshes={};states=[]
 for k in range(len(b.BENCH_STATES)):
  items,p=b.state(k);inst=[]
  for q in items:
   if q.part not in meshes:
    vv,ff=b.PARTS[q.part].tessellate(.12,.25);meshes[q.part]=dict(v=np.array([[v.x,v.y,v.z]for v in vv]).round(4).tolist(),f=ff)
   T=getattr(q.shape,'_mesh_pose',None)
   if T is None:raise ValueError('Missing exact transform '+q.name)
   inst.append(dict(name=q.name,part=q.part,group=q.group,color=q.color,T=np.array(T).round(8).tolist()))
  states.append(dict(p,items=inst,lines=[]if p.get('explode')else wire_paths.lines(p)))
 for name in('push_sliding_drive','module_case_R'):
  sh=b.PARTS[name].intersect(b.box(50,60,100,(25,0,-20)))
  if name=='module_case_R':sh=sh.intersect(b.cyl(6,18,(0,0,18.5)))
  vv,ff=sh.tessellate(.08,.20);meshes[name+'@section']=dict(v=np.array([[v.x,v.y,v.z]for v in vv]).round(4).tolist(),f=ff)
 data=dict(meshes=meshes,states=states,part_names=NAMES)
 packed=base64.b64encode(gzip.compress(json.dumps(data,separators=(',',':')).encode(),6)).decode()
 html=(R/'cad/viewer_template.html').read_text().replace('__PAYLOAD__',packed)
 (O/'卓上手動治具.html').write_text(html)
 print('HTML_BYTES',len(html.encode()),flush=True)
 (O/'validation/poses.json').write_text(json.dumps([{k:v for k,v in p.items()if k not in('items','lines')}for p in states],ensure_ascii=False,indent=2))

if __name__=='__main__':generate()
