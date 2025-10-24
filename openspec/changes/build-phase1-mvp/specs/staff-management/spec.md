# Staff Management Capability Specification

## ADDED Requirements

### Requirement: Staff CRUD Operations
システムは、スタッフ（相談支援専門員）の作成、読取、更新、削除機能を提供しなければならない（MUST）。

#### Scenario: Create staff
- **WHEN** ユーザー名、パスワード、氏名、権限を入力して登録ボタンをクリックした
- **THEN** システムは新しいスタッフレコードをデータベースに保存する
- **AND** パスワードをbcryptでハッシュ化して保存する
- **AND** スタッフ一覧にリダイレクトする
- **AND** 成功メッセージ「スタッフを登録しました」を表示する

#### Scenario: View staff list
- **WHEN** スタッフ一覧画面にアクセスした
- **THEN** システムはすべてのスタッフ（有効・無効含む）を表示する
- **AND** 各スタッフのユーザー名、氏名、権限、状態（有効/無効）を表示する

#### Scenario: View staff details
- **WHEN** スタッフ一覧から「詳細」ボタンをクリックした
- **THEN** システムは選択されたスタッフの詳細情報を表示する
- **AND** パスワードは表示しない（セキュリティのため）

#### Scenario: Update staff information
- **WHEN** スタッフ情報を編集して更新ボタンをクリックした
- **THEN** システムは変更内容をデータベースに保存する
- **AND** パスワードが変更された場合のみ、新しいパスワードをハッシュ化して保存する
- **AND** `updated_at`タイムスタンプを更新する
- **AND** 成功メッセージ「スタッフ情報を更新しました」を表示する

#### Scenario: Deactivate staff
- **WHEN** スタッフの「無効化」ボタンをクリックした
- **THEN** システムは`is_active=False`に設定する
- **AND** 該当スタッフはログインできなくなる
- **AND** スタッフ一覧で「無効」のラベルが表示される

#### Scenario: Reactivate staff
- **WHEN** 無効化されたスタッフの「再有効化」ボタンをクリックした
- **THEN** システムは`is_active=True`に設定する
- **AND** 該当スタッフは再度ログインできるようになる

### Requirement: Staff Role Management
システムは、スタッフの権限（管理者/一般）を管理しなければならない（MUST）。

#### Scenario: Assign admin role
- **WHEN** スタッフ登録時に権限「管理者」を選択した
- **THEN** システムは`role=admin`を設定する
- **AND** 該当スタッフはすべての機能にアクセスできる

#### Scenario: Assign staff role
- **WHEN** スタッフ登録時に権限「一般」を選択した
- **THEN** システムは`role=staff`を設定する
- **AND** 該当スタッフは自分が担当する利用者のみアクセスできる

#### Scenario: Change staff role
- **WHEN** 管理者がスタッフの権限を「一般」から「管理者」に変更した
- **THEN** システムは`role`を更新する
- **AND** 該当スタッフの権限が即座に反映される

### Requirement: Staff Username Uniqueness
システムは、スタッフのユーザー名の一意性を保証しなければならない（MUST）。

#### Scenario: Unique username validation
- **WHEN** 既存のユーザー名と同じユーザー名でスタッフを登録しようとした
- **THEN** システムはエラーメッセージ「このユーザー名は既に使用されています」を表示する
- **AND** 登録を拒否する

#### Scenario: Username case sensitivity
- **WHEN** 既存のユーザー名と大文字小文字が異なる同じユーザー名で登録しようとした
- **THEN** システムは大文字小文字を区別せずに重複をチェックする
- **AND** 重複している場合はエラーを表示する

### Requirement: Staff Password Management
システムは、スタッフのパスワードを安全に管理しなければならない（MUST）。

#### Scenario: Password hashing on creation
- **WHEN** 新しいスタッフを登録した
- **THEN** システムはbcryptアルゴリズムでパスワードをハッシュ化する
- **AND** ハッシュ化されたパスワードのみをデータベースに保存する

#### Scenario: Password change
- **WHEN** スタッフのパスワードを変更した
- **THEN** システムは新しいパスワードをハッシュ化して保存する
- **AND** 古いパスワードは使用できなくなる

#### Scenario: Password not displayed
- **WHEN** スタッフ詳細画面を表示する
- **THEN** システムはパスワードを表示しない
- **AND** パスワード欄には「••••••••」のようなマスク表示をする

### Requirement: Staff Data Validation
システムは、スタッフ情報の入力データを検証しなければならない（MUST）。

