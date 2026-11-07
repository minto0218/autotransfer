"""Three small plain-model 3MF plates. No slicer config or G-code."""
import json,struct,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
R=Path(__file__).resolve().parents[1];O=R/'output';D=O/'print'

def mesh(path):
 d=path.read_bytes();n=struct.unpack_from('<I',d,80)[0];vs=[];fs=[];lookup={}
 for i in range(n):
  q=struct.unpack_from('<12fH',d,84+50*i);f=[]
  for j in(3,6,9):
   p=tuple(round(v,5)for v in q[j:j+3])
   if p not in lookup:lookup[p]=len(vs);vs.append(p)
   f.append(lookup[p])
  fs.append(f)
 return vs,fs

def run():
 rows=json.loads((O/'validation/print_manifest.json').read_text());sets={
 '00_嵌合確認_ヘッドと同じノズル':[], '01_ヘッド一式_0.2mm推奨':[], '02_卓上支持台_0.4mm可':[]}
 for q in rows:
  key=next(iter(sets))if q['part'].startswith('fit_coupon')else'02_卓上支持台_0.4mm可'if q['part']=='bench_head_stand'else'01_ヘッド一式_0.2mm推奨'
  for i in range(q['quantity']):sets[key].append((q,i))
 manifest={}
 for name,rows in sets.items():
  rows.sort(key=lambda q:q[0]['bbox_mm'][1],reverse=True);x=y=5;h=0;placed=[]
  for q,i in rows:
   w,hh,z=q['bbox_mm']
   if x+w>250:x=5;y+=h+4;h=0
   if y+hh>250:raise ValueError('Plate too large')
   placed.append(dict(part=q['part'],copy=i+1,x=x,y=y));x+=w+4;h=max(h,hh)
  NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';root=E.Element('model',{'unit':'millimeter','xml:lang':'en-US','xmlns':NS});resources=E.SubElement(root,'resources');build=E.SubElement(root,'build')
  for j,q in enumerate(placed,1):
   vs,fs=mesh(D/(q['part']+'.stl'));mn=[min(p[a]for p in vs)for a in range(3)];ob=E.SubElement(resources,'object',id=str(j),type='model',name=q['part']+'_'+str(q['copy']));me=E.SubElement(ob,'mesh');ve=E.SubElement(me,'vertices');fa=E.SubElement(me,'triangles')
   for p in vs:E.SubElement(ve,'vertex',x=str(p[0]-mn[0]+q['x']),y=str(p[1]-mn[1]+q['y']),z=str(p[2]-mn[2]))
   for a,b,c in fs:E.SubElement(fa,'triangle',v1=str(a),v2=str(b),v3=str(c))
   E.SubElement(build,'item',objectid=str(j))
  with zipfile.ZipFile(D/(name+'.3mf'),'w',zipfile.ZIP_DEFLATED)as z:
   z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
   z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
   z.writestr('3D/3dmodel.model',E.tostring(root,encoding='utf-8',xml_declaration=True))
  with zipfile.ZipFile(D/(name+'.3mf'))as z:E.fromstring(z.read('3D/3dmodel.model'))
  manifest[name]=placed
 (O/'validation/plates.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('PLATES',[(k,len(v))for k,v in manifest.items()],flush=True)
if __name__=='__main__':run()
