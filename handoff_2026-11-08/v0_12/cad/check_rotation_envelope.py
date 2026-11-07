"""Rotation-invariant containment certificate for pitch, plus own fixed-part checks.
A circular bound remains valid at every angle, rather than relying on angular steps.
"""
import json,math
import cadquery as cq
import build as b
from validate import overlap
from control_model import interpolate
ROT={'twist_upper_drum','twist_guide_cage','rotor_M12_screw','grip_drum_pinion','grip_pinion_insert','twist_return_spool_L','twist_return_spool_R','return_spool_M14_screw','pinion_M14_screw','parallel_jaw_rack','contact_pad_5mm'}
def rotating(q):return q.part in ROT or q.name.endswith(('grip_cable_stop','twist_cable_stop'))
def run():
 b.make_parts();R=b.P['rotation_envelope_r'];pitch=b.P['vial_pitch'];rows=[];maxr=0
 # Cylindrical strata follow the axial levels of cage, rack, drum and pads.
 bands=[(-16,-11,2.5,22.5),(-11,3,7,22.5),(3,4,3.4,25),(4,7,3.15,25),(7,7.3,6.5,25),(7.3,10.5,3.1,25),(10.5,14,3.2,12.9),(14,16,3.2,12.9),(16,19,5,14),(19,20.6,5,12),(20.6,22.6,3.4,12),(22.6,23.1,9,12)]
 local=b.uni(*[b.ring(ro,ri,hi-lo,lo)for lo,hi,ri,ro in bands]);sweep=local.translate((-pitch/2,0,116));outer=b.cyl(R,40,(-pitch/2,0,100))
 # The added return supports only operate through +/-30deg. Their full-circle
 # annulus crosses the rear fixed cam rib, so certify a continuous angular sector.
 def sector(ri,ro,z,h,a,c):
  import numpy as np
  aa=np.radians(np.linspace(a,c,65));pts=[(ro*math.cos(t),ro*math.sin(t))for t in aa]+[(ri*math.cos(t),ri*math.sin(t))for t in aa[::-1]]
  return b.cq.Workplane('XY').polyline(pts).close().extrude(h).val().translate((0,0,z))
 op=[b.ring(ro,ri,hi-lo,lo)for lo,hi,ri,ro in bands[:9]]
 op.append(b.ring(4.65,3.4,2,20.6))
 for offset in(0,180):
  op.extend([sector(5,12,19,1.6,offset-40,offset+40),sector(3.4,12,20.6,2,offset-46,offset+46),sector(9,12,22.6,.5,offset-36,offset+36)])
 operating=b.uni(*op).translate((-pitch/2,0,116))
 failures=[]
 for gap in(5,10,15,20,25,30,35):
  its,p=b.state(0,override=b.target('envelope',0,116,gap,0,foam='installed'));rot=[q for q in its if q.name.startswith('old_')and rotating(q)]
  for q in rot:
   for v in q.shape.Vertices():maxr=max(maxr,math.hypot(v.X+pitch/2,v.Y))
   a=abs(q.shape.cut(outer).Volume());c=abs(q.shape.cut(sweep).Volume())
   if a>1e-5 or c>1e-5:failures.append(dict(gap=gap,name=q.name,outside_outer_mm3=a,outside_strata_mm3=c))
  fixed=[q for q in its if q.name.startswith('old_')and not rotating(q) and not q.reference and q.group!='holder']
  for q in fixed:
   v=overlap(operating,q.shape)
   if v>.025:failures.append(dict(gap=gap,fixed=q.name,envelope_overlap_mm3=v))
  rows.append(dict(gap=gap,rotating_bodies=len(rot)))
 print('CONTAINMENT',len(failures),'failures, vertex radius',maxr,flush=True)
 # The full outer cylinder checks the head's entire rotating height against shared supports.
 poses=[('state'+str(k),None,k)for k in(0,2,3,5,11,14,16)]
 for i,j in((2,3),(3,4),(4,5),(5,6),(6,7),(12,13)):
  for t in(.25,.5,.75):poses.append((f'{i}->{j}@{t}',interpolate(i,j,t),0))
 shared=[]
 for label,override,k in poses:
  its,p=b.state(k,override=override)
  common=[q for q in its if not q.reference and not q.name.startswith(('old_','new_'))]
  for hx in(-pitch/2,pitch/2):
   env=b.cyl(R,40,(hx,p['tip_y'],p['tip_z']-16))
   for q in common:
    v=overlap(env,q.shape)
    if v>.025:shared.append(dict(pose=label,head_x=hx,part=q.name,overlap_mm3=v))
  print('SHARED_BOUND',label,'contacts',len(shared),flush=True)
 refinement={n:dict(before_mm3=m['before_refinement_volume_mm3'],after_mm3=b.PARTS[n].Volume(),removed_percent=100*(1-b.PARTS[n].Volume()/m['before_refinement_volume_mm3']))for n,m in b.META.items()if'before_refinement_volume_mm3'in m}
 report=dict(pitch_mm=pitch,old_pitch_mm=52,outer_radius_bound_mm=R,vertex_radius_max_mm=maxr,certified_inter_head_gap_mm=pitch-2*R,minimum_pitch_for_2mm_margin_mm=2*R+2,containment_gaps=rows,containment_failures=failures,shared_support_poses=len(poses),shared_support_contacts=shared,strata=bands,refinement=refinement,own_fixed_operating_twist_range_deg=[-30,30],upper_return_sector_half_angles_deg=[40,46,36],scope='Own fixed-part check uses lower full circles and continuous +/-30deg sectors for the added upper return attachments. Upper return attachments are not360deg-capable. Inter-head exterior uses continuous circular bounds for arbitrary twist angles of both heads. Jaw translation is linear, so maximum radial extent lies at opening endpoints; the grip drum stays within radius11. Strata check own fixed parts at7 openings; shared supports at25 poses. This is geometry, not360degree servo/wire capability, strength, friction or cable dynamics.')
 (b.OUT/'validation/rotation_envelope.json').write_text(json.dumps(report,indent=2));print('ENVELOPE_DONE',json.dumps({k:report[k]for k in('pitch_mm','certified_inter_head_gap_mm','containment_failures','shared_support_contacts','refinement')}),flush=True)
 if failures or shared:raise SystemExit(1)
if __name__=='__main__':run()
