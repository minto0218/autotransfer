import json
import numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[1]
from cable_math import segdist
params=json.loads((root/'cad/parameters.json').read_text())
cd=params['joint_module']*(params['root_pin_teeth']+params['root_wheel_teeth'])/2+.12
normal=[]
for j in range(2):
 x=params['root_capstan_x']+2+2*j;y=params['root_y']+cd+(-params['joint_input_r']if j==0 else params['joint_input_r'])
 normal.append(dict(name='M4_normal_'+str(j),points=[[x,y,params['root_z']],[x,y,params['deck_z']+25]],radius=params['wire_d']/2))
routes=json.loads((root/'output/validation/cable_routes.json').read_text());rows=[]
for pose,rr in routes.items():
 allrows=[dict(q,radius=params['housing_od']/2)for q in rr]+normal
 for i,a in enumerate(allrows):
  for c in allrows[i+1:]:rows.append(dict(pose=pose,a=a['name'],b=c['name'],surface_clearance_mm=segdist(a['points'],c['points'])-a['radius']-c['radius']))
rep=dict(scope='Exact straight-segment pair distances for5 static candidate sets, housing OD1.6 plus two normal M4 wires0.3; no continuous deformation proof.',pairs=len(rows),minimum_surface_clearance_mm=min(q['surface_clearance_mm']for q in rows),intersections=[q for q in rows if q['surface_clearance_mm']<0],results=rows)
(root/'output/validation/cable_pair_audit.json').write_text(json.dumps(rep,indent=2));print({k:v for k,v in rep.items()if k!='results'})

for pose,rr in routes.items():
 for cable in rr:
  cable['cable_pair_clearance_mm']=min(q['surface_clearance_mm']for q in rows if q['pose']==pose and cable['name']in(q['a'],q['b']))
(root/'output/validation/cable_routes.json').write_text(json.dumps(routes,indent=2))
