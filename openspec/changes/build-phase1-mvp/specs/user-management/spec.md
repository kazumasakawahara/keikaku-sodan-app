# User Management Capability Specification

## ADDED Requirements

### Requirement: User CRUD Operations
システムは、利用者情報の作成、読取、更新、削除（CRUD）機能を提供しなければならない（MUST）。

#### Scenario: Create new user
- **WHEN** 必須項目（氏名、生年月日、担当職員）を入力して登録ボタンをクリックした
- **THEN** システムは新しい利用者レコードをデータベースに保存する
- **AND** 利用者詳細画面にリダイレクトする
- **AND** 成功メッセージ「利用者情報を登録しました」を表示する

#### Scenario: View user list
- **WHEN** 利用者一覧画面にアクセスした
- **THEN** システムは削除されていない（`is_deleted=False`）利用者の一覧を表示する
- **AND** 各利用者の氏名、年齢、担当者、最終相談日を表示する

#### Scenario: View user details
- **WHEN** 利用者一覧から「詳細」ボタンをクリックした
- **THEN** システムは選択された利用者の詳細情報を表示する
- **AND** 基本情報、手帳情報、相談記録、関係機関のタブを表示する

#### Scenario: Update user information
- **WHEN** 利用者情報を編集して更新ボタンをクリックした
- **THEN** システムは変更内容をデータベースに保存する
- **AND** `updated_at`タイムスタンプを更新する
- **AND** 成功メッセージ「利用者情報を更新しました」を表示する

#### Scenario: Delete user (logical deletion)
- **WHEN** 利用者削除ボタンをクリックして確認ダイアログで「はい」を選択した
- **THEN** システムは`is_deleted=True`に設定する（物理削除はしない）
- **AND** 利用者一覧から該当利用者が非表示になる
- **AND** 成功メッセージ「利用者情報を削除しました」を表示する

### Requirement: Automatic Age Calculation
システムは、生年月日から現在の年齢を自動計算して表示しなければならない（MUST）。

#### Scenario: Display current age
- **WHEN** 利用者情報を表示する
- **THEN** システムは生年月日から現在の年齢を計算する
- **AND** 計算された年齢を「XX歳」の形式で表示する

#### Scenario: Age calculation logic
- **WHEN** 本日が誕生日を過ぎている
- **THEN** システムは「今年 - 生年」を年齢とする
- **WHEN** 本日が誕生日前である
- **THEN** システムは「今年 - 生年 - 1」を年齢とする

### Requirement: Notebook Management
システムは、利用者の手帳情報（療育手帳、精神障害者保健福祉手帳）を管理しなければならない（MUST）。

#### Scenario: Add notebook
- **WHEN** 手帳情報タブで「手帳を追加」ボタンをクリックし、手帳情報を入力して登録した
- **THEN** システムは新しい手帳レコードを作成する
- **AND** 利用者IDと紐付ける
- **AND** 手帳情報一覧に追加された手帳が表示される

#### Scenario: Multiple notebooks
- **WHEN** 利用者が療育手帳と精神障害者保健福祉手帳の両方を所持している
- **THEN** システムは両方の手帳情報を別々のレコードとして保存する
- **AND** 手帳情報タブに両方の手帳が表示される

#### Scenario: Update notebook
- **WHEN** 手帳の更新日や等級を変更して保存した
- **THEN** システムは該当する手帳レコードを更新する
- **AND** 成功メッセージを表示する

#### Scenario: Delete notebook
- **WHEN** 手帳の削除ボタンをクリックして確認した
- **THEN** システムは該当する手帳レコードを論理削除する
- **AND** 手帳情報一覧から削除された手帳が非表示になる

### Requirement: Guardian Information Management
システムは、成年後見制度の利用情報を管理しなければならない（MUST）。

#### Scenario: Register guardian information
- **WHEN** 成年後見制度の「利用有無:あり」を選択し、種別（後見/保佐/補助）と後見人情報を入力した
- **THEN** システムは後見人情報を利用者レコードに保存する
- **AND** 後見人氏名、連絡先、種別が保存される

