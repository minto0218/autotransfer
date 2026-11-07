"""Write the bench-specific purchasing and assembly documents."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'output'
HARDWARE=[
 ('S01','小頭ねじ','M1.4×4',7,'0番1種なべ頭、公称頭径2.0mm（実測2.05以下）','主糸案内の蓋3個＋レール端止め4本'),
 ('S02','小頭ねじ','M1.4×5',2,'0番1種なべ頭、公称頭径2.0mm（実測2.05以下）','半割ねじり戻し輪2個'),
 ('S03','小頭ねじ','M1.4×6',4,'0番1種なべ頭、公称頭径2.0mm（実測2.05以下）','ピニオン2本＋後側コーム2本'),
 ('S04','小頭ねじ','M1.4×8',2,'0番1種なべ頭、公称頭径2.0mm（実測2.05以下）','上ドラムとガイド籠'),
 ('S05','ばねフック用ねじ','M1.4×8',3,'頭径2.4以上。公称2.5mmの0番2種なべ頭を想定','水平ばねの固定フック3本'),
 ('S06','共通案内軸ねじ','M1.6×16',1,'頭径3.2以下・頭高さ1.3以下。首下長16mm','案内輪3個を通す。下から挿入'),
 ('N01','ナット','M1.6',1,'対辺3.2以下・厚さ1.3以下','共通案内軸の上端'),
 ('S07','ねじ','M2×8',4,'なべ頭・頭径3.6以下','ばね側板2本＋支持台への固定2本'),
 ('S08','ねじ','M2×16',2,'なべ頭・頭径3.6以下','左右ケースの横締め'),
 ('N02','ナット','M2',4,'対辺4.0以下・厚さ1.6以下','ケース2個＋支持台2個'),
 ('B01','引張ばね','東京発条 JB-14',3,'外径2.5・自由長14・線径0.23・k0.05N/mm','把持・ねじり・押込みの戻し'),
 ('L01','PE編み釣り糸','実測径約0.3mm',1,'主糸3本＋戻し3本。仮組み用に計2m程度を用意','仮切断の目安：主糸各250mm、戻し各150mm。結んでから余りを切る'),
 ('L02','PTFEチューブ','外径1.59〜1.6／内径0.8mm',1,'100mm程度を用意。曲線ライナー約12.6mm×3本を現物合わせ','主糸の90°案内内のみ。外部の長いチューブなし'),
 ('P01','推奨置換用の金属丸ピン','Ø1.0×5.8mm',1,'印刷比較用STLも同梱。主構成では金属ピン推奨','押し棒の横フォロワ。棒中央だけに少量接着'),
]

def run():
 with(O/'購入部品一覧.csv').open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.writer(f);w.writerow(['番号','種類','サイズ・型式','必要数','頭部・寸法条件／用意する量','使用箇所']);w.writerows(HARDWARE)
 rows=json.loads((O/'validation/print_manifest.json').read_text())
 for q in rows:
  if q['part']in('module_case_R','twist_guide_cage','jaw_guide_endcap','case_alignment_key','push_cam_alignment_key','press_home_lock_pin'):q['nozzle_mm']='0.2推奨';q['layer_mm']='0.06〜0.08'
  if q['part']=='pusher_follower_pin':q['notes']='比較用。金属Ø1×5.8に置換する場合は印刷不要'
 (O/'validation/print_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 with(O/'印刷部品一覧.csv').open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.writer(f);w.writerow(['STL名','部品名','印刷個数','推奨ノズル','積層mm','外形mm','印刷方向・仕上げ'])
  for q in rows:w.writerow([q['part']+'.stl',q['name'],q['quantity'],q['nozzle_mm'],q['layer_mm'],q['bbox_mm'],q['notes']])
 print('DOCS_CSV_DONE',len(rows),'types; screws25 nuts5',flush=True)
if __name__=='__main__':run()
