# 別PC・クラウドでの起動

## まず表示だけ

B3の `bench_manual_v3/output/卓上手動治具.html` をダブルクリック。外部ライブラリ不要の保存HTMLなのでCADソフトなしで確認できる。全体HTMLは大きい。

## Python方式：Mac／Windows／Linux共通

Python 3.11を使う。元CADの直接依存はrequirements.txtにまとめた。CadQueryは2.8.0固定、他の依存は範囲指定で、完全な環境ロックではない。正常構築した環境で `python -m pip freeze > requirements.resolved.txt` を保存すれば、次の移行の参考になる。

Mac/Linux：

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python tools/project.py inspect
python tools/project.py verify
python tools/project.py smoke
```

Windows PowerShell（Python 3.11がインストール済み）：

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe tools/project.py smoke
```

以降、Windowsでは各 `python` を `.venv\Scripts\python.exe` に読み替える。

```sh
# B3全体を再生成し、CAD検査・印刷配置・経路表を更新
python tools/project.py bench

# 1部品のみSTEP/STLへ書き出す（原点姿勢。印刷方向は別確認）
python tools/project.py part --name cable_stop_button

# 全体V0.12のモデル生成と検査は重いため分ける
python tools/project.py full-export
python tools/project.py full-check

# HTMLをクラウドの転送ポートで見る（使用する環境で8000を転送）
python tools/project.py serve --port 8000
```

単品の出力は `output/edited_parts/`。元の印刷STLや組立HTMLとは別ファイルなので、確認後に全体を再生成する。元CADの手順は各READMEに残してある。`.venv`を別PCへコピーせず、環境を新しく構築する。

## Docker方式：Linuxクラウドでの候補

Docker対応環境でZIPを展開し、そのフォルダーを作業ディレクトリにする。

```sh
docker build -t tf-cad .
docker run --rm tf-cad python tools/project.py smoke
```

生成物を残すにはホストの作業フォルダーをマウントする。Mac/Linuxの例：

```sh
docker run --rm -v "$PWD:/work" tf-cad python tools/project.py bench
docker run --rm -p 127.0.0.1:8000:8000 -v "$PWD:/work" tf-cad python tools/project.py serve
```

WindowsではDockerのフォルダーマウント構文に合わせる。マウントしない `docker run --rm` で生成すると、コンテナ削除時に生成物も消える。

`.devcontainer/devcontainer.json`も同梱。Dev Containers対応のクラウド／VS Codeで、このフォルダーをプロジェクトのルートとして開く。GitHub Codespaces等を使う場合のリポジトリ作成・アップロードはユーザー側で行う。この作業ではクラウドアカウントに接続・配置していない。

クラウドでは4CPU／8GB RAM以上を出発点とする（保証スペックではない）。重い全体CADの同時生成を避け、まずB3を再生成する。G-codeの生成・プリンター接続は別作業。Picoの実機制御をクラウドから直接行う設定は含まない。

## 検証の限界

- この作業環境にはCadQueryの実行環境が残っていない。旧 `/private/tmp/tf-cad-venv` は依存を読み込めず、そのパスに頼らない構成へ整理した。
- 新しい隔離環境へのpipインストールを試したが、ネットワークの名前解決制限で取得できなかった。
- Dockerコマンドもこの環境にはない。そのため、**新規環境でのCADカーネル実行・Dockerビルド・クラウド起動は未確認**。
- 収録データの整合性、Python構文、標準ライブラリだけの入口コマンドは今回チェック。保存CAD検査結果は以前の実行記録。
- 元のrelease.pyはブラウザー検査記録も参照するため、今回の入口から自動で合格扱いのリリースは作らない。B3再生成時には以前のrelease.json／browser.jsonをhistoricalへ退避する。
- SHA256照合は受け取り時の同一性確認。正当に編集・再生成した後は差分が出る。新しい版を作るときにマニフェストも更新する。

インストール公式手順：https://cadquery.readthedocs.io/en/stable/installation.html

## 省略した重複データ

全体V0.12の大容量previews/state_*.jsonキャッシュ、progress_now.htmlの重複、古い一式ZIP、Python環境とキャッシュは省略。全体の自己完結viewer.html・STEP・印刷部品・原本は保持。V0.12のキャッシュを必要とするpublish_viewer.pyだけを先に実行せず、full-exportで生成し直す。履歴文書の旧リンクより最上位の案内を優先する。
