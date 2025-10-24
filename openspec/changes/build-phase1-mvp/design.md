# Design: Phase 1 MVP Application

## Context

計画相談支援事業所向けの利用者管理システムを新規構築します。プログラミング初心者でも保守できるシンプルな設計を優先しつつ、将来的な拡張性も考慮します。

### Constraints
- 単独事業所での利用（複数事業所対応は不要）
- ユーザー数: 3〜4名の専門員 + 管理者1名
- 既存システムとの連携: なし
- 運用環境: 事業所内サーバー（ローカル環境）

### Stakeholders
- **計画相談支援専門員**: 日常的に利用者情報を登録・閲覧・更新
- **管理者**: システム全体の管理、スタッフ管理
- **開発者**: プログラミング初心者でも理解・保守可能な設計が必要

## Goals / Non-Goals

### Goals
- ✅ 紙ベース・Excel管理から脱却
- ✅ 利用者情報の一元管理と効率的な検索
- ✅ スタッフ間での情報共有
- ✅ シンプルで保守しやすいコード
- ✅ 将来的なPostgreSQL/Neo4jへの移行可能性

### Non-Goals
- ❌ 複数事業所対応
- ❌ 外部システムとの連携（Phase 1では不要）
- ❌ モバイルアプリ（ブラウザベースで十分）
- ❌ リアルタイム通知（Phase 1では不要）

## Decisions

### Decision 1: データベースにSQLiteを採用

**選択**: SQLite
**理由**:
- ファイルベースでセットアップが簡単
- 単独事業所（ユーザー数3〜4名）には十分な性能
- バックアップが容易（ファイルコピーだけ）
- プログラミング初心者にも扱いやすい

**代替案**:
- PostgreSQL: より高性能だがセットアップが複雑、現時点ではオーバースペック
- MySQL: 同様の理由でオーバースペック
- Neo4j: ネットワーク図機能を考慮したが、学習コストが高く、Phase 1では不要

**移行パス**: 将来的にPostgreSQL（複数事業所対応時）やNeo4j（ネットワーク分析強化時）への移行を考慮した設計

### Decision 2: FastAPIを採用

**選択**: FastAPI
**理由**:
- 高速で軽量
- 型ヒントによる安全性とIDEサポート
- 自動ドキュメント生成（Swagger UI）
- 日本語ドキュメントが充実
- 学習曲線が緩やか

**代替案**:
- Django: 高機能だが重厚で学習コストが高い
- Flask: シンプルだが型安全性が低く、自動ドキュメント生成がない

### Decision 3: uvをパッケージマネージャーに採用

**選択**: uv
**理由**:
- pipより10-100倍高速（Rust製）
- 依存関係の競合を自動解決
- プログラミング初心者でもトラブルが少ない
- ロックファイルで環境の再現性が高い

**代替案**:
- pip: 標準だが遅く、依存関係の競合に弱い
- poetry: 高機能だが学習コストが高い

### Decision 4: Jinja2テンプレート + Bootstrap 5

**選択**: サーバーサイドレンダリング（Jinja2 + Bootstrap 5）
**理由**:
- シンプルで学習コストが低い
- レスポンシブデザインが容易
- JavaScriptフレームワーク（React/Vue）は不要

**代替案**:
- React/Vue + API: SPA構築には学習コストが高く、Phase 1では過剰

### Decision 5: 年齢の動的計算

**選択**: データベースには生年月日のみを保存し、表示時に動的計算
**理由**:
- データの整合性（常に最新の年齢を表示）
- ストレージの節約
- 計算コストは無視できるレベル

**実装**:
```python
from datetime import date

def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age
```

### Decision 6: 手帳情報の別テーブル化

**選択**: `notebooks`テーブルを独立させる
**理由**:
- 1人の利用者が複数の手帳（療育手帳+精神障害者保健福祉手帳）を所持する可能性
- 正規化により冗長性を排除

**データ構造**:
- `users` 1:N `notebooks`
- 各手帳レコードに種別、等級、交付日、更新日を保存

### Decision 7: 論理削除の採用

**選択**: 物理削除ではなく論理削除（`is_deleted`フラグ）
**理由**:
- 監査証跡の保持
- データ復旧の可能性
- 誤削除への対応

**実装**: 各テーブルに`is_deleted: BOOLEAN`フィールドを追加

## Database Schema

### Core Tables

