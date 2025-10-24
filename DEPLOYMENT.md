# デプロイ手順書

計画相談支援 利用者管理システムの本番環境へのデプロイ手順を記載します。

## 📋 目次

1. [前提条件](#前提条件)
2. [サーバー準備](#サーバー準備)
3. [アプリケーションのデプロイ](#アプリケーションのデプロイ)
4. [systemdサービスの設定](#systemdサービスの設定)
5. [Nginxの設定（オプション）](#nginxの設定オプション)
6. [バックアップの設定](#バックアップの設定)
7. [運用管理](#運用管理)
8. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 推奨環境
- **OS**: Ubuntu 22.04 LTS または Rocky Linux 9
- **Python**: 3.11以上
- **メモリ**: 最低2GB（推奨4GB）
- **ストレージ**: 最低10GB（データ増加に応じて）
- **ネットワーク**: 事業所内LAN

### 必要なソフトウェア
- Python 3.11+
- uv（Pythonパッケージマネージャー）
- Git（任意：ソースコード管理）
- Nginx（任意：リバースプロキシ）

---

## サーバー準備

### 1. システムアップデート

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# Rocky Linux/RHEL
sudo dnf update -y
```

### 2. Python 3.11のインストール

```bash
# Ubuntu/Debian
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Rocky Linux/RHEL
sudo dnf install -y python3.11 python3.11-devel
```

### 3. uvのインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # または ~/.zshrc
```

### 4. 専用ユーザーの作成

```bash
sudo useradd -m -s /bin/bash keikaku-sodan
sudo mkdir -p /opt/keikaku-sodan-app
sudo chown keikaku-sodan:keikaku-sodan /opt/keikaku-sodan-app
```

---

## アプリケーションのデプロイ

### 1. ソースコードの配置

```bash
# 開発環境からファイルを転送
# 方法1: rsyncを使用
rsync -avz --exclude='.venv' --exclude='*.db' --exclude='__pycache__' \
    /path/to/keikaku-sodan-app/ \
    keikaku-sodan@server:/opt/keikaku-sodan-app/

# 方法2: Gitを使用
sudo su - keikaku-sodan
cd /opt/keikaku-sodan-app
git clone <repository-url> .
```

### 2. 仮想環境の作成

```bash
sudo su - keikaku-sodan
cd /opt/keikaku-sodan-app

# uvで仮想環境を作成
uv venv

# 依存パッケージのインストール
uv pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
# 本番用設定ファイルをコピー
cp .env.production .env

# エディタで編集
nano .env
```

**必須の変更項目:**

```bash
# セキュリティキーを生成
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# .envファイルに設定
SECRET_KEY=<生成されたキー>
DEBUG=False
```

### 4. データベースの初期化

```bash
# データベースを初期化
.venv/bin/python scripts/init_db.py

# 初期管理者アカウントを作成（シードデータ投入）
.venv/bin/python scripts/seed_data.py
```

### 5. 動作確認

```bash
# テストサーバーを起動
./scripts/start.sh

# 別のターミナルから確認
curl http://localhost:8000/
```

動作確認後、Ctrl+Cでサーバーを停止します。

---

## systemdサービスの設定

### 1. サービスファイルのコピー

```bash
sudo cp /opt/keikaku-sodan-app/deployment/keikaku-sodan.service \
    /etc/systemd/system/keikaku-sodan.service
```

### 2. ログディレクトリの作成

```bash
sudo mkdir -p /var/log/keikaku-sodan
sudo chown keikaku-sodan:keikaku-sodan /var/log/keikaku-sodan
```

### 3. サービスの有効化と起動

```bash
# サービスをリロード
sudo systemctl daemon-reload

# サービスを有効化（自動起動）
sudo systemctl enable keikaku-sodan.service

# サービスを起動
sudo systemctl start keikaku-sodan.service

# ステータス確認
sudo systemctl status keikaku-sodan.service
```

### 4. サービス管理コマンド

```bash
# サービスの停止
sudo systemctl stop keikaku-sodan.service

# サービスの再起動
sudo systemctl restart keikaku-sodan.service

# ログの確認
sudo journalctl -u keikaku-sodan.service -f
```

---

## Nginxの設定（オプション）

より安全なHTTPS接続や、ポート80でのアクセスを実現するために、Nginxをリバースプロキシとして使用します。

### 1. Nginxのインストール

```bash
# Ubuntu/Debian
sudo apt install -y nginx

# Rocky Linux/RHEL
sudo dnf install -y nginx
```

### 2. Nginx設定ファイルの作成

```bash
sudo nano /etc/nginx/sites-available/keikaku-sodan
```

**設定内容:**

```nginx
server {
    listen 80;
    server_name 192.168.x.x;  # サーバーのIPアドレスまたはホスト名

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/keikaku-sodan-app/app/static;
        expires 30d;
    }
}
```

### 3. 設定の有効化

```bash
# Ubuntuの場合
sudo ln -s /etc/nginx/sites-available/keikaku-sodan \
    /etc/nginx/sites-enabled/

# Rocky Linuxの場合は sites-available/enabled の仕組みがないため、
# /etc/nginx/conf.d/keikaku-sodan.conf に直接作成

# 設定テスト
sudo nginx -t

# Nginxを再起動
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## バックアップの設定

### 1. 手動バックアップ

```bash
sudo su - keikaku-sodan
cd /opt/keikaku-sodan-app
./scripts/backup.sh
```

バックアップファイルは `backups/` ディレクトリに保存されます。

### 2. 自動バックアップ（cron設定）

```bash
# crontabを編集
crontab -e
```

**毎日午前3時にバックアップを実行:**

```cron
0 3 * * * /opt/keikaku-sodan-app/scripts/backup.sh >> /var/log/keikaku-sodan/backup.log 2>&1
```

### 3. バックアップの復元

```bash
# サービスを停止
sudo systemctl stop keikaku-sodan.service

# バックアップファイルを展開
cd /opt/keikaku-sodan-app
tar -xzf backups/keikaku_sodan_backup_YYYYMMDD_HHMMSS.tar.gz

# サービスを再起動
sudo systemctl start keikaku-sodan.service
```

---

## 運用管理

### ログの確認

```bash
# アプリケーションログ
tail -f /var/log/keikaku-sodan/app.log

# エラーログ
tail -f /var/log/keikaku-sodan/error.log

# systemdログ
sudo journalctl -u keikaku-sodan.service -f
```

### データベースのバックアップ

```bash
# データベースファイルを直接コピー
cp /opt/keikaku-sodan-app/keikaku_sodan.db \
    /path/to/backup/keikaku_sodan_$(date +%Y%m%d).db
```

### アプリケーションの更新

```bash
# サービスを停止
sudo systemctl stop keikaku-sodan.service

# ユーザーを切り替え
sudo su - keikaku-sodan
cd /opt/keikaku-sodan-app

# バックアップを作成
./scripts/backup.sh

# 最新コードを取得
git pull  # または rsync

# 依存パッケージを更新
uv pip install -r requirements.txt

# データベースマイグレーション（必要に応じて）
# .venv/bin/alembic upgrade head

# サービスを再起動
exit
sudo systemctl start keikaku-sodan.service

# 動作確認
sudo systemctl status keikaku-sodan.service
```

---

## トラブルシューティング

### サービスが起動しない

```bash
# ログを確認
sudo journalctl -u keikaku-sodan.service -n 50

# 設定ファイルを確認
cat /opt/keikaku-sodan-app/.env

# 手動起動で詳細エラーを確認
sudo su - keikaku-sodan
cd /opt/keikaku-sodan-app
./scripts/start.sh
```

### データベースエラー

```bash
# データベースファイルの権限を確認
ls -la /opt/keikaku-sodan-app/*.db

# 権限を修正
sudo chown keikaku-sodan:keikaku-sodan /opt/keikaku-sodan-app/*.db

# データベースを再初期化（データが失われます！）
rm /opt/keikaku-sodan-app/keikaku_sodan.db
.venv/bin/python scripts/init_db.py
```

### ポート競合

```bash
# 8000番ポートを使用しているプロセスを確認
sudo lsof -i :8000

# 必要に応じてプロセスを停止
sudo kill -9 <PID>
```

### Nginxのエラー

```bash
# Nginx設定をテスト
sudo nginx -t

# Nginxエラーログを確認
sudo tail -f /var/log/nginx/error.log

# Nginxを再起動
sudo systemctl restart nginx
```

---

## セキュリティの注意事項

1. **SECRET_KEYの変更**: 必ず本番用のランダムな値に変更してください
2. **DEBUGモードの無効化**: `.env`で`DEBUG=False`に設定してください
3. **ファイアウォールの設定**: 必要なポートのみ開放してください
   ```bash
   # Ubuntu
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable

   # Rocky Linux
   sudo firewall-cmd --permanent --add-service=http
   sudo firewall-cmd --permanent --add-service=https
   sudo firewall-cmd --reload
   ```
4. **定期的なバックアップ**: cronで自動バックアップを設定してください
5. **ログの監視**: 定期的にログを確認し、異常がないか確認してください

---

## 連絡先

問題が発生した場合は、プロジェクト管理者に連絡してください。

- **プロジェクト**: 計画相談支援 利用者管理システム
- **バージョン**: 1.0.0
- **最終更新**: 2025年10月24日
