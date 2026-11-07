"""Plain 3MF model plates, not G-code or a printer configuration."""
import csv,json,struct,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'output/print';NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
def mesh(path):
 data=path.read_bytes();N=struct.unpack_from('<I',data,80)[0];verts=[];faces=[];lookup={}
 for i in range(N):
  rec=struct.unpack_from('<12fH',data,84+50*i);tri=[]
  for j in(3,6,9):
   p=tuple(round(v,5)for v in rec[j:j+3])
   if p not in lookup:lookup[p]=len(verts);verts.append(p)
   tri.append(lookup[p])
  faces.append(tri)
 return verts,faces

def run():
 for stale in D.glob('head_plate_*.3mf'):stale.unlink()
 rows=json.loads((ROOT/'output/validation/print_pack.json').read_text())['parts'];pieces=[]
 for q in rows:
  count=q['one_head_quantity']
  if q['part']in('bench_head_stand','bench_anchor_back','bench_anchor_front','fit_coupon','fit_coupon_pin'):count=1
  if q['part']in('manual_pull_tab','upper_PTFE_adapter'):count=3
  for i in range(count):pieces.append((q['part'],i,q['bed_bbox_mm']))
 pieces.sort(key=lambda p:p[2][1],reverse=True);plates=[];placed=[];x=y=5;rowh=0
 for name,i,bb in pieces:
  w,h,_=bb
  if x+w>251:x=5;y+=rowh+4;rowh=0
  if y+h>251:plates.append(placed);placed=[];x=y=5;rowh=0
  placed.append((name,i,x,y));x+=w+4;rowh=max(rowh,h)
 if placed:plates.append(placed)
 for k,plate in enumerate(plates,1):
  model=ET.Element('model',{'unit':'millimeter','xml:lang':'en-US','xmlns':NS});resources=ET.SubElement(model,'resources');build=ET.SubElement(model,'build')
  for objid,(name,i,x,y)in enumerate(plate,1):
   vs,fs=mesh(D/(name+'.stl'));mn=[min(p[a]for p in vs)for a in range(3)]
   ob=ET.SubElement(resources,'object',id=str(objid),type='model',name=f'{name}_{i+1}');me=ET.SubElement(ob,'mesh');ve=ET.SubElement(me,'vertices');tr=ET.SubElement(me,'triangles')
   for p in vs:ET.SubElement(ve,'vertex',x=str(p[0]-mn[0]+x),y=str(p[1]-mn[1]+y),z=str(p[2]-mn[2]))
   for a,b,c in fs:ET.SubElement(tr,'triangle',v1=str(a),v2=str(b),v3=str(c))
   ET.SubElement(build,'item',objectid=str(objid))
  modelbytes=ET.tostring(model,encoding='utf-8',xml_declaration=True)
  dest=D/f'head_plate_{k:02}.3mf'
  with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
   z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
   z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
   z.writestr('3D/3dmodel.model',modelbytes)
  with zipfile.ZipFile(dest)as z:ET.fromstring(z.read('3D/3dmodel.model'))
 print('3MF_PLATES',len(plates),'parts',len(pieces),flush=True)
 (ROOT/'output/validation/head_plates.json').write_text(json.dumps(dict(plates=[[dict(part=n,copy=i+1,x=x,y=y)for n,i,x,y in p]for p in plates],scope='Plain 3MF model layout only; select A1 nozzle/layer/support settings in slicer. No G-code.'),indent=2))
if __name__=='__main__':run()
