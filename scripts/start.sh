#!/bin/bash
# 計画相談支援システム起動スクリプト

# スクリプトのディレクトリに移動
cd "$(dirname "$0")/.." || exit 1

echo "🚀 計画相談支援システムを起動しています..."

# 仮想環境の確認
if [ ! -d ".venv" ]; then
    echo "❌ 仮想環境が見つかりません。"
    echo "   以下のコマンドで仮想環境を作成してください："
    echo "   uv venv && uv pip install -r requirements.txt"
    exit 1
fi

# 環境変数ファイルの確認
if [ ! -f ".env" ]; then
    echo "⚠️  .env ファイルが見つかりません。"
    echo "   .env.production をコピーして .env を作成してください。"
    echo "   cp .env.production .env"
    exit 1
fi

# データベースの確認
if [ ! -f "keikaku_sodan.db" ]; then
    echo "⚠️  データベースが見つかりません。初期化しますか？ (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        echo "📊 データベースを初期化しています..."
        .venv/bin/python scripts/init_db.py
        echo "✅ データベースの初期化が完了しました。"
    else
        echo "❌ データベースが必要です。"
        exit 1
    fi
fi

# サーバーを起動
echo "🌐 サーバーを起動しています..."
echo "   アクセスURL: http://localhost:8000"
echo "   停止するには Ctrl+C を押してください"
echo ""

# uvicornでサーバーを起動
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
