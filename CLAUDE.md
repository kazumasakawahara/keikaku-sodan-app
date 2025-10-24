<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# 計画相談支援 利用者管理システム

## 🎯 プロジェクト概要

計画相談支援事業所における利用者情報の一元管理システム。
現在の紙ベース・Excel管理から脱却し、効率的な情報共有と支援履歴の可視化を実現する。

### 対象ユーザー
- 計画相談支援専門員: 3〜4名
- 管理者: 1名
- 単独事業所内での利用

### 利用環境
- 主要: PC (Windows/Mac)
- 副次: iPad等のタブレット
- ブラウザベースのWebアプリケーション

---

## 🛠️ 技術スタック

### バックエンド
- **Python 3.11+**: メインプログラミング言語
- **FastAPI**: 高速なWebフレームワーク
- **SQLAlchemy**: ORM(データベース操作)
- **SQLite**: 開発・本番用データベース(単独事業所向け)
  - 将来的にPostgreSQLやNeo4jへの移行も可能な設計

### フロントエンド
- **HTML/CSS/JavaScript**: 基本技術
- **Bootstrap 5**: レスポンシブUIフレームワーク
- **Jinja2**: テンプレートエンジン

### PDF生成
- **Docling**: ドキュメント生成・変換ツール
- **ReportLab**: Python用PDF生成ライブラリ(補助的に使用)

### ネットワーク図
- **D3.js**: データ可視化ライブラリ
- または **Cytoscape.js**: グラフ可視化ライブラリ

---

## 📁 プロジェクト構造

```
keikaku-sodan-app/
├── CLAUDE.md                 # このファイル
├── HANDOVER.md              # 引継書
├── README.md                # プロジェクト説明書
├── WIREFRAME.md             # UI設計書
├── requirements.txt         # Python依存関係
├── .env.example            # 環境変数サンプル
├── .gitignore              # Git除外設定
│
├── docs/                   # ドキュメント
│   ├── requirements.md     # 要件定義書
│   ├── specification.md    # 機能仕様書
│   ├── database-design.md  # データベース設計書
│   └── api-spec.md         # API仕様書
│
├── app/                    # アプリケーション本体
│   ├── __init__.py
│   ├── main.py            # FastAPIエントリーポイント
│   ├── config.py          # 設定管理
│   │
│   ├── models/            # データモデル(SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py        # 利用者モデル
│   │   ├── staff.py       # スタッフモデル
│   │   ├── consultation.py # 相談記録モデル
│   │   ├── plan.py        # 計画モデル
│   │   ├── monitoring.py  # モニタリングモデル
│   │   └── organization.py # 関係機関モデル
│   │
│   ├── schemas/           # Pydanticスキーマ(API入出力)
│   │   ├── __init__.py
│   │   └── ...
│   │
│   ├── api/               # APIエンドポイント
│   │   ├── __init__.py
│   │   ├── users.py       # 利用者API
│   │   ├── consultations.py
│   │   ├── plans.py
│   │   └── ...
│   │
│   ├── services/          # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── pdf_service.py  # PDF生成サービス
│   │   └── network_service.py # ネットワーク図生成
│   │
│   ├── database/          # データベース関連
│   │   ├── __init__.py
│   │   ├── connection.py  # DB接続管理
│   │   └── session.py     # セッション管理
│   │
│   ├── templates/         # HTMLテンプレート
│   │   ├── base.html
│   │   ├── users/
│   │   ├── consultations/
│   │   └── ...
│   │
│   └── static/            # 静的ファイル
│       ├── css/
│       ├── js/
│       └── images/
│
├── tests/                 # テストコード
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_api.py
│   └── ...
│
└── scripts/              # ユーティリティスクリプト
    ├── init_db.py        # DB初期化
    ├── seed_data.py      # テストデータ投入
    └── backup_db.py      # バックアップ
```

---

## 🚀 開発環境セットアップ

### 前提条件
- Python 3.11以上
- **uv** (高速Pythonパッケージマネージャー)
  - 依存関係の解決が優れており、トラブルを最小限に抑えられる

### uvのインストール

```bash
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# または Homebrew:
brew install uv

# インストール確認
uv --version
```

### セットアップ手順（uv使用）

```bash
# 1. プロジェクトディレクトリに移動
cd ~/AI-Workspace/keikaku-sodan-app

# 2. uvで仮想環境を作成し、自動的に有効化
uv venv

# 3. 仮想環境の有効化（手動で行う場合）
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 4. 依存パッケージのインストール（uvが自動的に依存関係を解決）
uv pip install -r requirements.txt

# または pyproject.toml がある場合:
uv pip install -e .

# 5. データベースの初期化
python scripts/init_db.py

# 6. 開発サーバーの起動
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# または仮想環境が有効化されている場合:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### uvの利点
- **高速**: Rust製で、pipより10-100倍高速
- **依存関係解決**: 複雑な依存関係も正確に解決
- **ロックファイル**: 再現可能な環境を保証
- **シンプル**: 直感的なコマンド

### 初回起動後
ブラウザで `http://localhost:8000` にアクセスして動作確認

---

## 📝 開発の進め方

### Phase 1: 基本機能(MVP) - 最優先 🎯
1. **利用者基本情報管理**
   - CRUD機能(作成・読取・更新・削除)
   - 年齢の自動計算
   - 手帳情報管理(療育手帳・精神障害者保健福祉手帳)
   - 成年後見制度情報管理

