"""Repack cached CAD meshes with current cable candidates without rebuilding STEP/STL."""
import json,gzip,base64
import build as b
import wires

def run():
 b.P['gear_cd']=b.P['joint_module']*(b.P['root_pin_teeth']+b.P['root_wheel_teeth'])/2+.12
 states=json.loads((b.OUT/'validation/states.json').read_text());tpl=(b.ROOT/'cad/viewer_template.html').read_text();data=[]
 for k,p in enumerate(states):
  mm=json.loads((b.OUT/'previews'/f'state_{k}.json').read_text());mm=[m for m in mm if m['group'] not in('cable','wire','spring','route_candidate','pitch_envelope','spring_actual')]
  if p.get('envelope_only'):mm.extend(wires.envelope_meshes(b,p))
  if p.get('bench_only'):mm.extend(m for m in wires.local_meshes(b,p)if m['name'].startswith('old_'))
  elif not p['explanatory']:mm.extend(wires.local_meshes(b,p))
  data.append(mm)
 packed=base64.b64encode(gzip.compress(json.dumps(data,separators=(',',':')).encode(),5)).decode()
 html=tpl.replace('__PAYLOAD__',packed).replace('__NAMES__',json.dumps([q['label'] for q in states],ensure_ascii=False)).replace('__POSES__',json.dumps(states,ensure_ascii=False))
 for name in('viewer.html','progress_now.html'):(b.OUT/name).write_text(html)
 print('VIEWER_REPACKED',len(states),flush=True)
if __name__=='__main__':run()
