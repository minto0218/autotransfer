import json,csv
import build as b
import wires

def run():
 b.make_parts();wires.routes.cache_clear();original=b.tube_mesh;rows=[]
 for k in(0,2,11):
  st=b.state(k)[1]
  def capture(name,pts,r,color,group='cable'):
   rows.append(dict(state=k,name=name,radius_mm=r,color=color,group=group,points_mm=[list(p)for p in pts]));return{}
  b.tube_mesh=capture;wires.local_meshes(b,st)
 b.tube_mesh=original
 (b.OUT/'validation/wire_centerlines.json').write_text(json.dumps(rows,indent=2))
 with(b.OUT/'ワイヤ経路.csv').open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.writer(f);w.writerow(['state','name','point','X_mm','Y_mm','Z_mm'])
  for q in rows:
   if q['group']=='spring_actual':continue
   for i,p in enumerate(q['points_mm']):w.writerow([q['state'],q['name'],i,*p])
 print('WIRE_CENTERLINES',len(rows),flush=True)
if __name__=='__main__':run()