#### users (利用者)
```sql
id: INTEGER PRIMARY KEY
name: TEXT NOT NULL
name_kana: TEXT
birth_date: DATE NOT NULL
gender: TEXT
postal_code: TEXT
address: TEXT
phone: TEXT
email: TEXT
emergency_contact_name: TEXT
emergency_contact_phone: TEXT
disability_support_level: INTEGER (1-6)
disability_support_certified_date: DATE
disability_support_expiry_date: DATE
guardian_type: TEXT (後見/保佐/補助)
guardian_name: TEXT
guardian_contact: TEXT
assigned_staff_id: INTEGER (FK to staff)
is_deleted: BOOLEAN DEFAULT FALSE
created_at: DATETIME
updated_at: DATETIME
```

#### notebooks (手帳)
```sql
id: INTEGER PRIMARY KEY
user_id: INTEGER NOT NULL (FK to users)
notebook_type: TEXT NOT NULL (療育手帳/精神障害者保健福祉手帳)
grade: TEXT
issue_date: DATE
renewal_date: DATE
notes: TEXT
is_deleted: BOOLEAN DEFAULT FALSE
created_at: DATETIME
updated_at: DATETIME
```

#### consultations (相談記録)
```sql
id: INTEGER PRIMARY KEY
user_id: INTEGER NOT NULL (FK to users)
staff_id: INTEGER NOT NULL (FK to staff)
consultation_date: DATETIME NOT NULL
consultation_type: TEXT (来所/訪問/電話/その他)
content: TEXT
response: TEXT
is_deleted: BOOLEAN DEFAULT FALSE
created_at: DATETIME
updated_at: DATETIME
```

#### organizations (関係機関)
```sql
id: INTEGER PRIMARY KEY
name: TEXT NOT NULL
type: TEXT NOT NULL (サービス事業所/医療機関/後見人/その他)
postal_code: TEXT
address: TEXT
phone: TEXT
fax: TEXT
email: TEXT
contact_person: TEXT
contact_person_phone: TEXT
notes: TEXT
is_deleted: BOOLEAN DEFAULT FALSE
created_at: DATETIME
updated_at: DATETIME
```

#### user_organizations (利用者-関係機関 中間テーブル)
```sql
id: INTEGER PRIMARY KEY
user_id: INTEGER NOT NULL (FK to users)
organization_id: INTEGER NOT NULL (FK to organizations)
relationship_type: TEXT (主治医/通所先/後見人/その他)
start_date: DATE
end_date: DATE
frequency: TEXT (毎日/週1回/月1回/その他)
notes: TEXT
is_deleted: BOOLEAN DEFAULT FALSE
created_at: DATETIME
updated_at: DATETIME
```

#### staff (職員)
```sql
id: INTEGER PRIMARY KEY
username: TEXT UNIQUE NOT NULL
password_hash: TEXT NOT NULL
name: TEXT NOT NULL
role: TEXT NOT NULL (admin/staff)
email: TEXT
is_active: BOOLEAN DEFAULT TRUE
created_at: DATETIME
updated_at: DATETIME
```

### Indexes
```sql
-- 検索高速化
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_birth_date ON users(birth_date);
CREATE INDEX idx_users_assigned_staff_id ON users(assigned_staff_id);
CREATE INDEX idx_users_is_deleted ON users(is_deleted);

CREATE INDEX idx_consultations_user_id ON consultations(user_id);
CREATE INDEX idx_consultations_date ON consultations(consultation_date);
CREATE INDEX idx_consultations_staff_id ON consultations(staff_id);

CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_type ON organizations(type);

CREATE INDEX idx_user_organizations_user_id ON user_organizations(user_id);
CREATE INDEX idx_user_organizations_org_id ON user_organizations(organization_id);
```

## API Design

### RESTful Endpoints

#### Authentication
- `POST /api/auth/login` - ログイン
- `POST /api/auth/logout` - ログアウト
- `GET /api/auth/me` - 現在のユーザー情報

#### Users
- `GET /api/users` - 利用者一覧（検索・フィルタリング対応）
- `GET /api/users/{id}` - 利用者詳細
- `POST /api/users` - 利用者作成
- `PUT /api/users/{id}` - 利用者更新
- `DELETE /api/users/{id}` - 利用者削除（論理削除）

#### Notebooks
- `GET /api/users/{user_id}/notebooks` - 手帳一覧
- `POST /api/users/{user_id}/notebooks` - 手帳作成
- `PUT /api/notebooks/{id}` - 手帳更新
- `DELETE /api/notebooks/{id}` - 手帳削除

