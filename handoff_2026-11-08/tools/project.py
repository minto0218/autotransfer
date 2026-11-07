#!/usr/bin/env python3
"""Portable entry points. Saved validation reports are historical, not new passes."""
import argparse, hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def call(design, script, *args):
    folder=ROOT/design
    for n in ('print','step','stl','previews','validation'):
        (folder/'output'/n).mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,str(folder/'cad'/script),*args],cwd=folder,check=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('task',choices=['inspect','verify','smoke','bench','full-export','full-check','part','serve'])
    ap.add_argument('--design',choices=['bench_manual_v3','v0_12'],default='bench_manual_v3')
    ap.add_argument('--name',help='CAD part identifier, for example cable_stop_button')
    ap.add_argument('--port',type=int,default=8000)
    a=ap.parse_args()
    if a.task=='inspect':
        for design in ('bench_manual_v3','v0_12'):
            p=ROOT/design
            print(design, 'sources:',len(list((p/'cad').glob('*.py'))),'STL:',len(list((p/'output/print').glob('*.stl'))))
        print('Current print design: bench_manual_v3 (B3). Full device: v0_12.')
        print('Read HANDOFF.md and SPEC.md before changes. No physical pass is claimed.')
        return
    if a.task=='verify':
        manifest=json.loads((ROOT/'SHA256.json').read_text());bad=[]
        for rel,wanted in manifest.items():
            p=ROOT/rel
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=wanted: bad.append(rel)
        print('Files checked:',len(manifest),'mismatches:',len(bad))
        for p in bad: print(p)
        if bad: raise SystemExit(1)
        return
    if a.task=='serve':
        # Explicit command; public binding is for container port forwarding.
        subprocess.run([sys.executable,'-m','http.server',str(a.port),'--bind','0.0.0.0','--directory',str(ROOT)],check=True)
        return
    if importlib.util.find_spec('cadquery') is None:
        raise SystemExit('CadQuery is missing. Install requirements.txt in a Python 3.11 environment; see SETUP.md.')
    if a.task=='smoke':
        import cadquery as cq
        box=cq.Workplane('XY').box(2,3,4).val()
        if not box.isValid() or abs(box.Volume()-24)>1e-6: raise RuntimeError('CAD kernel smoke failed')
        print('CadQuery',cq.__version__,'basic solid PASS. This does not validate the TF mechanism.')
    elif a.task=='bench':
        # Mark prior aggregate/browser verdicts stale before changing generated geometry.
        val=ROOT/'bench_manual_v3/output/validation'
        for n in ('release.json','browser.json'):
            p=val/n
            if p.exists(): (val/(n+'.historical')).write_bytes(p.read_bytes());p.unlink()
        call('bench_manual_v3','run_complete.py')
        for script in ('documents.py','make_plates.py','export_lines.py'): call('bench_manual_v3',script)
        print('B3 generated and geometry checks ran. Browser QA and physical assembly remain separate.')
    elif a.task=='full-export':
        call('v0_12','run_release.py','export')
        for script in ('append_bench.py','publish_viewer.py','make_3mf.py'): call('v0_12',script)
        print('Full device exported. Saved reports are not a new validation pass; run full-check.')
    elif a.task=='full-check':
        for mode in ('rigid','motion','cables'):call('v0_12','run_release.py',mode)
        for script in ('check_local_returns.py','check_horizontal_springs.py','check_cable_pairs.py','check_cable_springs.py'):call('v0_12',script)
        print('Listed CAD checks ran; no fresh browser/physical pass is implied.')
    elif a.task=='part':
        if not a.name:ap.error('--name is required for part')
        # A fresh process keeps identical module names from different designs isolated.
        code='''import sys\nfrom pathlib import Path\nimport build as b\nb.make_parts()\nn=sys.argv[1]\nif n not in b.PARTS: raise SystemExit('Unknown part: '+n+'; available: '+', '.join(sorted(b.PARTS)))\nout=b.ROOT/'output'/'edited_parts';out.mkdir(parents=True,exist_ok=True)\ns=b.PARTS[n]\nb.exporters.export(s,str(out/(n+'.step')))\nb.exporters.export(s,str(out/(n+'.stl')),tolerance=.025,angularTolerance=.1)\nprint(out/n)\nprint('CAD orientation, not guaranteed print orientation. Assembly outputs are unchanged.')\n'''
        subprocess.run([sys.executable,'-c',code,a.name],cwd=ROOT/a.design/'cad',check=True)
if __name__=='__main__':main()
