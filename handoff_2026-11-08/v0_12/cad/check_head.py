import json
import build as b
from validate import overlap

def run():
 b.make_parts();rows=[];parts=[]
 for n,s in b.PARTS.items():
  if len(s.Solids())!=1:print('MULTI',n,len(s.Solids()),flush=True)
 for k in(0,2,11,14,16):
  its,st=b.state(k);head=[q for q in its if q.name.startswith('old_')and not q.reference and q.group!='holder'];others=[q for q in its if not q.name.startswith(('old_','new_'))and not q.reference]
  for i,q in enumerate(head):
   for r in head[i+1:]+others:
    v=overlap(q.shape,r.shape)
    if v>.025:
     row=dict(state=k,a=q.name,b=r.name,volume=round(v,5));rows.append(row);print('HIT',row,flush=True)
  print('HEAD_CHECKED',k,'hits',len(rows),flush=True)
 (b.OUT/'validation/head_audit.json').write_text(json.dumps(dict(poses=5,contacts=rows),indent=2));print('HEAD_DONE',len(rows),flush=True)
if __name__=='__main__':run()
