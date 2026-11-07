import json,csv,io,zipfile
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'output';manifest=json.loads((O/'validation/head_plates.json').read_text());qty=Counter(q['part']for plate in manifest['plates']for q in plate);rows={q['part']:q for q in json.loads((O/'validation/print_pack.json').read_text())['parts']};s=io.StringIO();w=csv.writer(s);w.writerow(['部品','ヘッド1個＋治具の印刷個数','印刷方向など'])
for n,count in sorted(qty.items()):w.writerow([n,count,rows[n]['notes']])
dest=O/'独立ヘッド印刷キット.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for n in qty:z.write(O/'print'/(n+'.stl'),'parts/'+n+'.stl')
 for p in(O/'print').glob('head_plate_*.3mf'):z.write(p,p.name)
 z.writestr('ヘッド1個と治具の印刷個数.csv','\ufeff'+s.getvalue())
 for n in('組立手順.md','配線と購入部品.md','ばねの点検と交換.md'):z.write(R/'docs'/n,n)
 z.write(O/'hardware.csv','購入部品.csv');z.write(O/'step/bench_head.step','bench_head.step')
 z.writestr('最初に読む.txt','V0.12 独立ヘッドの組立・手動試験用です。\n最初はparts/fit_coupon.stlとfit_coupon_pin.stlのみ印刷し、嵌合を確認してください。\n3MFはモデル配置データです。A1・ノズル・積層・サポート設定はスライサーで選びます。G-codeではありません。\nばね・PE糸・PTFE・ねじ・金属横ピンは購入品です。ねじ山はSTLへ彫っておらず、下穴のタップと通し穴をさらう仕上げが必要です。\n組立手順と購入品の頭径条件を確認してください。実物の組立・動作試験は未実施です。\n')
print('HEAD_KIT',dest,len(qty),'part types',sum(qty.values()),'pieces',dest.stat().st_size,flush=True)
