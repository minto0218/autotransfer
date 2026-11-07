import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];V=R/'output/validation';q=json.loads((V/'release_summary.json').read_text());plates=json.loads((V/'head_plates.json').read_text())['plates'];types={p['part']for a in plates for p in a};pieces=sum(map(len,plates));bb=next(s['bbox_mm']for s in q['step_files']if s['file']=='module_old.step');bbox=' × '.join(f'{v:.1f}'for v in bb)
text=f'''# V0.12｜水平ばね3本と一枚の着脱側板

[3D HTML](output/viewer.html) ／ [ヘッド1個の印刷キット](output/独立ヘッド印刷キット.zip) ／ [組立手順](docs/組立手順.md) ／ [配線と購入品](docs/配線と購入部品.md) ／ [ばねの点検・交換](docs/ばねの点検と交換.md)

V0.11の縦向きばねを、3本とも横向きに変更しました。高さの違いを利用して一枚の共通側板へまとめています。ねじり時にばね板は回りません。引き抜き時にはケースごと移動します。V0.11は保存しています。

## 変更した構造

- 共通側板はケースへM2×2で着脱。ばね固定点を3個載せ、3枚の独立板にはしていません。
- 戻し溝からの糸を、高さの違うR4自由回転案内輪で横のばねへ導きます。主ケーブルの取出口は上向きのまま。
- 案内輪は棚へ横から入れ、最後に一本のM1.6×16共通軸を通します。上下棚の隙間で各輪を位置決めし、締結で輪を挟みません。輪3個を閉じた棚へ上から押し込む組立にはしていません。
- ねじり戻し輪の水平スポークを低くして、逆ねじり端でも戻し糸が上を通るようにしました。ばねを支える不要な縦柱は廃止。
- 公称ヘッド全高は74→66mm。初期姿勢の独立ヘッド外形は約{bbox}mm。中心間52、開口35→5、爪高さ5、押込み20mm、中空2ドラムと7サーボの連動は維持。

## 印刷・組立

印刷用は`output/print/`、CAD原点は`output/stl/`。原点STLには購入ねじの参考形状も入っており、一括印刷用ではありません。独立ヘッド＋治具は{len(types)}種類・{pieces}点、3MFは{len(plates)}枚。3MFは配置モデルで、プリンター設定やG-codeではありません。

最初に嵌合片を印刷し、次にヘッド1個で手動確認します。ケース・カム・戻し輪は開ける分割を維持。上の押込みドラムは別体で、下の押し足が一体でも組めます。共通側板は外面をベッド側にし、後梁の0.5mmの張出しによる薄い支持を確認。棚の隙間、軸穴と糸溝へサポートを埋めないようスライサーで確認してください。薄いスポークは積層0.12mm以下で断面を確認します。

## CAD上の確認

| 確認 | 結果 |
|---|---|
| 代表＋途中・端の剛体姿勢 | {q['rigid_pose_count']}姿勢、重なり検出0 |
| ケース・カム・戻し輪・案内輪・共通軸等の組立途中 | {q['assembly_distance_tests']}組、重なり検出0 |
| ヘッド間の回転外周余裕 | {q['inter_head_rotation_gap_mm']:.1f}mm |
| 局所戻し糸 | 5姿勢×3系統、離脱後の経路に剛体貫通0 |
| 水平ばねの全伸縮占有体積 | 5姿勢×2ヘッド×3本、剛体接触0・最小隙間{min(r['min_rigid_gap_mm']for r in q['horizontal_spring_audit']['rows']):.2f}mm |
| ばね同士 | 公称外周隙間1.0mm |
| 外部配線 | 40候補、剛体隙間最小{q['cable_min_rigid_gap_mm']:.2f}mm・225ペア交差0 |
| 外部配線と水平ばね占有体積 | 隙間最小{q['cable_spring_min_gap_mm']:.2f}mm |
| 印刷STL | {q['stl_part_types']['print']}種類、単一ソリッド・閉メッシュ・A1寸法内 |
| STEP | {len(q['step_files'])}ファイル読み戻し有効 |
| HTML | {q['browser']['states_clicked']}状態、JavaScript／WebGLエラー0 |

通常ねじりは±30°。一周表示はヘッド間外形の比較で、追加戻し輪を360°回す機能ではありません。剛体の姿勢検査と配線の静止候補の検査であり、全行程の連続掃引・同じチューブの連続変形・摩擦や速度・耐久試験の合格を意味しません。結び目とばねフックの実際の向き、ねじ山、工具の全形状、実サーボの適合は現物確認が必要です。

## ばねの寿命と保守

JB-14の3本をそのまま使用。自由長14、公称予伸び2、最大伸びは把持16.19／ねじり6.19／押込み9.54mm。カタログ許容20.4mm以内ですが、寿命回数は未確定です。金属ばねを戻しに使う構成は一般的で、摩耗・疲労・フック・永久伸びを点検し、実際の繰返し試験で交換間隔を決めます。

MG90Dの角度指令だけで張力は読めません。外部フォースゲージ等で同じ二つの伸びにおける力を測り、運転回数と基準との差を記録する保守が可能です。軽微な糸長変化は結び直して調整できますが、張力だけで疲労をすべて検出できるわけではなく、予圧を増やし続けて延命しません。自動計測のセンサー・治具・制御プログラムは未実装です。

## 保存と再生成

`cad/*.py`と`parameters.json`が編集可能なCadQuery原本。`prototype.py`に共通側板・戻し溝・案内輪、`wires.py`に局所糸とばね、`print_pack.py`に印刷方向を保存。主系統の配線は`output/validation/cable_routes.json`、局所線は`output/ワイヤ経路.csv`、検査集約は`output/validation/release_summary.json`。

```sh
/private/tmp/tf-cad-venv/bin/python v0_12/cad/run_release.py export
/private/tmp/tf-cad-venv/bin/python v0_12/cad/run_release.py rigid
/private/tmp/tf-cad-venv/bin/python v0_12/cad/run_release.py motion
/private/tmp/tf-cad-venv/bin/python v0_12/cad/run_release.py cables
/private/tmp/tf-cad-venv/bin/python v0_12/cad/check_local_returns.py
/private/tmp/tf-cad-venv/bin/python v0_12/cad/check_horizontal_springs.py
/private/tmp/tf-cad-venv/bin/python v0_12/cad/check_cable_pairs.py
/private/tmp/tf-cad-venv/bin/python v0_12/cad/check_cable_springs.py
/private/tmp/tf-cad-venv/bin/python v0_12/cad/append_bench.py
/private/tmp/tf-cad-venv/bin/python v0_12/cad/publish_viewer.py
/private/tmp/tf-cad-venv/bin/python v0_12/cad/make_3mf.py
/private/tmp/tf-cad-venv/bin/python v0_12/cad/package_head.py
```

STL／STEPとブラウザーの検査後に`final_report.py`で集約します。実物の組立・モーター駆動・耐久試験は未実施です。
'''
(R/'README.md').write_text(text)
