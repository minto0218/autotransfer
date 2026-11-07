"""Kinematic commands only. No serial port, PWM or firmware output."""
import json,csv,math
import numpy as np
import build as b
import drive
CYCLE=[0,1,2,3,4,5,6,7,8,9,11,12,13]
def interpolate(k,j,t):
 A=b.STATES[k];B=b.STATES[j]
 v=lambda key:A[key]*(1-t)+B[key]*t
 p=b.target(f'{k}->{j} t={t:.3f}',v('tip_y'),v('tip_z'),v('gap'),v('twist'),v('push_old'),v('push_new'),foam='installed')
 return p
def run():
 b.make_parts();rows=[];factor=0.;last=None
 for k,j in zip(CYCLE,CYCLE[1:]):
  for n in range(21):
   p=interpolate(k,j,n/20);rel,cmd=drive.commands(b,p)
   if last is not None:factor+=max(abs(a-c) for a,c in zip(cmd,last))/60
   last=cmd;rows.append(dict(from_state=k,to_state=j,t=n/20,tip_y=p['tip_y'],tip_z=p['tip_z'],a=p['a'],c=p['c'],gap=p['gap'],twist=p['twist'],push_old=p['push_old'],push_new=p['push_new'],commands=cmd))
 arr=np.array([q['commands'] for q in rows]);mx=arr.max(0).tolist();mn=arr.min(0).tolist()
 # Two jaws each contribute F*r to the pinion. T is in N mm.
 coeff=dict(jaw_force_each_per_motor_Nmm=(10.25/24)/(2*6),pusher_force_per_motor_Nmm=(7.3/13)/(20/math.radians(120)),joint_output_torque_per_motor_torque=(38/18)/2)
 (_,st)=b.state(7);coeff['undocked_total_vertical_force_per_motor_Nmm_M4']=coeff['joint_output_torque_per_motor_torque']/(b.P['link1']*abs(math.cos(math.radians(st['a']))));coeff['undocked_total_vertical_force_per_motor_Nmm_M5']=coeff['joint_output_torque_per_motor_torque']/(b.P['link2']*abs(math.cos(math.radians(st['c']))))
 report=dict(scope='Ideal rigid displacement, no force/speed guarantee; offsets are nominal, no firmware output.',cycle=CYCLE,samples=len(rows),motor_min_degrees=mn,motor_max_degrees=mx,within_assumed_90=all(a>=0 and c<=90 for a,c in zip(mn,mx)),ideal_cycle_time_as_multiple_of_measured_seconds_per_60deg=factor,ideal_lossless_coefficients=coeff,staging=dict(head_z=135,foot_start_z=127,foot_end_z=107,stroke=20,jaws_initial=[100,105],foam_closed_top=107,stop_clearance=.2))
 (b.OUT/'validation/control_model.json').write_text(json.dumps(report,indent=2))
 with (b.OUT/'control_trajectory.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.writer(f);w.writerow(['from','to','t','head_y','head_z','a_abs','c_abs','gap','twist','push_old','push_new']+['M'+str(i) for i in range(1,8)])
  for q in rows:w.writerow([q[n] for n in('from_state','to_state','t','tip_y','tip_z','a','c','gap','twist','push_old','push_new')]+q['commands'])
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