#### Scenario: Required field validation
- **WHEN** 必須項目（ユーザー名、パスワード、氏名、権限）が未入力のまま登録ボタンをクリックした
- **THEN** システムはエラーメッセージ「必須項目を入力してください」を表示する
- **AND** 未入力のフィールドを強調表示する

#### Scenario: Username format validation
- **WHEN** ユーザー名に使用できない文字（空白、特殊文字）を入力した
- **THEN** システムはエラーメッセージ「ユーザー名は英数字とアンダースコアのみ使用できます」を表示する

#### Scenario: Password strength validation
- **WHEN** パスワードが8文字未満の場合
- **THEN** システムはエラーメッセージ「パスワードは8文字以上で入力してください」を表示する

#### Scenario: Email format validation
- **WHEN** メールアドレスに無効な形式を入力した
- **THEN** システムはエラーメッセージ「メールアドレスの形式が正しくありません」を表示する

### Requirement: Staff Access Control
システムは、スタッフ管理機能へのアクセスを管理者のみに制限しなければならない（MUST）。

#### Scenario: Admin access to staff management
- **WHEN** 管理者（`role=admin`）がスタッフ管理画面にアクセスした
- **THEN** システムはスタッフ一覧を表示する
- **AND** スタッフの登録・編集・無効化機能を提供する

#### Scenario: Staff access denied
- **WHEN** 一般スタッフ（`role=staff`）がスタッフ管理画面にアクセスを試みた
- **THEN** システムは403 Forbiddenエラーを返す
- **AND** エラーメッセージ「この機能を使用する権限がありません」を表示する

### Requirement: Staff Assigned Users
システムは、各スタッフに担当利用者を割り当てなければならない（MUST）。

#### Scenario: View assigned users
- **WHEN** スタッフ詳細画面を表示した
- **THEN** システムは該当スタッフが担当する利用者の一覧を表示する
- **AND** 各利用者の氏名、年齢、最終相談日を表示する

#### Scenario: Count assigned users
- **WHEN** スタッフ一覧を表示する
- **THEN** システムは各スタッフの担当利用者数を表示する

### Requirement: Staff Activity Tracking
システムは、スタッフの活動状況を記録しなければならない（MUST）。

#### Scenario: Track creation timestamp
- **WHEN** 新しいスタッフを登録した
- **THEN** システムは現在日時を`created_at`に記録する

#### Scenario: Track update timestamp
- **WHEN** スタッフ情報を更新した
- **THEN** システムは現在日時を`updated_at`に記録する

### Requirement: Self Profile Management
システムは、スタッフが自分のプロフィール情報を編集できなければならない（MUST）。

#### Scenario: Edit own profile
- **WHEN** ログイン中のスタッフが自分のプロフィール画面にアクセスした
- **THEN** システムは自分の氏名、メールアドレス、パスワードを編集できる画面を表示する
- **AND** ユーザー名と権限は編集できない（管理者のみが変更可能）

#### Scenario: Change own password
- **WHEN** ログイン中のスタッフが自分のパスワードを変更した
- **THEN** システムは新しいパスワードをハッシュ化して保存する
- **AND** 次回ログイン時から新しいパスワードが有効になる

### Requirement: Staff List Display
システムは、スタッフ一覧を分かりやすく表示しなければならない（MUST）。

#### Scenario: Active staff display
- **WHEN** スタッフ一覧画面を表示した
- **THEN** システムは有効なスタッフ（`is_active=True`）を上部に表示する
- **AND** 無効なスタッフは下部にグレーアウトして表示する

#### Scenario: Role indicator
- **WHEN** スタッフ一覧を表示する
- **THEN** システムは各スタッフの権限を明確に表示する
- **AND** 管理者には👑アイコン、一般スタッフには👤アイコンを表示する

### Requirement: Prevent Self Deactivation
システムは、スタッフが自分自身を無効化できないようにしなければならない（MUST）。

#### Scenario: Block self deactivation
- **WHEN** ログイン中のスタッフが自分自身を無効化しようとした
- **THEN** システムはエラーメッセージ「自分自身を無効化することはできません」を表示する
- **AND** 操作を拒否する

#### Scenario: Prevent last admin deactivation
- **WHEN** 最後の有効な管理者を無効化しようとした
- **THEN** システムはエラーメッセージ「最後の管理者を無効化することはできません」を表示する
- **AND** 操作を拒否する
