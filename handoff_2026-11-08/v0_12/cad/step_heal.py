"""Read-back QA and conservative OpenCASCADE healing of transferred STEP shells.
The source solids remain authoritative; this does not validate fits or strength.
"""
import json
from pathlib import Path
import cadquery as cq
root=Path(__file__).resolve().parents[1];report=[]
for p in sorted((root/'output/step').glob('*.step')):
 sh=cq.importers.importStep(str(p)).val();bad=[s for s in sh.Solids() if not s.isValid()]
 row=dict(file=p.name,original_readback_valid=sh.isValid(),invalid_solids=len(bad),original_volume=sh.Volume())
 if bad:
  ss=[s.fix() if not s.isValid() else s for s in sh.Solids()];fixed=cq.Compound.makeCompound(ss)
  row['heal_valid']=fixed.isValid();row['volume_change_mm3']=fixed.Volume()-sh.Volume()
  if fixed.isValid() and abs(row['volume_change_mm3'])<.05:
   tmp=p.with_suffix('.healed.step');cq.exporters.export(fixed,str(tmp));test=cq.importers.importStep(str(tmp)).val();row['second_readback_valid']=test.isValid()
   if test.isValid():tmp.replace(p);row['flat_geometry_after_heal']=True
   else:tmp.unlink()
 row['final_readback_valid']=cq.importers.importStep(str(p)).val().isValid();report.append(row);print('STEP_QA',row,flush=True)
 (root/'output/validation/step_roundtrip.json').write_text(json.dumps(report,indent=2))
