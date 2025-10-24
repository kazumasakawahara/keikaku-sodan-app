# Organization Management Capability Specification

## ADDED Requirements

### Requirement: Organization CRUD Operations
システムは、関係機関の作成、読取、更新、削除（CRUD）機能を提供しなければならない（MUST）。

#### Scenario: Create organization
- **WHEN** 機関名、種別を入力して登録ボタンをクリックした
- **THEN** システムは新しい関係機関レコードをデータベースに保存する
- **AND** 関係機関一覧にリダイレクトする
- **AND** 成功メッセージ「関係機関を登録しました」を表示する

#### Scenario: View organization list
- **WHEN** 関係機関一覧画面にアクセスした
- **THEN** システムは削除されていない（`is_deleted=False`）関係機関を表示する
- **AND** 各機関の種別、名称、連絡先を表示する

#### Scenario: View organization details
- **WHEN** 関係機関一覧から「詳細」ボタンをクリックした
- **THEN** システムは選択された関係機関の詳細情報を表示する
- **AND** すべての登録情報（住所、電話、FAX、担当者等）を表示する

#### Scenario: Update organization
- **WHEN** 関係機関情報を編集して更新ボタンをクリックした
- **THEN** システムは変更内容をデータベースに保存する
- **AND** `updated_at`タイムスタンプを更新する
- **AND** 成功メッセージ「関係機関情報を更新しました」を表示する

#### Scenario: Delete organization
- **WHEN** 関係機関の削除ボタンをクリックして確認ダイアログで「はい」を選択した
- **THEN** システムは`is_deleted=True`に設定する（物理削除はしない）
- **AND** 関係機関一覧から該当機関が非表示になる
- **AND** 成功メッセージ「関係機関を削除しました」を表示する

### Requirement: Organization Type Management
システムは、関係機関の種別（サービス事業所/医療機関/後見人/その他）を管理しなければならない（MUST）。

#### Scenario: Select organization type
- **WHEN** 関係機関登録時に種別を選択した
- **THEN** システムは選択された種別を保存する

#### Scenario: Display organization type with icon
- **WHEN** 関係機関一覧を表示する
- **THEN** システムは各機関の種別をアイコンで視覚的に区別する
- **AND** 事業所: 🏢、医療機関: 🏥、後見人: ⚖️、その他: 📋 のように表示する

#### Scenario: Filter by organization type
- **WHEN** 種別フィルターで「医療機関」を選択した
- **THEN** システムは種別が「医療機関」の関係機関のみを表示する

### Requirement: Organization Contact Information
システムは、関係機関の詳細な連絡先情報を管理しなければならない（MUST）。

#### Scenario: Record contact information
- **WHEN** 郵便番号、住所、電話番号、FAX、メールアドレスを入力した
- **THEN** システムはすべての連絡先情報を保存する

#### Scenario: Record contact person
- **WHEN** 担当者名と担当者連絡先を入力した
- **THEN** システムは担当者情報を保存する
- **AND** 関係機関詳細画面で担当者情報を表示する

#### Scenario: Optional fields
- **WHEN** 必須項目（名称、種別）のみを入力して登録した
- **THEN** システムは他の項目を空（NULL）で保存する
- **AND** エラーを表示せずに登録を完了する

### Requirement: User-Organization Relationship
システムは、利用者と関係機関の紐付けを管理しなければならない（MUST）。

#### Scenario: Link organization to user
- **WHEN** 利用者詳細画面の「関係機関」タブで「機関を追加」ボタンをクリックし、機関を選択した
- **THEN** システムは利用者-関係機関の紐付けレコードを作成する
- **AND** 関係性の種別（主治医/通所先/後見人/その他）を記録する
- **AND** 利用者の関係機関一覧に追加された機関が表示される

#### Scenario: Record relationship type
- **WHEN** 利用者と関係機関を紐付ける際に関係性の種別を選択した
- **THEN** システムは関係性の種別を`relationship_type`フィールドに保存する

#### Scenario: Record relationship period
- **WHEN** 関係開始日を入力した
- **THEN** システムは開始日を`start_date`に保存する
- **AND** 終了日が未入力の場合は`end_date`をNULLにする（現在も継続中）

