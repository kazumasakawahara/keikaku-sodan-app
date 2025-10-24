# Consultation Records Capability Specification

## ADDED Requirements

### Requirement: Consultation Record CRUD Operations
システムは、相談支援記録の作成、読取、更新、削除（CRUD）機能を提供しなければならない（MUST）。

#### Scenario: Create consultation record
- **WHEN** 利用者、相談日時、相談形態、対応者、相談内容、対応内容を入力して登録ボタンをクリックした
- **THEN** システムは新しい相談記録をデータベースに保存する
- **AND** 相談記録一覧にリダイレクトする
- **AND** 成功メッセージ「相談記録を登録しました」を表示する

#### Scenario: View consultation record list
- **WHEN** 相談記録一覧画面にアクセスした
- **THEN** システムは削除されていない（`is_deleted=False`）相談記録を新しい順に表示する
- **AND** 各記録の相談日時、利用者名、相談形態、対応者を表示する

#### Scenario: View user-specific consultation records
- **WHEN** 利用者詳細画面の「相談記録」タブを表示した
- **THEN** システムは該当利用者の相談記録のみを新しい順に表示する
- **AND** 各記録の概要（日時、対応者、相談内容の冒頭）を表示する

#### Scenario: View consultation record details
- **WHEN** 相談記録の「詳細」ボタンをクリックした
- **THEN** システムは選択された相談記録の詳細情報を表示する
- **AND** 相談日時、利用者名、対応者、相談形態、相談内容、対応内容をすべて表示する

#### Scenario: Update consultation record
- **WHEN** 相談記録を編集して更新ボタンをクリックした
- **THEN** システムは変更内容をデータベースに保存する
- **AND** `updated_at`タイムスタンプを更新する
- **AND** 成功メッセージ「相談記録を更新しました」を表示する

#### Scenario: Delete consultation record
- **WHEN** 相談記録の削除ボタンをクリックして確認ダイアログで「はい」を選択した
- **THEN** システムは`is_deleted=True`に設定する（物理削除はしない）
- **AND** 相談記録一覧から該当記録が非表示になる
- **AND** 成功メッセージ「相談記録を削除しました」を表示する

### Requirement: Consultation Type Management
システムは、相談形態（来所/訪問/電話/その他）を管理しなければならない（MUST）。

#### Scenario: Select consultation type
- **WHEN** 相談記録登録画面で相談形態を選択した
- **THEN** システムは選択された相談形態（来所/訪問/電話/その他）を保存する

#### Scenario: Display consultation type
- **WHEN** 相談記録一覧を表示する
- **THEN** システムは各記録の相談形態をアイコンまたはラベルで表示する
- **AND** 来所: 🏢、訪問: 🏠、電話: 📞、その他: 📝 のように視覚的に区別する

### Requirement: Consultation Date and Time Management
システムは、相談日時を正確に記録しなければならない（MUST）。

#### Scenario: Record consultation datetime
- **WHEN** 相談記録登録時に日付と時刻を入力した
- **THEN** システムは相談日時を`DATETIME`形式で保存する

#### Scenario: Default datetime
- **WHEN** 相談記録登録画面を開いた
- **THEN** システムは現在の日時をデフォルト値として表示する

#### Scenario: Display consultation datetime
- **WHEN** 相談記録を表示する
- **THEN** システムは相談日時を「YYYY/MM/DD HH:MM」形式で表示する

### Requirement: Staff Assignment
システムは、相談記録に対応者（スタッフ）を紐付けなければならない（MUST）。

#### Scenario: Assign staff to consultation
- **WHEN** 相談記録登録時に対応者を選択した
- **THEN** システムは選択されたスタッフIDを`staff_id`に保存する

#### Scenario: Default staff assignment
- **WHEN** 相談記録登録画面を開いた
- **THEN** システムは現在ログイン中のスタッフをデフォルトの対応者として選択する

