# Authentication Capability Specification

## ADDED Requirements

### Requirement: User Login
システムは、登録済みのユーザー名とパスワードによるログイン機能を提供しなければならない（MUST）。

#### Scenario: Valid credentials
- **WHEN** 有効なユーザー名とパスワードを入力してログインボタンをクリックした
- **THEN** システムはユーザーを認証し、ダッシュボードにリダイレクトする
- **AND** セッションが作成され、ユーザー情報がセッションに保存される

#### Scenario: Invalid credentials
- **WHEN** 無効なユーザー名またはパスワードを入力してログインした
- **THEN** システムはエラーメッセージ「ユーザー名またはパスワードが正しくありません」を表示する
- **AND** ログイン画面に留まる

#### Scenario: Inactive user
- **WHEN** 無効化されたユーザー（`is_active=False`）がログインを試みた
- **THEN** システムはエラーメッセージ「このアカウントは無効化されています」を表示する
- **AND** ログインを拒否する

### Requirement: User Logout
システムは、ログイン中のユーザーがログアウトできる機能を提供しなければならない（MUST）。

#### Scenario: Successful logout
- **WHEN** ログイン中のユーザーがログアウトボタンをクリックした
- **THEN** システムはセッションを破棄する
- **AND** ログイン画面にリダイレクトする

### Requirement: Session Management
システムは、セッションベースの認証を実装しなければならない（MUST）。

#### Scenario: Session timeout
- **WHEN** ユーザーが30分間操作を行わなかった
- **THEN** システムはセッションを自動的に破棄する
- **AND** 次の操作時にログイン画面にリダイレクトする

#### Scenario: Session validation
- **WHEN** 認証が必要なページにアクセスした
- **THEN** システムは有効なセッションの存在を確認する
- **AND** セッションが無効な場合、ログイン画面にリダイレクトする

### Requirement: Password Security
システムは、パスワードを安全に保存しなければならない（MUST）。

#### Scenario: Password hashing
- **WHEN** 新しいユーザーが作成される、またはパスワードが変更される
- **THEN** システムはbcryptアルゴリズムを使用してパスワードをハッシュ化する
- **AND** ハッシュ化されたパスワードのみをデータベースに保存する
- **AND** 平文のパスワードは保存しない

### Requirement: Role-Based Authorization
システムは、ロールベースのアクセス制御を実装しなければならない（MUST）。

#### Scenario: Admin access
- **WHEN** `role=admin`のユーザーがログインした
- **THEN** システムはすべての機能へのアクセスを許可する
- **AND** すべての利用者情報の閲覧・編集が可能である

#### Scenario: Staff access
- **WHEN** `role=staff`のユーザーがログインした
- **THEN** システムは自分が担当する利用者の情報のみ閲覧・編集を許可する
- **AND** 他のスタッフが担当する利用者の詳細情報へのアクセスを拒否する

#### Scenario: Unauthorized access attempt
- **WHEN** 一般スタッフが他のスタッフの担当利用者の編集画面にアクセスを試みた
- **THEN** システムは403 Forbiddenエラーを返す
- **AND** エラーメッセージ「この操作を行う権限がありません」を表示する

### Requirement: Login UI
システムは、シンプルで使いやすいログイン画面を提供しなければならない（MUST）。

#### Scenario: Login page display
- **WHEN** 未認証のユーザーがアプリケーションのURLにアクセスした
- **THEN** システムはログイン画面を表示する
- **AND** ユーザー名入力欄、パスワード入力欄、ログインボタンが表示される

#### Scenario: Error message display
- **WHEN** ログインに失敗した
- **THEN** システムはエラーメッセージを入力欄の下に赤色で表示する
- **AND** 入力したユーザー名は保持される（パスワードはクリアされる）
