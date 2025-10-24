# 引継書: 計画相談支援 利用者管理システム

**作成日**: 2025年10月24日  
**作成者**: Claude (要件定義フェーズ)  
**引継先**: Claude Code (開発実装フェーズ)

---

## 📋 目次
1. [プロジェクト背景](#1-プロジェクト背景)
2. [要件定義のサマリー](#2-要件定義のサマリー)
3. [技術選定の理由](#3-技術選定の理由)
4. [データベース設計方針](#4-データベース設計方針)
5. [開発フェーズと優先順位](#5-開発フェーズと優先順位)
6. [重要な設計決定事項](#6-重要な設計決定事項)
7. [次のステップ](#7-次のステップ)
8. [注意事項](#8-注意事項)

---

## 1. プロジェクト背景

### 1.1 現状の課題
計画相談支援事業所において、以下の課題が存在している:

- **非効率な管理体制**: Excelで書式を作成し、印刷して紙ベースで管理
- **情報共有の困難さ**: 複数スタッフ間での情報共有が非効率
- **検索性の低さ**: 必要な情報を素早く見つけることが困難
- **更新履歴の追跡不可**: 誰がいつ何を変更したか分からない
- **データの散在**: 利用者情報が複数の場所に分散

### 1.2 プロジェクトの目的
紙ベース・Excel管理から脱却し、以下を実現する:
- 利用者情報の一元管理
- スタッフ間での効率的な情報共有
- 利用者情報の高速検索
- 支援履歴の可視化と追跡
- ネットワーク図による支援体制の見える化
- PDF出力によるケース会議・家族交付への対応

### 1.3 利用環境
- **ユーザー**: 計画相談支援専門員 3〜4名、管理者 1名
- **事業所**: 単独事業所内での利用(複数事業所対応は不要)
- **デバイス**: 主にPC(Windows/Mac)、副次的にiPad等のタブレット
- **ネットワーク**: インターネット接続環境あり

---

## 2. 要件定義のサマリー

### 2.1 機能要件

#### A. 利用者基本情報管理 ⭐️ 最重要
**管理項目**:
- 基本情報: 氏名、生年月日、**現在の年齢(自動計算)**、住所、連絡先
- **手帳情報**(重要):
  - 療育手帳(知的障害): 等級、交付日、更新日
  - 精神障害者保健福祉手帳: 等級、交付日、更新日
  - ※ 重複所持(知的+精神)の場合、両方を登録可能
- 障害支援区分: 区分、認定日、有効期限
- **成年後見制度情報**(重要):
  - 利用有無
  - 種別(後見/保佐/補助)
  - 後見人等の氏名・連絡先
- 緊急連絡先

**注意点**:
- 年齢は生年月日から自動計算し、常に最新の年齢を表示
- 手帳の更新日が近づいたらアラート表示(将来機能)
- 成年後見人は関係機関としても管理

#### B. 相談支援記録管理
- 相談日時、対応者(担当専門員)
- 相談内容、対応内容(テキストエリア)
- 相談形態(来所/訪問/電話/その他)
- 添付ファイル(必要に応じて - Phase 2以降)

#### C. サービス利用計画管理(Phase 2)
- 計画作成日、作成者
- 計画期間(開始日〜終了日)
- 利用サービス一覧
- 支援目標
- 本人・家族の意向

#### D. モニタリング記録管理(Phase 2)
- モニタリング実施日、実施者
- サービス利用状況
- 目標達成状況
- 課題・今後の方針

#### E. 関係機関管理
**種別**:
- **サービス事業所**: 就労支援、生活介護、グループホーム等
- **医療機関**: 病院、クリニック等
- **成年後見人等**: 弁護士、司法書士、社会福祉士等
- **その他関係機関**: 行政機関、他の相談支援事業所等

**共通項目**:
- 名称、種別、郵便番号、住所、電話番号、FAX番号、メールアドレス
- 担当者名、担当者連絡先
- メモ欄

#### F. 検索・閲覧機能
- 利用者名での検索(部分一致)
- 担当専門員での絞り込み
- 手帳種別での絞り込み
- 障害支援区分での絞り込み
- 成年後見制度利用の有無での絞り込み
- 最終相談日での並び替え
- 一覧表示・詳細表示

#### G. スタッフ管理
- 相談支援専門員の登録・編集・削除
- ログイン認証(ユーザー名・パスワード)
- アクセス権限設定(管理者/一般)
- 管理者: すべての機能にアクセス可能
- 一般: 自分が担当する利用者の閲覧・編集

#### H. ネットワーク図機能(Phase 3) 🆕
**目的**: 利用者を中心とした支援ネットワークの可視化

**機能**:
- 利用者を中心に、関係機関を配置
- 関係の強度・頻度を線の太さや色で表現
- インタラクティブな操作(ドラッグ、ズーム)
- 図の保存・更新
- PDF出力対応

**技術候補**:
- D3.js: 柔軟性が高く、カスタマイズ可能
- Cytoscape.js: グラフ可視化に特化

#### I. PDF出力機能(Phase 2) 🆕
**用途別のPDF生成**:
1. **ケース会議用資料**
   - 利用者基本情報
   - 支援経過のサマリー
   - ネットワーク図(Phase 3)

2. **家族交付用資料**
   - 本人基本情報(氏名、年齢、手帳情報等)
   - サービス利用計画の概要

3. **相談支援記録**
   - 期間指定での記録出力
   - 担当者別の出力

4. **ネットワーク図**(Phase 3)
   - 支援体制の全体像

**技術**: Docling + ReportLab

---

## 3. 技術選定の理由

### 3.1 データベース: SQLite

#### 選定理由
1. **シンプルさ**: ファイルベースで、サーバー不要
2. **セットアップの容易さ**: インストール不要、すぐに使える
3. **バックアップの簡単さ**: ファイルコピーだけで完了
4. **十分な性能**: 単独事業所(3〜4名の利用)には過剰な性能
5. **プログラミング初心者に優しい**: SQLの基本だけで十分

#### Neo4jではない理由
当初、ネットワーク図の管理を考慮してNeo4j(グラフデータベース)も検討したが、以下の理由で見送り:
- **学習コストが高い**: GraphQLやCypherクエリの学習が必要
- **セットアップが複雑**: 独立したサーバーの起動が必要
- **オーバースペック**: 単純なネットワーク図なら、通常のリレーショナルDBで十分

#### 将来的な移行パス
設計上、将来的な移行を考慮:
- **PostgreSQL**: 複数事業所対応時、または大量データ時
- **Neo4j**: 本格的なネットワーク分析機能を追加する場合

現在のSQLite設計でも、データ構造を適切に設計すれば移行は可能。

### 3.2 Webフレームワーク: FastAPI

#### 選定理由
1. **高速**: 非同期処理に対応、軽量
2. **型安全**: Pythonの型ヒントを活用
3. **自動ドキュメント**: Swagger UIが自動生成される
4. **学習しやすい**: Pythonの基本が分かれば理解できる
5. **日本語ドキュメント**: 公式に日本語ドキュメントあり

#### 他の選択肢との比較
- **Django**: 高機能だが、重厚で学習コストが高い
- **Flask**: シンプルだが、型安全性が低い

### 3.3 フロントエンド: Bootstrap 5

#### 選定理由
1. **レスポンシブデザイン**: PC・タブレット自動対応
2. **既製コンポーネント**: ボタン、フォーム、モーダル等が豊富
3. **カスタマイズ可能**: 必要に応じてスタイル変更可能
4. **学習リソース豊富**: 日本語の情報も多い

#### 他の選択肢との比較
- **React/Vue.js**: 高度だが、JavaScriptフレームワークの学習が必要
- **Tailwind CSS**: カスタマイズ性は高いが、Bootstrap の方が初心者向け

### 3.4 PDF生成: Docling

#### 選定理由
1. **高品質**: 複雑なレイアウトに対応
2. **日本語対応**: 問題なく日本語PDF生成可能
3. **柔軟性**: カスタムテンプレート作成可能
4. **MCP統合**: DoclingのMCPサーバーが利用可能

#### 補助ツール: ReportLab
シンプルな帳票生成にはReportLabも併用可能。

---

## 4. データベース設計方針

### 4.1 主要テーブル設計

#### users (利用者テーブル)
```
id: INTEGER PRIMARY KEY
name: TEXT NOT NULL (氏名)
name_kana: TEXT (氏名カナ)
birth_date: DATE NOT NULL (生年月日)
gender: TEXT (性別: 男性/女性/その他)
postal_code: TEXT (郵便番号)
address: TEXT (住所)
phone: TEXT (電話番号)
email: TEXT (メールアドレス)
emergency_contact_name: TEXT (緊急連絡先氏名)
emergency_contact_phone: TEXT (緊急連絡先電話)
disability_support_level: INTEGER (障害支援区分: 1-6)
disability_support_certified_date: DATE (区分認定日)
disability_support_expiry_date: DATE (区分有効期限)
guardian_type: TEXT (後見制度種別: 後見/保佐/補助)
guardian_name: TEXT (後見人等氏名)
guardian_contact: TEXT (後見人等連絡先)
assigned_staff_id: INTEGER (担当職員ID - FOREIGN KEY)
created_at: DATETIME
updated_at: DATETIME
```

#### notebooks (手帳テーブル)
**理由**: 1人が複数の手帳を持つ可能性があるため、別テーブル化
```
id: INTEGER PRIMARY KEY
user_id: INTEGER NOT NULL (FOREIGN KEY to users)
notebook_type: TEXT NOT NULL (種別: 療育手帳/精神障害者保健福祉手帳)
grade: TEXT (等級)
issue_date: DATE (交付日)
renewal_date: DATE (更新日)
notes: TEXT (備考)
created_at: DATETIME
updated_at: DATETIME
```

#### consultations (相談記録テーブル)
```
id: INTEGER PRIMARY KEY
user_id: INTEGER NOT NULL (FOREIGN KEY to users)
staff_id: INTEGER NOT NULL (対応職員ID - FOREIGN KEY to staff)
consultation_date: DATETIME NOT NULL (相談日時)
consultation_type: TEXT (相談形態: 来所/訪問/電話/その他)
content: TEXT (相談内容)
response: TEXT (対応内容)
created_at: DATETIME
updated_at: DATETIME
```

#### organizations (関係機関テーブル)
```
id: INTEGER PRIMARY KEY
name: TEXT NOT NULL (機関名)
type: TEXT NOT NULL (種別: サービス事業所/医療機関/後見人/その他)
postal_code: TEXT (郵便番号)
address: TEXT (住所)
phone: TEXT (電話番号)
fax: TEXT (FAX番号)
email: TEXT (メールアドレス)
contact_person: TEXT (担当者名)
contact_person_phone: TEXT (担当者電話)
notes: TEXT (メモ)
created_at: DATETIME
updated_at: DATETIME
```

#### user_organizations (利用者-関係機関 中間テーブル)
**理由**: 多対多のリレーションシップを表現
```
id: INTEGER PRIMARY KEY
user_id: INTEGER NOT NULL (FOREIGN KEY to users)
organization_id: INTEGER NOT NULL (FOREIGN KEY to organizations)
relationship_type: TEXT (関係性: 主治医/通所先/後見人/その他)
start_date: DATE (関係開始日)
end_date: DATE (関係終了日 - NULLの場合は現在も継続)
frequency: TEXT (頻度: 毎日/週1回/月1回/その他)
notes: TEXT (メモ)
created_at: DATETIME
updated_at: DATETIME
```

#### staff (職員テーブル)
```
id: INTEGER PRIMARY KEY
username: TEXT UNIQUE NOT NULL (ログインID)
password_hash: TEXT NOT NULL (パスワードハッシュ)
name: TEXT NOT NULL (氏名)
role: TEXT NOT NULL (権限: admin/staff)
email: TEXT (メールアドレス)
is_active: BOOLEAN DEFAULT TRUE (有効/無効)
created_at: DATETIME
updated_at: DATETIME
```

#### plans (サービス利用計画テーブル - Phase 2)
```
id: INTEGER PRIMARY KEY
user_id: INTEGER NOT NULL (FOREIGN KEY to users)
created_by_staff_id: INTEGER NOT NULL (作成者ID - FOREIGN KEY to staff)
plan_date: DATE NOT NULL (計画作成日)
start_date: DATE NOT NULL (計画開始日)
end_date: DATE NOT NULL (計画終了日)
user_wishes: TEXT (本人の意向)
family_wishes: TEXT (家族の意向)
goals: TEXT (支援目標)
created_at: DATETIME
updated_at: DATETIME
```

#### monitoring (モニタリング記録テーブル - Phase 2)
```
id: INTEGER PRIMARY KEY
plan_id: INTEGER NOT NULL (FOREIGN KEY to plans)
staff_id: INTEGER NOT NULL (実施者ID - FOREIGN KEY to staff)
monitoring_date: DATE NOT NULL (実施日)
service_status: TEXT (サービス利用状況)
goal_achievement: TEXT (目標達成状況)
issues: TEXT (課題)
future_direction: TEXT (今後の方針)
created_at: DATETIME
updated_at: DATETIME
```

### 4.2 ER図の概要

```
users (利用者)
  ├── 1:N → notebooks (手帳)
  ├── 1:N → consultations (相談記録)
  ├── 1:N → plans (計画)
  ├── N:1 → staff (担当職員)
  └── N:M → organizations (関係機関) via user_organizations

staff (職員)
  ├── 1:N → users (担当利用者)
  ├── 1:N → consultations (対応記録)
  └── 1:N → plans (作成計画)

plans (計画)
  └── 1:N → monitoring (モニタリング)

organizations (関係機関)
  └── N:M → users (利用者) via user_organizations
```

### 4.3 インデックス設計

パフォーマンス向上のため、以下のインデックスを作成:
```sql
-- 利用者検索の高速化
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_birth_date ON users(birth_date);
CREATE INDEX idx_users_assigned_staff_id ON users(assigned_staff_id);

-- 相談記録検索の高速化
CREATE INDEX idx_consultations_user_id ON consultations(user_id);
CREATE INDEX idx_consultations_date ON consultations(consultation_date);
CREATE INDEX idx_consultations_staff_id ON consultations(staff_id);

-- 関係機関検索の高速化
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_type ON organizations(type);

-- 中間テーブル検索の高速化
CREATE INDEX idx_user_organizations_user_id ON user_organizations(user_id);
CREATE INDEX idx_user_organizations_org_id ON user_organizations(organization_id);
```

---

## 5. 開発フェーズと優先順位

### Phase 1: 基本機能(MVP) - 最優先 🎯
**目的**: 最小限の機能で動作するシステムを構築

**タスク**:
1. プロジェクト構造の構築
   - ディレクトリ作成
   - requirements.txt作成
   - 基本設定ファイル作成

2. データベースセットアップ
   - SQLAlchemyモデル定義(users, staff, consultations, organizations, notebooks)
   - マイグレーションスクリプト作成
   - 初期データ投入スクリプト

3. 認証機能
   - ログイン/ログアウト
   - セッション管理
   - 権限チェック

4. 利用者管理機能
   - 一覧表示(検索・フィルタリング)
   - 詳細表示
   - 新規登録
   - 編集
   - 削除(論理削除)
   - **年齢自動計算の実装**

5. 手帳情報管理
   - 手帳の登録・編集・削除
   - 複数手帳の管理

6. 相談記録管理
   - 記録の登録・編集・削除
   - 一覧表示

7. 関係機関管理
   - 機関の登録・編集・削除
   - 一覧表示
   - 利用者との紐付け

8. スタッフ管理
   - スタッフの登録・編集・削除
   - 権限設定

**完了基準**:
- 利用者情報の登録・閲覧・編集ができる
- 相談記録を記録できる
- 関係機関を管理できる
- スタッフ間で情報共有ができる

---

### Phase 2: 計画・記録機能 ✅ **完了**
**目的**: サービス利用計画とモニタリング機能の追加

**タスク**:
1. ✅ サービス利用計画管理
   - ✅ 計画の作成・編集・削除
   - ✅ 計画一覧表示（利用者名・スタッフ名の並行取得、ステータスバッジ表示）
   - ✅ 計画詳細表示（基本情報、利用者の状況、援助方針と目標）
   - ✅ 計画PDF出力（`/api/plans/{plan_id}/pdf`）

2. ✅ モニタリング記録管理
   - ✅ モニタリング記録の作成・編集・削除
   - ✅ 記録一覧表示（期限超過の警告表示付き）
   - ✅ 記録詳細表示（モニタリング内容、課題と今後の方針）
   - ✅ モニタリングPDF出力（`/api/monitorings/{monitoring_id}/pdf`）

3. ✅ 基本的なPDF出力
   - ✅ 利用者基本情報のPDF化（既存機能）
   - ✅ サービス利用計画のPDF化
   - ✅ モニタリング記録のPDF化
   - ✅ 相談記録のPDF化（`/api/consultations/{consultation_id}/pdf`）

**実装詳細**:
- **PDFService**: ReportLabを使用した日本語PDF生成
  - `generate_plan_pdf()`: 計画書PDF生成
  - `generate_monitoring_pdf()`: モニタリング記録PDF生成
  - `generate_consultation_pdf()`: 相談記録PDF生成
- **APIエンドポイント**: すべてのPDFダウンロードエンドポイント実装済み
- **フロントエンド**: 一覧・詳細ページでの名前表示、ステータスバッジ、PDF出力ボタン実装

**完了基準**: ✅ すべて達成
- ✅ 計画とモニタリングが管理できる
- ✅ 必要な資料をPDFで出力できる

**完了日**: 2025年10月24日

---

### Phase 3: 可視化・高度機能
**目的**: ネットワーク図と高度な分析機能の追加

**タスク**:
1. ネットワーク図機能
   - D3.jsまたはCytoscape.jsの導入
   - 利用者-関係機関のネットワーク可視化
   - インタラクティブ操作
   - 図の保存

2. ネットワーク図のPDF出力
   - SVG→PDF変換
   - レイアウト調整

3. 高度な検索・分析
   - 複合条件検索
   - 統計情報の表示(担当者別の利用者数等)
   - ダッシュボード機能

**完了基準**:
- 支援ネットワークが視覚的に理解できる
- 高度な検索・分析ができる

---

### Phase 4: 将来の拡張
**目的**: さらなる利便性向上

**タスク**:
1. 過去データのインポート
   - ExcelからのCSVインポート
   - データ検証機能

2. 外部システム連携
   - 他システムとのAPI連携(必要に応じて)

3. 通知機能
   - 手帳更新期限の通知
   - モニタリング実施期限の通知

**完了基準**:
- 過去データを移行できる
- 業務効率がさらに向上する

---

## 6. 重要な設計決定事項

### 6.1 年齢の自動計算
**要件**: 生年月日から現在の年齢を自動計算して表示

**実装方法**:
1. データベースには生年月日のみを保存
2. 表示時に動的に年齢を計算
3. Pythonの`datetime`モジュールを使用

```python
from datetime import date

def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age
```

4. テンプレートで表示: `{{ user.age }}歳`

### 6.2 手帳情報の管理
**要件**: 1人の利用者が複数の手帳(療育手帳+精神障害者保健福祉手帳)を持つ可能性

**実装方法**:
- `notebooks`テーブルを別途作成
- `user_id`で紐付け
- 1人の利用者に対して複数のレコードを持つ

**画面表示**:
- 利用者詳細画面に「手帳情報」セクション
- 手帳の一覧表示
- 追加・編集・削除ボタン

### 6.3 成年後見人の管理
**要件**: 成年後見人(保佐人・補助人含む)を関係機関として管理

**実装方法**:
1. 利用者テーブルに`guardian_type`, `guardian_name`, `guardian_contact`を持たせる(基本情報として)
2. 関係機関テーブルにも後見人を登録可能(詳細情報として)
3. 関係機関タイプに「後見人」を追加

**理由**: 基本情報として必要な場合と、詳細な事務所情報が必要な場合の両方に対応

### 6.4 データの論理削除
**要件**: データを実際には削除せず、無効化する

**実装方法**:
- 各テーブルに`is_deleted`フィールドを追加(BooleanまたはDATE型)
- 削除時は`is_deleted = TRUE`に変更
- 通常の検索では`is_deleted = FALSE`のみを表示

**理由**: 監査証跡、データ復旧の可能性を残すため

### 6.5 セキュリティ
**パスワード管理**:
- `passlib`ライブラリを使用したハッシュ化
- bcryptアルゴリズムを推奨

**セッション管理**:
- FastAPIの`SessionMiddleware`を使用
- タイムアウト設定(30分無操作でログアウト)

**SQLインジェクション対策**:
- SQLAlchemyのORM機能を使用することで自動的に対策

---

## 7. 次のステップ

### 7.1 Phase 1の開発開始
以下の順序で開発を進めることを推奨:

#### Step 1: プロジェクトセットアップ
- [ ] ディレクトリ構造の作成
- [ ] `requirements.txt`の作成
- [ ] 仮想環境のセットアップ
- [ ] `.gitignore`の作成
- [ ] FastAPIの基本設定

#### Step 2: データベース構築
- [ ] SQLAlchemyモデルの定義
  - User, Staff, Consultation, Organization, Notebook, UserOrganization
- [ ] `database/connection.py`の作成
- [ ] マイグレーションスクリプト(`scripts/init_db.py`)
- [ ] シードデータ作成(`scripts/seed_data.py`)

#### Step 3: 認証機能
- [ ] ログイン画面の作成
- [ ] 認証APIの実装
- [ ] セッション管理
- [ ] 権限チェックのデコレーター

#### Step 4: 利用者管理機能
- [ ] 利用者一覧画面
- [ ] 利用者詳細画面
- [ ] 利用者登録画面
- [ ] 利用者編集画面
- [ ] 年齢自動計算の実装
- [ ] 検索・フィルタリング機能

#### Step 5: 手帳管理機能
- [ ] 手帳登録・編集画面
- [ ] 手帳一覧表示
- [ ] 複数手帳対応

#### Step 6: 相談記録管理
- [ ] 相談記録登録画面
- [ ] 相談記録一覧画面
- [ ] 相談記録詳細画面

#### Step 7: 関係機関管理
- [ ] 関係機関登録画面
- [ ] 関係機関一覧画面
- [ ] 利用者との紐付け機能

#### Step 8: スタッフ管理
- [ ] スタッフ登録・編集画面
- [ ] 権限設定機能

### 7.2 開発環境の準備

**重要**: このプロジェクトでは、依存関係の問題を回避するために **uv** を使用します。

#### uvのインストール
```bash
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# または Homebrew:
brew install uv

# インストール確認
uv --version
```

#### プロジェクトセットアップ
```bash
# プロジェクトディレクトリに移動
cd ~/AI-Workspace/keikaku-sodan-app

# uvで仮想環境を作成（.venvディレクトリが作成される）
uv venv

# 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux
# または .venv\Scripts\activate  # Windows

# 必要なパッケージをインストール（requirements.txtを先に作成）
uv pip install -r requirements.txt

# データベースの初期化
python scripts/init_db.py

# 開発サーバーの起動
uv run uvicorn app.main:app --reload
# または仮想環境有効化済みの場合:
# uvicorn app.main:app --reload
```

#### uvを使う理由
- **高速**: Rust製で、従来のpipより10-100倍高速
- **依存関係の正確な解決**: 複雑な依存関係も確実に解決
- **再現性**: ロックファイルで環境を完全に再現可能
- **バージョン競合の回避**: プログラミング初心者でも安心

### 7.3 最初に作成すべきファイル

1. **requirements.txt** (uvで管理する場合も互換性のため作成)
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
jinja2>=3.1.0
python-jose[cryptography]>=3.3.0
```

**注意**: uvを使う場合、バージョンは柔軟に `>=` で指定することを推奨。uvが最適なバージョンを自動選択します。

または、**pyproject.toml**（uvの推奨方式）:
```toml
[project]
name = "keikaku-sodan-app"
version = "0.1.0"
description = "計画相談支援 利用者管理システム"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
    "jinja2>=3.1.0",
    "python-jose[cryptography]>=3.3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

pyproject.tomlを使う場合のインストール:
```bash
uv pip install -e .
```

2. **app/main.py** (FastAPIエントリーポイント)
3. **app/database/connection.py** (DB接続)
4. **app/models/** (各種モデル)
5. **scripts/init_db.py** (DB初期化スクリプト)

---

## 8. 注意事項

### 8.1 プログラミング初心者向けの配慮
- **uvの使用**: 依存関係の問題を最小限に抑えるため、uvを使用
  - uvは従来のpipより高速で、依存関係の競合を自動解決
  - コマンドはシンプルで初心者にも分かりやすい
- コードには日本語コメントを豊富に記載
- 関数・クラスには詳細なドキュメント文字列
- 複雑なロジックは段階的に実装
- エラーメッセージは分かりやすく日本語で

### 8.2 個人情報の取り扱い
- 開発時はダミーデータを使用
- 実際の利用者情報は使わない
- テストデータにも注意

### 8.3 バックアップ
- 定期的なデータベースバックアップの仕組みを実装
- `scripts/backup_db.py`を作成予定

### 8.4 ドキュメント
- コードと同時にドキュメントも更新
- 変更があれば`CLAUDE.md`と`HANDOVER.md`も更新

### 8.5 テスト
- 各機能の実装後、動作確認を徹底
- 可能な限り自動テストも作成

---

## 9. 質問・確認事項

開発を進める中で、以下の点を確認してください:

### 9.1 UI/UX
- 画面のレイアウトやデザインの好み
- ボタンの配置や色
- 一覧表示の項目数(ページング)

### 9.2 業務フロー
- 実際の業務の流れに沿った画面遷移
- 入力項目の必須/任意の区別
- デフォルト値の設定

### 9.3 運用
- バックアップの頻度
- データ保持期間
- アクセスログの記録

---

## 10. まとめ

このプロジェクトは、計画相談支援事業所の業務効率化を目指し、以下を実現します:

✅ 紙ベース管理からの脱却  
✅ 利用者情報の一元管理  
✅ スタッフ間の情報共有  
✅ 支援履歴の可視化  
✅ ネットワーク図による支援体制の見える化  
✅ PDF出力によるケース会議・家族交付対応

Phase 1から段階的に開発を進め、確実に動作するシステムを構築していきましょう。

**開発の成功を祈っています!**

---

**最終更新**: 2025年10月24日  
**次回更新予定**: Phase 1完了後
