# 自動TF装置：別PC・クラウドへの引き継ぎ

2026-11-08時点のスナップショット。**最初にHANDOFF.mdを読んでください。**

- [引き継ぎ・再開指示](HANDOFF.md)：次のAI／設計者へ渡す記録。
- [最新仕様](SPEC.md)：確定したCAD、ユーザー要求、未実装の相談案を区別。
- [環境構築](SETUP.md)：Python／Docker／クラウドで再開。
- [自分で部品を直す方法](EDITING.md)：CadQueryとGUI CADの使い分け。
- [卓上B3 HTML](bench_manual_v3/output/卓上手動治具.html)：軽量、まずこれを開く。
- [全体V0.12 HTML](v0_12/output/viewer.html)：重い全体モデル。
- [B3組立](bench_manual_v3/docs/組立と手動確認.md)
- [購入先・部品数](bench_manual_v3/docs/B3_購入リンク.md)：販売状況は購入時点の記録。

`python tools/project.py inspect` と `python tools/project.py verify` はCADソフトなしで実行可能。

仕様書＋STLだけではパラメトリック設計の続きを再現できません。この一式には **Python CAD原本、寸法JSON、STEP、STL、3MF、HTML、参考PDF、検査記録、実行用設定** を収録しました。

このZIPは引き継ぎ用の保存データであり、クラウドへのアップロード・アカウント作成・実行環境の起動はしていません。Docker／新規環境でのCAD再生成は今回未実行。詳細はSETUP.mdとVERIFICATION.mdを参照。
