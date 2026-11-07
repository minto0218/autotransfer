import json,struct,collections,math
import cadquery as cq
import build as b

def mesh_report(path):
 data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0];edges=collections.Counter();volume=0
 for i in range(n):
  a=struct.unpack_from('<12fH',data,84+50*i);v=[tuple(round(x,5) for x in a[j:j+3]) for j in(3,6,9)]
  for j in range(3):edges[tuple(sorted((v[j],v[(j+1)%3])))]+=1
 return dict(triangles=n,binary_length_matches=len(data)==84+50*n,non_two_incident_edges=sum(c!=2 for c in edges.values()))
def run():
 result={'stl':{p.stem:mesh_report(p) for p in sorted((b.OUT/'stl').glob('*.stl'))},'step':{}}
 for name in('assembly_0.step','module_old.step'):
  sh=cq.importers.importStep(str(b.OUT/'step'/name)).val();bb=sh.BoundingBox();result['step'][name]=dict(valid=sh.isValid(),solids=len(sh.Solids()),bbox_mm=[bb.xlen,bb.ylen,bb.zlen])
  print('STEP_READBACK',name,result['step'][name],flush=True)
 b.make_parts();grav=[]
 for k in(0,3,5,7):
  orig=b.STATES[k];a,c=orig['a'],orig['c'];eps=math.degrees(1e-4)
  def calc(aa,cc):
   p=b.target('gravity',0,0,25,30,angles=(aa,cc));its,_=b.state(0,override=p)
   return {q.name:(q.shape.Volume(),q.shape.Center().z) for q in its if not q.reference}
  minusA=calc(a-eps,c);plusA=calc(a+eps,c);minusC=calc(a,c-eps);plusC=calc(a,c+eps)
  tauA=sum(v*(plusA[n][1]-z)/(2e-4) for n,(v,z) in minusA.items());tauC=sum(v*(plusC[n][1]-z)/(2e-4) for n,(v,z) in minusC.items())
  moving=sum(v for n,(v,z) in minusA.items() if abs(plusA[n][1]-z)>1e-6 or abs(plusC[n][1]-minusC[n][1])>1e-6)
  row=dict(state=k,moving_solid_volume_mm3=moving)
  for label,rho in(('aluminium',2.7e-6),('steel',7.85e-6)):
   row[label]=dict(moving_mass_g=moving*rho*1000,required_motor_M4_Nmm=abs(tauA*rho*9.80665)/b.P['joint_ratio']*2,required_motor_M5_Nmm=abs(tauC*rho*9.80665)/b.P['joint_ratio']*2)
  grav.append(row);print('GRAVITY',row,flush=True)
 result['gravity']=dict(scope='Uniform solid metal volume estimates; no cavities/material substitutions, wire forces, springs, acceleration or losses. Not servo qualification.',samples=grav)
 (b.OUT/'validation/deliverables.json').write_text(json.dumps(result,indent=2));print('DELIVERABLES_DONE',flush=True)
if __name__=='__main__':run()