2. **相談支援記録管理**
   - 相談記録のCRUD
   - 担当者・日時管理
   - 相談形態の記録

3. **関係機関管理**
   - 事業所・医療機関・後見人等の登録
   - 連絡先管理

4. **検索・閲覧機能**
   - 利用者名検索
   - 担当者フィルター
   - 一覧表示・詳細表示

5. **スタッフ管理**
   - 相談支援専門員の登録
   - アクセス権限設定(管理者/一般)

### Phase 2: 計画・記録機能
1. **サービス利用計画管理**
2. **モニタリング記録管理**
3. **基本的なPDF出力機能**

### Phase 3: 可視化・高度機能
1. **簡易ネットワーク図機能**
2. **ネットワーク図のPDF出力**
3. **高度な検索・分析機能**

### Phase 4: 将来の拡張
1. **過去データのインポート**
2. **外部システム連携**

---

## 💾 データベース設計方針

### Phase 1: SQLite
- **理由**: 
  - セットアップが簡単(ファイルベース)
  - 単独事業所での利用に十分な性能
  - バックアップが容易(ファイルコピーだけ)
  - プログラミング初心者にも扱いやすい

### 将来の移行パス
- **PostgreSQL**: 複数事業所対応や大規模データ時
- **Neo4j**: ネットワーク分析を本格的に行う場合
  - 現在のSQLite設計でも、将来的な移行が可能な構造にする
  - リレーションシップを明確に定義

---

## 🎨 UI/UX方針

### デザイン原則
1. **シンプル・直感的**: 複雑な操作を避ける
2. **レスポンシブ**: PC・タブレット両対応
3. **アクセシビリティ**: 読みやすいフォント・配色
4. **効率性**: 少ないクリックで目的達成

### 画面構成
- **ダッシュボード**: 最近の相談記録、注目すべき利用者
- **利用者一覧**: 検索・フィルタリング機能付き
- **利用者詳細**: タブ形式で情報整理
  - 基本情報
  - 相談記録
  - 計画・モニタリング
  - ネットワーク図
  - 関係機関

詳細は **WIREFRAME.md** を参照してください。

---

## 🔒 セキュリティとプライバシー

### 基本方針
1. **ローカル環境での運用**: 事業所内サーバー推奨
2. **アクセス制御**: ログイン認証必須
3. **データ暗号化**: 機密情報は暗号化して保存
4. **バックアップ**: 定期的な自動バックアップ
5. **監査ログ**: データ変更履歴の記録

---

## 📚 重要な技術的決定事項

### 1. データベースにSQLiteを選択
**理由**:
- 単独事業所での利用に最適
- セットアップ・管理が簡単
- ファイルベースでバックアップが容易
- 将来的な拡張性も担保

### 2. FastAPIを採用
**理由**:
- 高速で軽量
- 自動ドキュメント生成(Swagger UI)
- 型ヒントによる安全性
- 初心者にも学びやすい

### 3. Doclingを使用
**理由**:
- 高品質なPDF生成
- 柔軟なレイアウト対応
- 日本語対応

### 4. シンプルなネットワーク図
**理由**:
- Neo4jではなく、まずはD3.jsで可視化
- データベースは通常のリレーショナル構造
- 必要に応じて将来的にNeo4jへ移行

---

## 🧪 テスト方針

### テスト種別
1. **単体テスト**: 各機能の動作確認(pytest)
2. **統合テスト**: API全体の動作確認
3. **手動テスト**: UI操作の確認

### テストデータ
- `scripts/seed_data.py`でサンプルデータを投入
- 個人情報は架空のデータを使用

---

## 📖 参考資料

### FastAPI公式ドキュメント
https://fastapi.tiangolo.com/ja/

### SQLAlchemy公式ドキュメント
https://docs.sqlalchemy.org/

### Bootstrap 5公式ドキュメント
https://getbootstrap.jp/docs/5.0/getting-started/introduction/

### Docling関連
https://github.com/DS4SD/docling

---

## 🤝 開発時の注意事項

### コーディング規約
- PEP 8に準拠したPythonコード
- 関数・クラスには日本語のドキュメント文字列
- 変数名は英語、コメントは日本語

### コミットメッセージ
```
[Phase1] 利用者基本情報管理: CRUDエンドポイント実装
[Phase2] PDF出力機能: 基本テンプレート作成
[Fix] バグ修正: 年齢計算の誤り
```

### ブランチ戦略
- `main`: 安定版
- `develop`: 開発版
- `feature/xxx`: 機能開発ブランチ

---

## 🆘 トラブルシューティング

### よくある問題

**1. データベースエラー**
```bash
# データベースを再初期化
rm app.db
python scripts/init_db.py
```

**2. パッケージのインストールエラー（uv使用時）**
```bash
# 仮想環境を再作成
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# または pyproject.toml がある場合:
uv pip install -e .
```

**3. uvがインストールされていない**
```bash
# uvをインストール
curl -LsSf https://astral.sh/uv/install.sh | sh
# または
brew install uv
```

**4. ポートが使用中**
```bash
# 別のポートで起動
uvicorn app.main:app --reload --port 8001
```

**5. 依存関係の競合**
```bash
# uvで依存関係を再解決
uv pip compile requirements.txt -o requirements.lock
uv pip sync requirements.lock
```

---

## 📧 サポート

質問や問題があれば、HANDOVER.mdを参照するか、プロジェクトの開発者に連絡してください。

---

**最終更新**: 2025年10月24日
**バージョン**: 1.0.0
