"""Publish B3 only after geometry, capture, mesh and browser checks pass."""
import json,csv,re,gzip,base64,collections,hashlib,zipfile,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'output';V=O/'validation'
def read(n):return json.loads((V/(n+'.json')).read_text())
def run():
 import documents
 documents.run();q=read('report');f=read('function');spr=read('springs');web=read('browser');parts=read('print_manifest');plates=read('plates');style=read('style');sources=read('source_hashes')
 names=['build.py','head.py','prototype.py','parameters.json','refinements.py'];matches=all(hashlib.sha256((R/'cad'/n).read_bytes()).hexdigest()==sources[n]for n in names)
 raw=re.search("const packed='([^']+)'",(O/'卓上手動治具.html').read_text()).group(1);model=json.loads(gzip.decompress(base64.b64decode(raw)));c=collections.Counter(x['part']for x in model['states'][0]['items'])
 got={'S01':sum(c['fairlead_screw_'+s]for s in'GTP')+c['guide_endcap_M14_screw'],'S02':c['return_spool_M14_screw'],'S03':c['pinion_M14_screw']+c['retainer_M12_screw'],'S04':c['rotor_M12_screw'],'S05':c['spring_hook_screw'],'S06':c['idler_common_axle'],'S07':c['cassette_M2_screw']+c['module_M2_bolt'],'S08':c['case_M2_bolt'],'N01':c['idler_axle_nut'],'N02':c['case_M2_nut']+c['module_M2_nut']}
 expected={x[0]:x[3]for x in documents.HARDWARE if x[0].startswith(('S','N'))}
 counts=collections.Counter(x['part']for pp in plates.values()for x in pp);packing_match=counts==collections.Counter({x['part']:x['quantity']for x in parts})
 passed=q['pass']and f['pass_']and not spr['contacts']and web['states']==10 and not web['page_errors']and web['webgl_error']==0 and matches and got==expected and packing_match and style['pass_']
 with(O/'必要ねじ一覧.csv').open('w',encoding='utf-8-sig',newline='')as fp:
  w=csv.writer(fp);w.writerow(['番号','種類','サイズ','数','頭部寸法等','用途']);w.writerows(x for x in documents.HARDWARE if x[0].startswith(('S','N')))
 table='\n'.join('| '+x[2]+(' ナット'if x[0].startswith('N')else' 小頭'if x[0]in('S01','S02','S03','S04')else' ばね用'if x[0]=='S05'else'')+' | '+str(x[3])+' | '+x[5]+' |'for x in documents.HARDWARE if x[0].startswith(('S','N')))
 summary=dict(version='B3',generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks_pass=passed,geometry_sources_match=matches,hardware_counts_match=got==expected,plate_counts_match=packing_match,print_types=len(parts),print_pieces=sum(x['quantity']for x in parts),screws=sum(v for k,v in got.items()if k.startswith('S')),nuts=sum(v for k,v in got.items()if k.startswith('N')),rigid_poses=q['states'],assembly_tests=q['assembly_paths']['sampled_distance_tests'],pusher_path_samples=f['pusher_samples'],positive_constraint_tests=len(f['positive_constraints']),browser=web,physical_print_tested=False,twist_range_deg=[0,30],twist_sweep_samples=len(f['twist_samples']),twist_spring=f['twist_spring'],style_support_checks=style)
 (V/'release.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 if not passed:raise ValueError('B3 release checks failed '+str(summary))
 # Geometry comparison is advisory: old B1 remains immutable.
 before=R.parent/'bench_manual_v2/output/print';delta=[]
 for x in parts:
  n=x['part']+'.stl';p=O/'print'/n;old=before/n
  status='追加'if not old.exists()else'変更'if p.read_bytes()[80:]!=old.read_bytes()[80:]else'形状同一'
  delta.append([n,x['quantity'],status])
 with(O/'B2からの変更部品.csv').open('w',encoding='utf-8-sig',newline='')as fp:
  w=csv.writer(fp);w.writerow(['STL','B3必要数','B2との比較']);w.writerows(delta)
 (R/'README.md').write_text(f'''# 卓上手動治具 B3｜0°戻り端・片方向ねじり・曲線ブラケット

[軽量3D HTML](output/卓上手動治具.html) ／ [CAD・印刷一式ZIP](output/卓上手動治具_B3_一式.zip) ／ [組立手順](docs/組立と手動確認.md) ／ [購入品と印刷](docs/購入品と印刷.md) ／ [B2からの変更部品](output/B2からの変更部品.csv)

B2を保存した独立改訂版。ねじりを0〜＋30°だけへ変更し、0°を機械的な戻り端にしました。取付側からばね側へのつなぎを曲線リブへ、案内輪の台と側板を丸い輪郭へ整えています。全体装置V0.12は変更していません。

## 0°の決め方

短い動作用ピンを付けたまま、T糸を戻すとTばねがピンを0°のストッパー面へ戻します。T糸の張力を中間角度で釣り合わせて0°を作る必要はありません。＋30°側にも端面があります。印刷誤差とピン穴の遊びは残るので、初回に組立用0°ピンの穴合わせとストッパーを確認します。

Tばねは自由長14mmに対して0°で16mm、＋15°で約17.05mm、＋30°で約18.09mm。**0°でも約2mmの予伸びを残す**設定です。主T糸は端止めを引き離さない位置で、大きなたるみだけを取って結びます。T戻し糸の有効長はB2より約2.09mm長くする目安。初期の巻き残しは105°で継続し、固定座も継続しています。

G糸は開口を維持するよう連動操作します。＋30°ではTを約6.81mm引き、Gを約5.37mm戻す。復帰は逆です。全ての糸を放すだけで全機構が初期位置へ揃う保証ではありません。保管・電源OFFの位置固定には従来の固定ピンを使います。戻り力・摩擦・糸伸びは実物で確かめる対象です。

## 曲線化した部分

- 取付ねじ部は丸い端部へ、斜めの直線梁は滑らかな曲線リブへ変更。
- 一枚側板の肩と先端を丸め、案内輪の上下台は輪の外周をなぞる丸い形へ。
- 取付穴、ばね固定点、案内輪の軸位置は継続。組立後も交換可能。
- 外面をX24.5に揃え、以前の梁の0.5mm張出しを除きました。印刷時は側板外面をベッド側へ。輪の隙間と軸穴へサポートを入れません。

## 継続した機構

開口35→5mm、爪高さ5mm、中空2ドラム、押込み20mm＋棒回転120°、上下に捕捉する爪レール、着脱端止め、カムとケースの合わせキー、棒の上端固定ピンはB2と同じです。押込みドラムは二面幅で棒へ回転を伝え、棒だけが上下に滑ります。摺動の遊びは現物調整が必要です。

## 印刷・購入品

STL **{len(parts)}種類・{sum(x['quantity']for x in parts)}個**。比較用フォロワピン1個を含み、金属Ø1×5.8ピンへ置換する場合はその印刷1個を省略。3MFは嵌合確認片／ヘッド一式／支持台の3枚です。形状と向きの配置データで、プリンター設定や支持設定、G-codeではありません。

精密部品は0.2mmノズル・積層0.06〜0.08mmを推奨。支持台は0.4mm・0.12〜0.16mm可。まず嵌合片をヘッドと同じ条件で印刷し、歯・滑り面・細穴を確認してから1台を組みます。バイアル・Pico・サーボ・長いアウターは今回不要。

必要ねじはB2と同じ**25本、ナット5個**。JB-14×3、PE約Ø0.3を約2m、PTFE1.6/0.8を約100mm、推奨金属横ピンØ1×5.8×1を用意。詳細な頭寸法条件は[購入品CSV](output/購入部品一覧.csv)。

| サイズ | 数 | 用途 |
|---|---:|---|
{table}

## データと検査

`cad/`に自己完結した編集用CadQuery原本、`output/step/`に組立・押込み20mm・分解STEP、`output/print/`に印刷STLと3MF。HTMLは約{web['html_bytes']/1e6:.2f}MBで10姿勢、曲線ブラケット表示と押込み断面を確認できます。ばね・糸はHTML中心線で、STEPに巻線は含めません。ねじ山は参考形状で、印刷穴の仕上げとタップが必要です。

剛体{q['states']}姿勢・組立途中{q['assembly_paths']['sampled_distance_tests']}組で重なり検出0。ねじりは中間角と開口端を含む{len(f['twist_samples'])}姿勢で0。0°より負側へ回そうとすると止まり、＋側へ動けること、＋30°側の止まりも検査。押込みは41位置、拘束確認{len(f['positive_constraints'])}項目を通過。曲線化後も取付・ばね・輪の支持部が残り、一部品でつながることを確認。STLは閉じた単一ソリッド・A1内、STEP3有効、Chrome10姿勢でJS/WebGLエラー0。

実際の印刷・組立・摩擦・ばね力・耐久試験は未実施です。CAD上の離散検査は、実機動作や連続掃引を全面保証するものではありません。

再生成：`python cad/run_complete.py`、`python cad/documents.py`、`python cad/make_plates.py`、`python cad/export_lines.py`。表示と検査の確認後に`python cad/release.py`でZIPを作ります。
''')
 hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(R/'cad').glob('*')if p.is_file()and p.suffix in('.py','.json','.html','.txt')}
 (V/'final_source_hashes.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2))
 dest=O/'卓上手動治具_B3_一式.zip'
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
  for p in R.rglob('*'):
   if p.is_file()and p!=dest and'__pycache__'not in p.parts and p.suffix not in('.pyc','.zip'):z.write(p,Path(R.name)/p.relative_to(R))
 with zipfile.ZipFile(dest)as z:
  if z.testzip():raise ValueError('ZIP invalid')
 print('RELEASE_PASS',passed,dest.stat().st_size,flush=True)
if __name__=='__main__':run()
