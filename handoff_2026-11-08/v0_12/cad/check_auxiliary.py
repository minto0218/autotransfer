"""Run local return, horizontal spring and external housing checks on one CAD build."""
import runpy,json,hashlib
import build as b
import check_local_returns,validate_cables
b.make_parts();check_local_returns.run()
runpy.run_path(str(b.ROOT/'cad/check_horizontal_springs.py'),run_name='__main__')
validate_cables.run()
runpy.run_path(str(b.ROOT/'cad/check_cable_springs.py'),run_name='__main__')
names=['build.py','head.py','prototype.py','retention.py','mechanism.py','drive.py','mesh_cache.py','parameters.json']
(b.OUT/'validation/aux_sources.json').write_text(json.dumps({n:hashlib.sha256((b.ROOT/'cad'/n).read_bytes()).hexdigest()for n in names},indent=2))
print('AUXILIARY_DONE',flush=True)
