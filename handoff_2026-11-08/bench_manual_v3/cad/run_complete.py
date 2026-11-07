"""One CAD construction for export and checks, ensuring the manifests are current."""
import runpy
import bench,build as b,validate
bench.generate()
validate.run()
runpy.run_path(str(b.ROOT/'cad/check_function.py'),run_name='__main__')
runpy.run_path(str(b.ROOT/'cad/check_springs.py'),run_name='__main__')
runpy.run_path(str(b.ROOT/'cad/check_style.py'),run_name='__main__')
print('CAD_CHECKS_COMPLETE',flush=True)