#### Consultations
- `GET /api/consultations` - 相談記録一覧
- `GET /api/users/{user_id}/consultations` - 特定利用者の相談記録
- `POST /api/consultations` - 相談記録作成
- `PUT /api/consultations/{id}` - 相談記録更新
- `DELETE /api/consultations/{id}` - 相談記録削除

#### Organizations
- `GET /api/organizations` - 関係機関一覧
- `GET /api/organizations/{id}` - 関係機関詳細
- `POST /api/organizations` - 関係機関作成
- `PUT /api/organizations/{id}` - 関係機関更新
- `DELETE /api/organizations/{id}` - 関係機関削除

#### User-Organization Relations
- `GET /api/users/{user_id}/organizations` - 利用者の関係機関一覧
- `POST /api/users/{user_id}/organizations` - 関係機関との紐付け
- `DELETE /api/users/{user_id}/organizations/{org_id}` - 紐付け解除

#### Staff
- `GET /api/staff` - スタッフ一覧
- `POST /api/staff` - スタッフ作成
- `PUT /api/staff/{id}` - スタッフ更新
- `DELETE /api/staff/{id}` - スタッフ削除

## Security Design

### Authentication
- セッションベース認証（FastAPIの`SessionMiddleware`）
- パスワードハッシュ化（`passlib[bcrypt]`）
- タイムアウト: 30分無操作でログアウト

### Authorization
- ロールベース: `admin`と`staff`
- `admin`: 全機能アクセス可能
- `staff`: 自分が担当する利用者のみアクセス可能

### Data Protection
- SQLインジェクション対策: SQLAlchemyのORM使用
- XSS対策: Jinja2の自動エスケープ
- CSRF対策: FastAPIのCSRF保護（将来実装）

## UI/UX Design Principles

### レイアウト
- 左サイドバー: 固定ナビゲーションメニュー
- メインコンテンツ: 中央エリア
- レスポンシブ: タブレット対応（ハンバーガーメニュー）

### カラースキーム
- プライマリ: #2C5F8D（落ち着いた青）
- セカンダリ: #4A9B7F（やさしい緑）
- 背景: #F8F9FA（明るいグレー）

### フォント・スペーシング
- 本文: 16px
- 見出し: 20-28px
- カード間: 20-30px
- 余白を十分に確保（可読性優先）

## Risks / Trade-offs

### Risk 1: SQLiteの同時書き込み制限
**リスク**: SQLiteは複数ユーザーの同時書き込みに弱い
**影響度**: 低（ユーザー数3〜4名、同時書き込みは稀）
**対策**: 将来的にPostgreSQLへの移行パスを確保

### Risk 2: セキュリティ
**リスク**: 個人情報を扱うため、セキュリティが重要
**対策**:
- パスワードハッシュ化
- セッション管理
- SQLインジェクション・XSS対策
- ローカル環境での運用推奨

### Risk 3: 初心者による保守
**リスク**: プログラミング初心者が保守する可能性
**対策**:
- 豊富な日本語コメント
- シンプルな設計
- ドキュメントの充実

## Migration Plan

### Phase 1 → Phase 2
- サービス利用計画管理機能の追加
- モニタリング記録管理機能の追加
- PDF出力機能の追加

### Phase 2 → Phase 3
- ネットワーク図機能の追加（D3.js または Cytoscape.js）
- 高度な検索・分析機能

### 将来的なデータベース移行
- SQLite → PostgreSQL: スキーマ変更は最小限
- PostgreSQL → Neo4j: リレーションシップデータを活用

### Rollback Strategy
- データベースバックアップを定期実行
- スクリプト`scripts/backup_db.py`で自動化
- Gitによるコードバージョン管理

## Open Questions

1. **バックアップ頻度**: 毎日？週1回？
2. **データ保持期間**: 何年間保存する？
3. **アクセスログ**: 誰がいつ何を閲覧したか記録する？
4. **手帳更新期限アラート**: Phase 1で実装する？Phase 2以降？
5. **郵便番号から住所自動入力**: 外部APIを使う？オフライン対応？

## Implementation Notes

### 開発環境セットアップ
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

### テスト戦略
- 単体テスト: pytest
- 統合テスト: FastAPIのTestClient
- 手動テスト: ブラウザでの動作確認

### ドキュメント
- コード内コメント: 日本語
- API仕様: Swagger UIで自動生成
- ユーザーマニュアル: Phase 1完了後に作成
