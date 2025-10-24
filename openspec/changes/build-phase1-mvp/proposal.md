# Proposal: Build Phase 1 MVP Application

## Why

計画相談支援事業所では、現在紙ベースおよびExcelでの利用者管理を行っており、以下の課題があります:
- 情報共有の非効率性（複数スタッフ間での情報共有が困難）
- 検索性の低さ（必要な情報を素早く見つけることができない）
- 更新履歴の追跡不可（誰がいつ何を変更したか不明）
- データの散在（利用者情報が複数箇所に分散）

これらの課題を解決するため、Webベースの一元管理システムを構築します。Phase 1では、日常業務に最低限必要な基本機能（MVP）を実装し、動作するシステムを構築します。

## What Changes

Phase 1で実装する5つの中核機能:

1. **認証機能** - ログイン/ログアウト、セッション管理、権限チェック
2. **利用者管理** - CRUD操作、年齢自動計算、手帳情報管理、成年後見制度情報管理
3. **相談記録管理** - 相談記録のCRUD、担当者・日時管理、相談形態の記録
4. **関係機関管理** - 事業所・医療機関・後見人等の登録、連絡先管理、利用者との紐付け
5. **スタッフ管理** - 相談支援専門員の登録、アクセス権限設定（管理者/一般）

### 技術スタック
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML/CSS/JavaScript, Bootstrap 5, Jinja2
- **Package Manager**: uv (高速で依存関係解決に優れる)

### アプリケーション構造
```
app/
├── main.py              # FastAPIエントリーポイント
├── config.py            # 設定管理
├── models/              # SQLAlchemyモデル
├── schemas/             # Pydanticスキーマ
├── api/                 # APIエンドポイント
├── services/            # ビジネスロジック
├── database/            # DB接続・セッション管理
├── templates/           # Jinja2テンプレート
└── static/              # CSS/JS/画像
```

## Impact

### Affected specs
新規作成される仕様:
- `user-management` - 利用者情報の管理
- `consultation-records` - 相談記録の管理
- `organization-management` - 関係機関の管理
- `authentication` - 認証・認可
- `staff-management` - スタッフ管理

### Affected code
新規作成されるコード:
- `app/` - アプリケーション全体
- `scripts/` - DB初期化、シードデータ、バックアップスクリプト
- `tests/` - テストコード

### 利用者への影響
- 紙ベース管理から脱却し、効率的な情報管理が可能
- 検索・絞り込み機能により必要な情報へ素早くアクセス
- スタッフ間での情報共有がリアルタイムで可能
- データの一元管理により情報の散在を解消

### 運用環境
- 対象ユーザー: 計画相談支援専門員 3〜4名、管理者 1名
- 利用環境: 事業所内サーバー（ローカル環境推奨）
- デバイス: PC（Windows/Mac）メイン、タブレット（iPad等）サブ

### セキュリティ考慮事項
- パスワードのハッシュ化（bcrypt）
- セッション管理（30分無操作でタイムアウト）
- SQLインジェクション対策（SQLAlchemyのORM使用）
- データの論理削除（監査証跡の保持）
