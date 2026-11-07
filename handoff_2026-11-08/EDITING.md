# 自分で部品を修正する方法

## おすすめの選び方

- **今の設計を寸法連動のまま直す：CadQuery＋Python。** 無料のコードエディター（VS Code等）で寸法JSON／Pythonを編集し、生成コマンドを実行する。クラウドならPCにCADソフトをインストールせず作業できる。
- **画面で穴を追加・角を削る：FreeCAD＋STEP。** FreeCADをPCへインストールする。STEPから始めると固体を扱えるが、CadQueryの元の寸法式・履歴は復元されない。変更は元Pythonへ自動反映しない。
- **ブラウザーだけでGUI編集：Onshape等へSTEPをインポート。** 外部サービスへのアップロードは自分で行う。契約・公開範囲の条件を確認する。これも元Pythonへ自動反映しない。
- **Bambu Studio：印刷準備。** 配置、向き、支持、印刷条件には使えるが、機構部品の穴径や歯形を正しく設計し直す主CADとしては使わない。全体スケーリングはねじ穴・クリアランスも変えてしまう。

現CAD原本は**CadQuery**。FreeCADネイティブの編集履歴付きFCStdやOpenSCADではない。

## 触るファイル（B3）

| 変更したいところ | 主な原本 |
|---|---|
| 開口、行程、回転角など | `bench_manual_v3/cad/parameters.json` |
| 爪、ラック、ドラム、糸端ビーズ | `bench_manual_v3/cad/head.py` |
| カム、ばね側板、案内輪、支持台等 | `bench_manual_v3/cad/prototype.py` |
| B3の追加案内・固定機構・輪郭調整 | `bench_manual_v3/cad/refinements.py` |
| 組立位置・姿勢 | `bench_manual_v3/cad/build.py` |
| 表示上の糸経路 | `bench_manual_v3/cad/wire_paths.py` |
| 印刷方向・必要個数 | `bench_manual_v3/cad/bench.py` |
| 3MFの配置 | `bench_manual_v3/cad/make_plates.py` |
| 購入品の数・組立説明の生成 | `bench_manual_v3/cad/documents.py` |

JSONだけで全寸法が連動する完全パラメトリック化はできていない。Python内に数値で固定した寸法も残る。例えば`cable_stop_button`はhead.pyに外半径1.05・厚さ0.6・穴半径0.4が直接書かれている。大きくする場合は収納部との適合も確認する。

`parameters.json`のversion欄が0.12なのは派生元の名残であり、フォルダー名bench_manual_v3とREADMEがB3の識別。全体V0.12とB3の設定ファイルは独立している。

## 最小の編集手順

1. B3フォルダーを別名で複製して保存版を残す。新しい版ではtools/project.pyの選択肢も合わせるか、複製先の`python cad/run_complete.py`等を実行する。
2. 寸法を一つだけ変更し、まず単品STEP／STLを生成。
3. 対になる部品と組立状態で干渉・抜け止め・組立順を確認。
4. 全体再生成とCAD検査。HTMLで動作状態を切り替える。
5. スライサーで印刷方向、糸溝、小穴、歯先、支持を確認。嵌合片／少数部品から印刷。
6. 新しい寸法と結果、BOM変更、必要な購入品を記録する。

自分でGUI編集するならまずFreeCADで組立STEPを開き、対象の固体を選ぶところから。単品STEPが欲しい場合はSETUP.mdのpartコマンドを使う。STLは三角形のメッシュなので、本格的な寸法修正はSTEPか原本から行う。

公式資料：
- CadQuery：https://cadquery.readthedocs.io/en/stable/installation.html
- FreeCAD：https://www.freecad.org/features
- OnshapeのSTEP編集：https://www.onshape.com/en/resource-center/tech-tips/import-edit-step-iges-parasolid-stl
