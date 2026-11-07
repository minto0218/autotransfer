import csv,json,math
from pathlib import Path
import wire_paths
R=Path(__file__).resolve().parents[1];O=R/'output';poses=json.loads((O/'validation/poses.json').read_text());rows=[];lengths=[]
for k,p in enumerate(poses):
 if p.get('explode'):continue
 for r in wire_paths.lines(p):
  if r['kind']=='spring':continue
  pts=r['points'];length=sum(math.dist(a,c)for a,c in zip(pts,pts[1:]));lengths.append(dict(state=k,name=r['name'],centerline_length_mm=length))
  for i,pt in enumerate(pts):rows.append([k,p['label'],r['name'],i,*pt])
with(O/'糸の経路.csv').open('w',encoding='utf-8-sig',newline='')as f:
 w=csv.writer(f);w.writerow(['姿勢','動作','糸','点番号','X_mm','Y_mm','Z_mm']);w.writerows(rows)
(O/'validation/line_lengths.json').write_text(json.dumps(dict(scope='Polyline length including the shown winding reserve and tab end. Not a cutting length; add knot and fitting allowance.',rows=lengths),ensure_ascii=False,indent=2));print('LINE_POINTS',len(rows),flush=True)
