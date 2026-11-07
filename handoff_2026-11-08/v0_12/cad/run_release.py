import sys,json,hashlib,datetime
from pathlib import Path
import build as b
mode=sys.argv[1]
CORE=['build.py','head.py','prototype.py','retention.py','mechanism.py','drive.py','mesh_cache.py','parameters.json']
sources={n:hashlib.sha256((b.ROOT/'cad'/n).read_bytes()).hexdigest()for n in CORE}
if mode=='export':
 b.publish()
 import print_pack,export_wire_paths
 print_pack.run();export_wire_paths.run()
 (b.OUT/'validation/export_sources.json').write_text(json.dumps(sources,indent=2))
elif mode=='rigid':
 import validate,check_assembly,control_model
 validate.run();check_assembly.run();control_model.run()
elif mode=='motion':
 import validate_motion,check_rotation_envelope
 validate_motion.run();check_rotation_envelope.run()
elif mode=='cables':
 import validate_cables
 validate_cables.run()
print('RELEASE_JOB_DONE',mode,flush=True)
