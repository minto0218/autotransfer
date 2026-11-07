import json
from pathlib import Path
from check_deliverables import mesh_report
root=Path(__file__).resolve().parents[1];report={}
for folder in('stl','print'):
 rows={p.name:mesh_report(p)for p in sorted((root/'output'/folder).glob('*.stl'))};report[folder]=rows
 print(folder,len(rows),'failed',[n for n,q in rows.items()if q['non_two_incident_edges']or not q['binary_length_matches']],flush=True)
(root/'output/validation/stl_final.json').write_text(json.dumps(report,indent=2))
