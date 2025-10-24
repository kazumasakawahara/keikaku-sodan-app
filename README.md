# 計画相談支援 利用者管理システム

障害福祉サービスの計画相談支援事業所向けの利用者情報管理システムです。

## 🎯 プロジェクト概要

紙ベース・Excel管理から脱却し、利用者情報の一元管理、効率的な情報共有、支援履歴の可視化を実現します。

### 主な機能

- **利用者基本情報管理**: 氏名、生年月日、手帳情報、成年後見制度情報など
- **相談支援記録管理**: 相談日時、内容、対応記録
- **関係機関管理**: サービス事業所、医療機関、後見人等の情報
- **ネットワーク図**: 支援体制の可視化（Phase 3）
- **PDF出力**: ケース会議資料、家族交付資料の作成（Phase 2）

## 🚀 クイックスタート

### 前提条件

- Python 3.11以上
- uv (Pythonパッケージマネージャー)

### uvのインストール

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# または Homebrew
brew install uv
```

### セットアップ

```bash
# リポジトリのクローン
cd ~/AI-Workspace/keikaku-sodan-app

# 仮想環境の作成
uv venv

# 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 依存関係のインストール
uv sync  # または uv pip install -e .

# 環境変数の設定（オプション）
cp .env.example .env
# 必要に応じて .env を編集

# データベースの初期化（既に実行済みの場合はスキップ）
# python scripts/init_db.py

# 開発サーバーの起動
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

ブラウザで `http://localhost:8000` にアクセスしてください。

**デフォルトログイン情報**:
- ユーザー名: `admin`
- パスワード: `admin123`

## 📚 ドキュメント

- **[CLAUDE.md](./CLAUDE.md)**: 開発ガイド（技術スタック、セットアップ、開発の進め方）
- **[HANDOVER.md](./HANDOVER.md)**: 引継書（要件定義、設計、実装詳細）
- **[WIREFRAME.md](./WIREFRAME.md)**: UI設計・ワイヤーフレーム

## 🛠️ 技術スタック

- **バックエンド**: Python, FastAPI, SQLAlchemy, SQLite
- **フロントエンド**: HTML, CSS (Bootstrap 5), JavaScript
- **PDF生成**: Docling, ReportLab
- **パッケージ管理**: uv

## 📋 開発フェーズ

### Phase 1: 基本機能 (MVP) - 🎯 現在のフェーズ
- 利用者基本情報管理
- 相談支援記録管理
- 関係機関管理
- スタッフ管理

### Phase 2: 計画・記録機能
- サービス利用計画管理
- モニタリング記録管理
- PDF出力機能

### Phase 3: 可視化・高度機能
- ネットワーク図機能
- 高度な検索・分析機能

### Phase 4: 将来の拡張
- 過去データのインポート
- 外部システム連携

## 🤝 貢献

このプロジェクトは計画相談支援事業所の業務効率化を目的としています。
機能追加や改善の提案は歓迎します。

## 📝 ライセンス

このプロジェクトは内部利用を目的としています。

## 📧 サポート

質問や問題がある場合は、CLAUDE.mdやHANDOVER.mdを参照してください。

---

**最終更新**: 2025年10月24日  
**バージョン**: 0.1.0
