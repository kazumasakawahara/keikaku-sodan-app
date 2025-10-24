#!/bin/bash
# 計画相談支援システム バックアップスクリプト

# スクリプトのディレクトリに移動
cd "$(dirname "$0")/.." || exit 1

# バックアップディレクトリ
BACKUP_DIR="./backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/keikaku_sodan_backup_${DATE}.tar.gz"

# バックアップディレクトリを作成
mkdir -p "${BACKUP_DIR}"

echo "🔄 バックアップを開始します..."
echo "   日時: $(date '+%Y-%m-%d %H:%M:%S')"

# データベースとログをバックアップ
tar -czf "${BACKUP_FILE}" \
    keikaku_sodan.db \
    2>/dev/null || true

if [ -f "${BACKUP_FILE}" ]; then
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ バックアップが完了しました！"
    echo "   ファイル: ${BACKUP_FILE}"
    echo "   サイズ: ${SIZE}"

    # 古いバックアップを削除（30日以上前）
    find "${BACKUP_DIR}" -name "keikaku_sodan_backup_*.tar.gz" -type f -mtime +30 -delete 2>/dev/null

    # バックアップ一覧を表示
    echo ""
    echo "📋 保存されているバックアップ:"
    ls -lh "${BACKUP_DIR}"/keikaku_sodan_backup_*.tar.gz 2>/dev/null | awk '{print "   -", $9, "("$5")"}'
else
    echo "❌ バックアップに失敗しました"
    exit 1
fi
