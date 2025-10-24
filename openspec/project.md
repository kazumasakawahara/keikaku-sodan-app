# Project Context

## Purpose
計画相談支援事業所における利用者情報の一元管理システム。紙ベース・Excel管理から脱却し、効率的な情報共有と支援履歴の可視化を実現する。

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML/CSS/JavaScript, Bootstrap 5, Jinja2
- **Package Manager**: uv (高速Pythonパッケージマネージャー)
- **PDF Generation**: Docling, ReportLab (Phase 2以降)
- **Visualization**: D3.js または Cytoscape.js (Phase 3以降)

## Project Conventions

### Code Style
- PEP 8準拠のPythonコード
- 関数・クラスには日本語のドキュメント文字列
- 変数名は英語、コメントは日本語
- 型ヒントを積極的に使用

### Architecture Patterns
- RESTful API設計
- MVCパターン（Models, Views, Controllers/API endpoints）
- サービス層でビジネスロジックをカプセル化
- Pydanticスキーマでデータ検証

### Database Design
- 論理削除（`is_deleted`フラグ）を採用
- すべてのテーブルに`created_at`、`updated_at`を持つ
- 外部キーで整合性を保証
- 検索頻度の高いフィールドにインデックスを作成

### Testing Strategy
- 単体テスト: pytest
- 統合テスト: FastAPIのTestClient
- 手動テスト: ブラウザでの動作確認
- テストデータは架空のデータを使用（個人情報保護）

### Git Workflow
- `main`: 安定版（本番デプロイ可能）
- `develop`: 開発版
- `feature/xxx`: 機能開発ブランチ
- コミットメッセージ形式: `[Phase1] 利用者管理: CRUDエンドポイント実装`

## Domain Context

### 計画相談支援とは
障害者総合支援法に基づき、障害のある方が適切なサービスを利用できるよう支援する事業。計画相談支援専門員が利用者のニーズを把握し、サービス利用計画を作成・モニタリングする。

### 主要なドメイン概念
- **利用者**: 障害福祉サービスを利用する方
- **手帳**: 療育手帳（知的障害）、精神障害者保健福祉手帳
- **障害支援区分**: 1〜6の段階（数字が大きいほど支援の必要度が高い）
- **成年後見制度**: 判断能力が不十分な方を法的に保護する制度（後見・保佐・補助）
- **相談支援専門員**: 利用者の相談支援を行う専門職
- **サービス事業所**: 就労支援、生活介護、グループホーム等のサービス提供事業所
- **モニタリング**: サービス利用計画が適切に実施されているか定期的に確認すること

### 業務フロー
1. 利用者からの相談受付（来所/訪問/電話）
2. 利用者情報の登録・更新
3. サービス利用計画の作成（Phase 2）
4. モニタリングの実施（Phase 2）
5. ケース会議の開催とネットワーク調整（Phase 3）

## Important Constraints

### 技術的制約
- SQLiteの同時書き込み制限（ユーザー数3〜4名のため影響は軽微）
- ローカル環境での運用（インターネット接続は必須ではない）
- シングルデータベース（複数事業所対応は不要）

### ビジネス制約
- 個人情報保護法の遵守
- 監査証跡の保持（論理削除による）
- データ保持期間: 少なくとも5年（法的要件）

### 運用制約
- 単独事業所内での利用（3〜4名のスタッフ）
- 事業所内サーバーまたはローカルPCでの運用推奨
- 定期的なバックアップが必須

## External Dependencies

### 主要な外部ライブラリ
- FastAPI: Webフレームワーク
- SQLAlchemy: ORM
- Passlib: パスワードハッシュ化
- Jinja2: テンプレートエンジン
- Bootstrap 5: UIフレームワーク

### 将来的な依存関係（Phase 2以降）
- Docling: PDF生成
- ReportLab: PDF生成（補助）
- D3.js または Cytoscape.js: ネットワーク図可視化

### 外部API（オプション）
- 郵便番号検索API: 住所自動入力（検討中）

## Phase Strategy

### Phase 1: 基本機能（MVP）- 現在のフェーズ
目標: 紙ベース管理から脱却し、基本的な利用者情報管理と相談記録を電子化

機能:
- 認証・認可
- 利用者管理（CRUD、年齢自動計算、手帳管理）
- 相談記録管理
- 関係機関管理
- スタッフ管理

### Phase 2: 計画・記録機能
目標: サービス利用計画とモニタリング機能の追加、PDF出力

機能:
- サービス利用計画管理
- モニタリング記録管理
- PDF出力（ケース会議用資料、家族交付用資料）

### Phase 3: 可視化・高度機能
目標: ネットワーク図と高度な分析機能

機能:
- ネットワーク図機能（D3.jsまたはCytoscape.js）
- 高度な検索・分析
- 統計情報の可視化

### Phase 4: 将来の拡張
目標: さらなる利便性向上

機能:
- 過去データのインポート（Excel → CSV → DB）
- 外部システム連携（必要に応じて）
- 通知機能（手帳更新期限、モニタリング実施期限）

## Security Considerations

### 認証・認可
- セッションベース認証（FastAPIのSessionMiddleware）
- パスワードのbcryptハッシュ化
- ロールベースアクセス制御（admin/staff）
- セッションタイムアウト: 30分

### データ保護
- SQLインジェクション対策: SQLAlchemyのORM使用
- XSS対策: Jinja2の自動エスケープ
- CSRF対策: 将来実装予定
- 個人情報の暗号化: 必要に応じて実装

### 監査
- ログイン試行の記録
- CRUD操作のログ記録（誰が、いつ、何を変更したか）
- 論理削除による削除履歴の保持

## Development Environment

### Setup
```bash
# uvのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトセットアップ
cd ~/AI-Workspace/keikaku-sodan-app
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# データベース初期化
python scripts/init_db.py

# 開発サーバー起動
uvicorn app.main:app --reload
```

### 推奨ツール
- エディタ: VS Code, PyCharm
- ブラウザ: Chrome（開発者ツールが充実）
- データベース閲覧: DB Browser for SQLite

## Naming Conventions

### ファイル・ディレクトリ
- Pythonファイル: `snake_case.py`
- テンプレート: `snake_case.html`
- スタティックファイル: `kebab-case.css`, `kebab-case.js`

### コード内
- 変数・関数: `snake_case`
- クラス: `PascalCase`
- 定数: `UPPER_SNAKE_CASE`
- プライベートメンバ: `_leading_underscore`

### データベース
- テーブル名: 複数形（`users`, `consultations`）
- カラム名: `snake_case`
- インデックス名: `idx_<table>_<column>`