#### Scenario: No guardian
- **WHEN** 成年後見制度の「利用有無:なし」を選択した
- **THEN** システムは後見人関連フィールドを空（NULL）にする

### Requirement: Search and Filter
システムは、利用者の検索およびフィルタリング機能を提供しなければならない（MUST）。

#### Scenario: Search by name
- **WHEN** 検索欄に氏名の一部を入力して検索ボタンをクリックした
- **THEN** システムは氏名（`name`）または氏名カナ（`name_kana`）に検索キーワードを含む利用者を表示する
- **AND** 部分一致検索を行う（「佐藤」で「佐藤花子」がヒット）

#### Scenario: Filter by staff
- **WHEN** 担当者フィルターで特定のスタッフを選択した
- **THEN** システムは選択されたスタッフが担当する利用者のみを表示する

#### Scenario: Filter by disability support level
- **WHEN** 障害支援区分フィルターで特定の区分を選択した
- **THEN** システムは選択された障害支援区分の利用者のみを表示する

#### Scenario: Combined filters
- **WHEN** 複数のフィルター（担当者、障害支援区分）を同時に適用した
- **THEN** システムはすべての条件に一致する利用者のみを表示する（AND条件）

### Requirement: User List Pagination
システムは、利用者一覧のページング機能を提供しなければならない（MUST）。

#### Scenario: Default page size
- **WHEN** 利用者一覧画面を表示した
- **THEN** システムは1ページあたり50件の利用者を表示する
- **AND** ページネーションコントロール（前へ、次へ、ページ番号）を表示する

#### Scenario: Navigate pages
- **WHEN** ページネーションの「次へ」ボタンをクリックした
- **THEN** システムは次の50件の利用者を表示する

### Requirement: User Data Validation
システムは、利用者情報の入力データを検証しなければならない（MUST）。

#### Scenario: Required field validation
- **WHEN** 必須項目（氏名、生年月日、担当職員）が未入力のまま登録ボタンをクリックした
- **THEN** システムはエラーメッセージ「必須項目を入力してください」を表示する
- **AND** 未入力のフィールドを強調表示する

#### Scenario: Birth date validation
- **WHEN** 生年月日に未来の日付を入力した
- **THEN** システムはエラーメッセージ「生年月日に未来の日付は指定できません」を表示する

#### Scenario: Phone number format validation
- **WHEN** 電話番号に数字以外の文字（ハイフンは除く）を入力した
- **THEN** システムはエラーメッセージ「電話番号の形式が正しくありません」を表示する

### Requirement: User Information Display
システムは、利用者情報をタブ形式で整理して表示しなければならない（MUST）。

#### Scenario: Tab navigation
- **WHEN** 利用者詳細画面で「手帳情報」タブをクリックした
- **THEN** システムは手帳情報セクションを表示する
- **AND** 他のタブ（基本情報、相談記録、関係機関）は非表示になる

#### Scenario: Default tab
- **WHEN** 利用者詳細画面を開いた
- **THEN** システムはデフォルトで「基本情報」タブを表示する

### Requirement: Authorization Check for User Access
システムは、ユーザーのアクセス権限を確認しなければならない（MUST）。

#### Scenario: Admin access to all users
- **WHEN** 管理者（`role=admin`）が利用者一覧にアクセスした
- **THEN** システムはすべての利用者を表示する

#### Scenario: Staff access to assigned users only
- **WHEN** 一般スタッフ（`role=staff`）が利用者一覧にアクセスした
- **THEN** システムは自分が担当する利用者（`assigned_staff_id`が自分のID）のみを表示する

#### Scenario: Unauthorized user detail access
- **WHEN** 一般スタッフが他のスタッフの担当利用者の詳細画面にアクセスを試みた
- **THEN** システムは403 Forbiddenエラーを返す
- **AND** エラーメッセージ「この利用者の情報にアクセスする権限がありません」を表示する
