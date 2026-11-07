"""Manual bench discrete geometry and deliverable checks; not physical qualification."""
import json,math,hashlib,struct,collections
import numpy as np
import build as b

def overlap(a,c):
 x=a.BoundingBox();y=c.BoundingBox()
 if any(min(getattr(x,k+'max'),getattr(y,k+'max'))-max(getattr(x,k+'min'),getattr(y,k+'min'))<.0005 for k in'xyz'):return 0.
 return abs(a.intersect(c).Volume())

def mesh_report(p):
 data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0];edges=collections.Counter()
 for i in range(n):
  a=struct.unpack_from('<12fH',data,84+50*i);v=[tuple(round(x,5)for x in a[j:j+3])for j in(3,6,9)]
  for j in range(3):edges[tuple(sorted((v[j],v[(j+1)%3])))]+=1
 return dict(triangles=n,closed=all(v==2 for v in edges.values()),length_valid=len(data)==84+50*n)

def run():
 b.make_parts();hits=[];cache={};wire=[]
 for k in list(range(8))+[9]:
  items,p=b.state(k)
  for i,q in enumerate(items):
   for r in items[i+1:]:
    A=getattr(q.shape,'_mesh_pose');B=getattr(r.shape,'_mesh_pose');key=(q.part,r.part,tuple(np.round(np.linalg.inv(A)@B,6).ravel()))
    if key not in cache:cache[key]=overlap(q.shape,r.shape)
    if cache[key]>.025:hits.append(dict(state=k,a=q.name,b=r.name,overlap_mm3=cache[key]))
  import wire_paths
  for tag,(x,y,z)in wire_paths.PORTS.items():
   i=('G','T','P').index(tag);edge=b.cq.Edge.makeLine(b.cq.Vector(x,y,82.5),b.cq.Vector(x,y,42+z+p['pull_mm'][i]+4));best=10;near=None
   for q in items:
    bb=q.shape.BoundingBox()
    if x<bb.xmin-best or x>bb.xmax+best or y<bb.ymin-best or y>bb.ymax+best:continue
    d=q.shape.distance(edge)
    if d<best:best=d;near=q.name
   wire.append(dict(state=k,tag=tag,clearance_mm=best-.15,nearest=near))
  print('POSE',k,'contacts',len(hits),flush=True)
 import check_assembly
 check_assembly.run()
 steps=[]
 for path in sorted((b.OUT/'step').glob('*.step')):
  s=b.cq.importers.importStep(str(path)).val();bb=s.BoundingBox();steps.append(dict(file=path.name,valid=s.isValid(),solids=len(s.Solids()),bbox_mm=[bb.xlen,bb.ylen,bb.zlen]))
 stl={p.name:mesh_report(p)for p in sorted((b.OUT/'print').glob('*.stl'))}
 manifests=json.loads((b.OUT/'validation/print_manifest.json').read_text());paths=json.loads((b.OUT/'validation/assembly_paths.json').read_text())
 report=dict(states=9,rigid_contacts=hits,straight_hand_line_checks=wire,straight_hand_line_contacts=[q for q in wire if q['clearance_mm']<-.01],steps=steps,stl=stl,print_types=len(manifests),print_pieces=sum(q['quantity']for q in manifests),all_single_solid=all(q['solids']==1 for q in manifests),all_A1_fit=all(q['fits_A1']for q in manifests),assembly_paths=paths,scope=__doc__,limitations=['Discrete poses, not continuous sweep','Wrapped main and return lines, knots, spring force/friction, exact hook clocking and tool/hand access not certified','No physical print, assembly or motor test'])
 report['pass']=not hits and not report['straight_hand_line_contacts']and not paths['contacts']and all(q['valid']for q in steps)and all(q['closed']and q['length_valid']for q in stl.values())and report['all_single_solid']and report['all_A1_fit']
 (b.OUT/'validation/report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('VALIDATION_PASS',report['pass'],'assembly tests',paths['sampled_distance_tests'],flush=True)
 if not report['pass']:raise SystemExit(1)
if __name__=='__main__':run()