### Requirement: Consultation Content Management
システムは、相談内容と対応内容を分けて管理しなければならない（MUST）。

#### Scenario: Record consultation content
- **WHEN** 相談内容欄にテキストを入力した
- **THEN** システムは相談内容を`content`フィールドに保存する
- **AND** 改行やフォーマットを保持する

#### Scenario: Record response content
- **WHEN** 対応内容欄にテキストを入力した
- **THEN** システムは対応内容を`response`フィールドに保存する
- **AND** 改行やフォーマットを保持する

#### Scenario: Display consultation and response
- **WHEN** 相談記録詳細を表示する
- **THEN** システムは相談内容と対応内容を明確に区別して表示する
- **AND** 「【相談内容】」「【対応内容】」のようにラベルを付ける

### Requirement: Consultation Record Filtering
システムは、相談記録のフィルタリング機能を提供しなければならない（MUST）。

#### Scenario: Filter by period
- **WHEN** 期間フィルターで「過去1ヶ月」を選択した
- **THEN** システムは過去1ヶ月以内の相談記録のみを表示する

#### Scenario: Filter by consultation type
- **WHEN** 相談形態フィルターで「訪問」を選択した
- **THEN** システムは相談形態が「訪問」の記録のみを表示する

#### Scenario: Filter by staff
- **WHEN** 対応者フィルターで特定のスタッフを選択した
- **THEN** システムは選択されたスタッフが対応した相談記録のみを表示する

### Requirement: Recent Consultation Display
システムは、最近の相談記録をダッシュボードに表示しなければならない（MUST）。

#### Scenario: Dashboard recent consultations
- **WHEN** ダッシュボードを表示した
- **THEN** システムは最新5件の相談記録を表示する
- **AND** 各記録の日時、利用者名、相談形態を表示する
- **AND** 「詳細」リンクをクリックすると相談記録詳細画面に遷移する

### Requirement: Consultation Record Validation
システムは、相談記録の入力データを検証しなければならない（MUST）。

#### Scenario: Required field validation
- **WHEN** 必須項目（利用者、相談日時、対応者）が未入力のまま登録ボタンをクリックした
- **THEN** システムはエラーメッセージ「必須項目を入力してください」を表示する
- **AND** 未入力のフィールドを強調表示する

#### Scenario: Future datetime validation
- **WHEN** 相談日時に未来の日時を入力した
- **THEN** システムはエラーメッセージ「相談日時に未来の日時は指定できません」を表示する

#### Scenario: Content length validation
- **WHEN** 相談内容または対応内容が空のまま登録しようとした
- **THEN** システムは警告メッセージ「相談内容または対応内容を入力してください」を表示する

### Requirement: Consultation Record Authorization
システムは、相談記録へのアクセス権限を確認しなければならない（MUST）。

#### Scenario: Admin access to all records
- **WHEN** 管理者（`role=admin`）が相談記録一覧にアクセスした
- **THEN** システムはすべての相談記録を表示する

#### Scenario: Staff access to assigned user records
- **WHEN** 一般スタッフ（`role=staff`）が相談記録一覧にアクセスした
- **THEN** システムは自分が担当する利用者の相談記録のみを表示する

#### Scenario: Own consultation records
- **WHEN** 一般スタッフが自分が対応した相談記録を表示する
- **THEN** システムはアクセスを許可する（自分が担当する利用者の記録でなくても）

### Requirement: Consultation Record Timeline
システムは、利用者の相談記録を時系列で表示しなければならない（MUST）。

#### Scenario: Chronological order
- **WHEN** 利用者詳細画面の「相談記録」タブを表示した
- **THEN** システムは相談記録を新しい順（降順）に表示する
- **AND** 各記録の日時が明確に表示される

#### Scenario: Timeline navigation
- **WHEN** 相談記録が多数ある場合
- **THEN** システムは期間フィルターで絞り込みを可能にする
- **AND** ページングまたは無限スクロールで記録を表示する