#### Scenario: End relationship
- **WHEN** 利用者と関係機関の紐付けを解除した
- **THEN** システムは`end_date`に現在日時を設定する
- **AND** 関係機関一覧で「終了」のラベルを表示する

#### Scenario: Unlink organization from user
- **WHEN** 利用者の関係機関一覧から「削除」ボタンをクリックした
- **THEN** システムは利用者-関係機関の紐付けレコードを論理削除する
- **AND** 利用者の関係機関一覧から削除された機関が非表示になる

### Requirement: Organization Frequency Information
システムは、利用者と関係機関の関わり頻度を記録しなければならない（MUST）。

#### Scenario: Record frequency
- **WHEN** 利用者と関係機関を紐付ける際に頻度（毎日/週1回/月1回/その他）を選択した
- **THEN** システムは頻度情報を`frequency`フィールドに保存する

#### Scenario: Display frequency
- **WHEN** 利用者の関係機関一覧を表示する
- **THEN** システムは各機関との関わり頻度を表示する

### Requirement: Organization Search and Filter
システムは、関係機関の検索およびフィルタリング機能を提供しなければならない（MUST）。

#### Scenario: Search by name
- **WHEN** 検索欄に機関名の一部を入力して検索ボタンをクリックした
- **THEN** システムは機関名（`name`）に検索キーワードを含む関係機関を表示する
- **AND** 部分一致検索を行う

#### Scenario: Filter by type
- **WHEN** 種別フィルターで特定の種別を選択した
- **THEN** システムは選択された種別の関係機関のみを表示する

### Requirement: User Organization List Display
システムは、利用者詳細画面で関連する関係機関を表示しなければならない（MUST）。

#### Scenario: Display user organizations
- **WHEN** 利用者詳細画面の「関係機関」タブを表示した
- **THEN** システムは該当利用者に紐付けられた関係機関の一覧を表示する
- **AND** 各機関の名称、種別、関係性、頻度を表示する

#### Scenario: Active relationships only
- **WHEN** 関係機関一覧を表示する
- **THEN** システムは終了していない（`end_date IS NULL`）関係のみをデフォルトで表示する
- **AND** 「終了した関係も表示」オプションで過去の関係も表示できる

### Requirement: Organization Data Validation
システムは、関係機関情報の入力データを検証しなければならない（MUST）。

#### Scenario: Required field validation
- **WHEN** 必須項目（名称、種別）が未入力のまま登録ボタンをクリックした
- **THEN** システムはエラーメッセージ「必須項目を入力してください」を表示する
- **AND** 未入力のフィールドを強調表示する

#### Scenario: Phone number format validation
- **WHEN** 電話番号に数字以外の文字（ハイフンは除く）を入力した
- **THEN** システムはエラーメッセージ「電話番号の形式が正しくありません」を表示する

#### Scenario: Email format validation
- **WHEN** メールアドレスに無効な形式を入力した
- **THEN** システムはエラーメッセージ「メールアドレスの形式が正しくありません」を表示する

### Requirement: Organization Notes
システムは、関係機関に関するメモを保存できなければならない（MUST）。

#### Scenario: Save organization notes
- **WHEN** メモ欄にテキストを入力して保存した
- **THEN** システムはメモを`notes`フィールドに保存する
- **AND** 改行やフォーマットを保持する

#### Scenario: Display organization notes
- **WHEN** 関係機関詳細を表示する
- **THEN** システムは保存されたメモを表示する

### Requirement: Guardian as Organization
システムは、成年後見人を関係機関として登録できなければならない（MUST）。

#### Scenario: Register guardian as organization
- **WHEN** 種別「後見人」で関係機関を登録した
- **THEN** システムは後見人情報を関係機関として保存する
- **AND** 後見人の事務所情報（法律事務所など）も登録できる

#### Scenario: Link guardian to user
- **WHEN** 利用者に後見人を紐付ける際、関係性の種別「後見人」を選択した
- **THEN** システムは利用者-後見人の関係を記録する
- **AND** 利用者基本情報の後見人欄にも反映される
