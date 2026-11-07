"""Sample actual insertion directions at the assembly home pose.
This is a geometric path check, not a physical assembly or tooling-access guarantee.
"""
import json
import build as b
from validate import overlap

def run():
 b.make_parts();its,st=b.state(0);head={q.name.removeprefix('head_'):q for q in its if q.name.startswith('head_')};rows=[];checks=0
 def test(label,shape,others):
  nonlocal checks
  for q in others:
   checks+=1;v=overlap(shape,q.shape)
   if v>.025:rows.append(dict(step=label,part=q.name,overlap_mm3=round(v,6)))
 core=[q for n,q in head.items()if q.part in('push_cam_left','push_cam_right','push_rotating_plunger','pusher_follower_pin','push_sliding_drive','grip_drum_pinion','grip_pinion_insert','twist_upper_drum','twist_guide_cage','parallel_jaw_rack','rotor_M12_screw','pinion_M14_screw','cable_stop_button','twist_return_spool_L','twist_return_spool_R','return_spool_M14_screw','push_cam_alignment_key','case_alignment_key')]
 for side,sg in(('L',-1),('R',1)):
  for distance in(20,10,5,2,1,.3,0):test('case_'+side+'_offset_'+str(distance),head['chassis_'+side].shape.translate((sg*distance,0,0)),core)
 for side,sg in(('L',-1),('R',1)):
  for distance in(8,4,2,1,.3,0):test('cam_'+side+'_offset_'+str(distance),head['push_cam_'+side].shape.translate((sg*distance,0,0)),[head['push_rod'],head['follower_pin']]+[q for q in head.values()if q.part=='push_cam_alignment_key'])
 # Bench arc guide obstructs later side insertion: fit the split ring BEFORE closing cases.
 fixed=[head['push_drum'],head['push_rod'],head['push_cam_L'],head['push_cam_R'],head['twist_drum']]
 for side,sg in(('L',-1),('R',1)):
  for dx in(20,12,5,1,0):test('return_half_'+side+'_side_'+str(dx),head['return_spool_'+side].shape.translate((sg*dx,0,1.7)),fixed)
  for dz in(1.7,1,.3,0):test('return_half_'+side+'_lower_'+str(dz),head['return_spool_'+side].shape.translate((0,0,dz)),fixed)
 # Insert each carriage from its own end, then close that end with a screwed stop.
 for sign in(-1,1):
  jaw=head['jaw_'+str(sign)]
  for d in(25,15,8,3,1,.3,0):test('jaw_from_end_'+str(sign)+'_'+str(d),jaw.shape.translate((0,sign*d,0)),[head['guide_cage']])
  cap=head['guide_endcap_'+str(sign)]
  for d in(12,5,1,.3,0):test('endcap_from_end_'+str(sign)+'_'+str(d),cap.shape.translate((0,sign*d,0)),[head['guide_cage'],head['jaw_-1'],head['jaw_1']])
 # Lower drive is screwed together before entering the cage; upper twist drum is absent.
 lower=[head['grip_drum'],head['pinion_insert'],head['pinion_screw_-4.1'],head['pinion_screw_4.1']]
 for distance in(25,15,8,3,0):
  for q in lower:test('lower_stack_from_above_'+str(distance),q.shape.translate((0,0,distance)),[head['guide_cage'],head['jaw_-1'],head['jaw_1']])
 # Integral foot stays below; stem enters guide/coupler before the cross pin is inserted.
 for distance in(60,35,20,5,0):test('rod_from_below_'+str(distance),head['push_rod'].shape.translate((0,0,-distance)),[head['push_cam_L'],head['push_cam_R'],head['push_drum']])
 # Assemble the cassette outside the head: three wheels enter open slots from -Y.
 from types import SimpleNamespace
 rail=SimpleNamespace(name='spring_plate',shape=b.PARTS['spring_cassette'])
 for q in __import__('prototype').RETURN:
  for offset in(15,10,5,2,.3,0):test('idler_side_'+str(q['z'])+'_'+str(offset),b.PARTS['return_idler'].translate((14,-24-offset,q['z'])),[rail])
 wheels=[SimpleNamespace(name='wheel_'+str(q['z']),shape=b.PARTS['return_idler'].translate((14,-24,q['z'])))for q in __import__('prototype').RETURN]
 for dz in(20,10,5,1,.3,0):test('common_idler_axle_'+str(dz),b.PARTS['idler_common_axle'].translate((0,0,-dz)),[rail]+wheels)
 # The upper parking pin enters from the left after the case is closed.
 for distance in(20,10,5,2,1,.3,0):test('press_home_pin_'+str(distance),head['press_home_lock'].shape.translate((-distance,0,0)),[q for q in its if q.name!='head_press_home_lock'])
 fits=[]
 # Lower the complete head onto the bench ledge before adding its two bolts.
 stand=next(q for q in its if q.name=='stand')
 for distance in(25,10,3,.3,0):
  for q in head.values():
   if q.part not in('module_M2_bolt','module_M2_nut'):test('head_onto_stand_'+str(distance),q.shape.translate((0,0,distance)),[stand])
 report=dict(sampled_distance_tests=checks,contacts=rows,hex_insertion_fits=fits,scope='Selected home-pose case/cam closing, lower-stack insertion, rod insertion without cross pin. Fasteners removed in the stated order. No tool envelope, elastic clip insertion, knot or hand-access certification.')
 (b.OUT/'validation/assembly_paths.json').write_text(json.dumps(report,indent=2));print('ASSEMBLY_PATHS',checks,'contacts',rows,flush=True)
if __name__=='__main__':run()
