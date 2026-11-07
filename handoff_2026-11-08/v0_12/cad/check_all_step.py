import json
from pathlib import Path
import cadquery as cq
root=Path(__file__).resolve().parents[1];rows=[]
for p in sorted((root/'output/step').glob('*.step')):
 if '.healed.' in p.name:continue
 s=cq.importers.importStep(str(p)).val();bb=s.BoundingBox();row=dict(file=p.name,valid=s.isValid(),solids=len(s.Solids()),bbox_mm=[bb.xlen,bb.ylen,bb.zlen]);rows.append(row);print(row,flush=True)
 (root/'output/validation/step_roundtrip.json').write_text(json.dumps(rows,indent=2))
