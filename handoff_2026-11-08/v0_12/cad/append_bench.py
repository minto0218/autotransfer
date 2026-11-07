import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];p=root/'output/validation/states.json';states=json.loads(p.read_text());bench=json.loads((root/'output/validation/bench_pose.json').read_text())
if len(states)==28:states.append(bench)
else:states[28]=bench
p.write_text(json.dumps(states,ensure_ascii=False,indent=2));print('BENCH_APPENDED',len(states))
