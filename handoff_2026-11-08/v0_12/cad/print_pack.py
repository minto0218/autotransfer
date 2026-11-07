"""Export bed-oriented FDM parts, test jig, coupons, and explicit hardware separation."""
import json,csv
import build as b
PRINT_HARDWARE={'shaft_clip_2','shaft_clip_3','shaft_clip_5','root_parallel_stub','elbow_parallel_axle','head_main_stub','head_parallel_stub','input_support_bush','tube_reducer_25','upper_PTFE_adapter','spring_tendon_eye','cable_stop_button','pusher_follower_pin','jaw_lock_pin','twist_lock_pin','joint_home_lock_pin'}
def run():
 b.make_parts()
 import bench_anchor
 bench_anchor.make(b)
 out=b.OUT/'print';out.mkdir(exist_ok=True);counts={}
 for q in b.state(0)[0]:
  if not q.reference:counts[q.part]=counts.get(q.part,0)+1
 for n in('fit_coupon','fit_coupon_pin','bench_head_stand','bench_anchor_back','bench_anchor_front','manual_pull_tab'):counts[n]=3 if n=='manual_pull_tab'else 1
 rows=[]
 for n,count in counts.items():
  group=b.META[n]['group']
  if group=='hardware'and n not in PRINT_HARDWARE:continue
  sh=b.PARTS[n];notes=[]
  if n in('module_case_L','module_case_R'):sh=b.ry(sh,90 if n.endswith('L')else-90);notes.append('半割の平面をベッドへ・内部案内へサポートを入れない')
  elif n in('root_output_shaft','elbow_output_shaft','root_input_shaft','elbow_input_shaft'):
   sh=b.rx(sh,30);notes.append('六角の平面を下にして軸を寝かせる・長い軸の立て印刷を避ける')
  elif n=='elbow_parallel_axle':notes.append('長軸を寝かせる・外側の取り除ける支持のみ')
  elif n=='column_reaction_bracket':
   sh=b.rx(b.rz(sh,-__import__('math').degrees(__import__('math').atan2(40,-30.5))),90);notes.append('斜め梁と縦受けの面を寝かせる')
  elif n.startswith('shaft_clip_')or n in('root_parallel_stub','elbow_parallel_axle','head_main_stub','head_parallel_stub','upper_keyed_shaft','root_input_shaft','elbow_input_shaft','root_output_shaft','elbow_output_shaft'):sh=b.ry(sh,-90);notes.append('軸方向をZへ・長軸はブリム')
  elif n in('arm_stage1','arm_stage2','parallel_stage1','parallel_stage2','joint_input_pinion','joint_output_gear','root_output_gear','elbow_output_gear','upper_driver36','upper_pinion18','upper_grip_drum','upper_joint_drum','upper_direct_drum','upper_twist_dual_drum','joint_input_drum'):sh=b.ry(sh,-90);notes.append('歯車／アームの平面をベッドへ')
  elif n in('bench_anchor_back','bench_anchor_front'):
   sh=b.rx(sh,90);notes.append('平らな背面をベッドへ・支柱用の開口を上へ')
  elif n.startswith('fairlead_cover_'):sh=b.ry(sh,90);notes.append('案内蓋の平面をベッドへ')
  elif n.startswith('push_cam_'):sh=b.ry(sh,90 if n.endswith('left')else-90);notes.append('半割面をベッドへ・螺旋溝内のサポート禁止')
  elif n=='push_rotating_plunger':notes.append('足を下に・ブリム・横穴は印刷後Ø1.1でさらう')
  elif n=='spring_cassette':sh=b.ry(sh,90);notes.append('共通側板の外面をベッド側へ・後梁の張出し0.5mm分の薄い支持を板下面へ・輪の軸穴へ支持を入れない')
  else:notes.append('接地面を確認・必要な支持のみ・摺動面への支持を避ける')
  bb=sh.BoundingBox();sh=sh.translate((5-bb.xmin,5-bb.ymin,-bb.zmin));bb=sh.BoundingBox()
  if max(bb.xlen,bb.ylen)>246:
   sh=b.rx(sh,90);bb=sh.BoundingBox();sh=sh.translate((5-bb.xmin,5-bb.ymin,-bb.zmin));bb=sh.BoundingBox()
  fits=bb.xlen<=246 and bb.ylen<=246 and bb.zlen<=250
  b.exporters.export(sh,str(out/(n+'.stl')),tolerance=.04,angularTolerance=.12)
  per_head=next((sum(q.part==n for q in b.state(0)[0]if q.name.startswith('old_'))for _ in[0]),0)
  rows.append(dict(part=n,full_unit_quantity=count,one_head_quantity=per_head,volume_mm3=round(sh.Volume(),3),bed_bbox_mm=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],fits_A1_256_with_margin=fits,solids=len(sh.Solids()),notes='／'.join(notes)))
 wanted={q['part']for q in rows}
 for stale in out.glob('*.stl'):
  if stale.stem not in wanted:stale.unlink()
 with(out/'印刷一覧.csv').open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (b.OUT/'validation/print_pack.json').write_text(json.dumps(dict(parts=rows,all_fit=all(q['fits_A1_256_with_margin']for q in rows),all_single_solid=all(q['solids']==1 for q in rows),scope='BRep solidity and bounding-box fit, orientation proposals; slicer supports and actual FDM quality require inspection.'),ensure_ascii=False,indent=2))
 fixture=[q for q in b.state(0)[0]if q.name.startswith('old_')and q.group not in('reference','holder')]
 fixture=[b.Item(q.name,q.part,q.shape.translate((b.P['vial_pitch']/2,0,-116)),q.group,q.color)for q in fixture]
 fixture.append(b.Item('bench_stand','bench_head_stand',b.PARTS['bench_head_stand'],'fixture','#526c80'))
 for n in('bench_anchor_back','bench_anchor_front'):fixture.append(b.Item(n,n,b.PARTS[n],'fixture','#526c80'))
 for x in(-16,0,16):fixture.append(b.Item('manual_outer_anchor_'+str(x),'upper_PTFE_adapter',b.rx(b.PARTS['upper_PTFE_adapter'],90).translate((x,-50,20)),'hardware','#83949d'))
 world=[b.Item(q.name,q.part,q.shape.translate((-b.P['vial_pitch']/2,0,116)),q.group,q.color)for q in fixture]
 (b.OUT/'previews/state_28.json').write_text(json.dumps(b.mesh_items(world),separators=(',',':')))
 pose=b.state(0)[1];pose.update(label='卓上治具：ヘッド1個の手動確認（バイアルなし）',explanatory='bench',bench_only=True)
 (b.OUT/'validation/bench_pose.json').write_text(json.dumps(pose,ensure_ascii=False,indent=2))
 b.assembly(fixture,'Bench_head').export(str(b.OUT/'step/bench_head.step'))
 print('PRINT_PACK',len(rows),'fit',all(q['fits_A1_256_with_margin']for q in rows),'single',all(q['solids']==1 for q in rows),flush=True)
if __name__=='__main__':run()
