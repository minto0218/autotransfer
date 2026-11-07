"""Positive constraints and a denser pusher path: collision-free is not a force test."""
import json,math
import build as b
from validate import overlap
b.make_parts();items,p=b.state(0);H={q.name.removeprefix('head_'):q for q in items if q.name.startswith('head_')};tests=[]
def blocked(name,moving,fixed,expected=True):
 v=overlap(moving,fixed);row=dict(test=name,overlap_mm3=v,expected_block=expected,pass_=(v>.001 if expected else v<.001));tests.append(row);print('CONSTRAINT',row,flush=True)
# Captured driver: small free gaps, then shoulders stop axial escape.
fixed_lower=b.uni(H['push_cam_L'].shape,H['push_cam_R'].shape)
fixed_upper=b.uni(H['chassis_L'].shape,H['chassis_R'].shape)
blocked('drum_down_0.05_free',H['push_drum'].shape.translate((0,0,-.05)),fixed_lower,False)
blocked('drum_down_0.15_hits_shoulder',H['push_drum'].shape.translate((0,0,-.15)),fixed_lower)
blocked('drum_up_0.10_free',H['push_drum'].shape.translate((0,0,.1)),fixed_upper,False)
blocked('drum_up_0.25_hits_upper_guide',H['push_drum'].shape.translate((0,0,.25)),fixed_upper)
for dz in(-.3,.3):blocked('park_pin_blocks_rod_'+str(dz),H['push_rod'].shape.translate((0,0,dz)),H['press_home_lock'].shape)
# The rack carriage cannot be lifted clear or pulled beyond its opening stop.
for gap in(5,25,35):
 its,_=b.state(0,override=dict(gap=gap,twist=0,push=0,press_lock=False));h={q.name:q for q in its};jaw=h['head_jaw_1'].shape;cage=b.uni(h['head_guide_cage'].shape,*[q.shape for q in its if q.part=='jaw_guide_endcap'])
 blocked('jaw_lift_0.5_at_gap'+str(gap),jaw.translate((0,0,.5)),cage)
 blocked('jaw_down_0.3_at_gap'+str(gap),jaw.translate((0,0,-.3)),cage)
blocked('jaw_overopening_0.4_stop',H['jaw_1'].shape.translate((0,.4,0)),b.uni(H['guide_cage'].shape,H['guide_endcap_-1'].shape,H['guide_endcap_1'].shape))
# The non-round bore mechanically blocks a relative angle, although it has play.
for push in(0,10,20):
 its,_=b.state(0,override=dict(gap=35,twist=0,push=push,press_lock=False));h={q.name:q for q in its};rod=h['head_push_rod'].shape;driver=h['head_push_drum'].shape
 for a in(-10,10):blocked('double_D_blocks_'+str(a)+'_at_push'+str(push),driver.rotate((0,0,0),(0,0,1),a),rod)
# Drive/rod centre is the Z axis, so this records analytical nominal overlap at all strokes.
engagement=[dict(push=s,rod_top_local_z=50-s,driver_top_local_z=29.3,flat_engagement_mm=4.8,top_margin_mm=50-s-29.3)for s in(0,10,20)]
path=[]
for n in range(41):
 push=n/2;its,_=b.state(0,override=dict(gap=35,twist=0,push=push,press_lock=False));mov=[q for q in its if q.part in('push_rotating_plunger','pusher_follower_pin')];fixed=[q for q in its if q.part in('push_cam_left','push_cam_right','push_cam_alignment_key','module_case_L','module_case_R','push_sliding_drive')]
 for a in mov:
  for c in fixed:
   v=overlap(a.shape,c.shape)
   if v>.025:path.append(dict(push=push,moving=a.name,fixed=c.name,overlap_mm3=v))
print('PUSHER_PATH',len(path),'contacts',flush=True)
# Self-zero uses the SHORT follower with no indexing pin: end faces stop both ends.
for angle,offset,expect in [(0,-1,True),(0,.5,False),(30,-.5,False),(30,1,True)]:
 its,_=b.state(0,override=dict(gap=25,twist=angle,push=0,press_lock=False));h={q.name:q for q in its}
 blocked('twist_stop_'+str(angle)+'_offset'+str(offset),h['head_motion_follower'].shape.rotate((0,0,0),(0,0,1),offset),h['head_chassis_R'].shape,expect)
# Angular sweep samples with the short follower installed throughout.
rotparts={'twist_upper_drum','twist_guide_cage','parallel_jaw_rack','grip_drum_pinion','grip_pinion_insert','twist_return_spool_L','twist_return_spool_R','rotor_M12_screw','pinion_M14_screw','return_spool_M14_screw','jaw_guide_endcap','guide_endcap_M14_screw','twist_motion_follower'}
twist_contacts=[];twist_samples=[]
for gap,angle in [(25,a)for a in range(31)]+[(g,a)for g in(5,35)for a in(0,15,30)]:
 its,_=b.state(0,override=dict(gap=gap,twist=angle,push=0,press_lock=False));moving=[q for q in its if q.part in rotparts or q.name in('head_grip_cable_stop','head_twist_cable_stop')];fixed=[q for q in its if q not in moving]
 for a in moving:
  for c in fixed:
   v=overlap(a.shape,c.shape)
   if v>.025:twist_contacts.append(dict(gap=gap,angle=angle,a=a.name,b=c.name,volume=v))
 twist_samples.append(dict(gap=gap,angle=angle))
import prototype
spring_table=[]
for angle in(0,15,30):
 q=prototype.RETURN[1];length=prototype.return_path(q,angle)['spring_length'];spring_table.append(dict(angle=angle,length_mm=length,extension_mm=length-14,return_torque_lower_bound_Nmm=(length-14)*.05*4))
print('TWIST_PATH',len(twist_contacts),'contacts',flush=True)
report=dict(scope=__doc__,twist_samples=twist_samples,twist_contacts=twist_contacts,twist_spring=spring_table,positive_constraints=tests,pusher_samples=41,pusher_contacts=path,flat_engagement=engagement,nominal_clearances=dict(carriage_lower=.15,carriage_upper=.2,carriage_lateral=.2,carriage_upper_lip_overlap=.5,rack_outer_guide=.2,rack_upper_guide=.2,driver_lower_axial=.1,driver_upper_axial=.2,shaft_to_bore_flat=.1),pass_=all(q['pass_']for q in tests)and not path and not twist_contacts and all(q['extension_mm']>0 for q in spring_table))
(b.OUT/'validation/function.json').write_text(json.dumps(report,indent=2));print('FUNCTION_PASS',report['pass_'],flush=True)
if not report['pass_']:raise SystemExit(1)
