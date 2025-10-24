/**
 * 削除確認ダイアログと削除処理のユーティリティ関数
 *
 * 使用例:
 * <button onclick="confirmDelete('users', 123, '山田太郎', '/users')">削除</button>
 */

/**
 * 削除確認ダイアログを表示し、削除を実行
 *
 * @param {string} entityType - エンティティの種類 ('users', 'consultations', 'plans', 'monitorings')
 * @param {number} entityId - 削除対象のID
 * @param {string} entityName - 削除対象の名前（確認メッセージに使用）
 * @param {string} redirectUrl - 削除成功後のリダイレクト先（省略時は一覧ページ）
 * @returns {Promise<void>}
 */
async function confirmDelete(entityType, entityId, entityName, redirectUrl = null) {
    const entityTypeNames = {
        'users': '利用者',
        'consultations': '相談記録',
        'plans': '計画',
        'monitorings': 'モニタリング記録',
        'organizations': '関係機関'
    };

    const typeName = entityTypeNames[entityType] || 'データ';
    const confirmMessage = `${entityName}の${typeName}を削除してもよろしいですか?\n\n※この操作は取り消せません。`;

    if (!confirm(confirmMessage)) {
        return;
    }

    try {
        const response = await fetch(`/api/${entityType}/${entityId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok || response.status === 204) {
            showSuccessMessage(`${typeName}を削除しました`);

            // リダイレクト先の決定
            const finalRedirectUrl = redirectUrl || `/${entityType}`;

            setTimeout(() => {
                window.location.href = finalRedirectUrl;
            }, 1000);
        } else {
            const error = await response.json().catch(() => ({ detail: '不明なエラー' }));
            alert(`削除に失敗しました: ${error.detail || '不明なエラー'}`);
        }
    } catch (error) {
        console.error('削除エラー:', error);
        alert('サーバーとの通信に失敗しました');
    }
}

/**
 * 成功メッセージを表示
 *
 * @param {string} message - 表示するメッセージ
 * @param {number} duration - 表示時間（ミリ秒、デフォルト3000）
 */
function showSuccessMessage(message, duration = 3000) {
    // 既存のメッセージを削除
    const existingAlert = document.querySelector('.alert-success.position-fixed');
    if (existingAlert) {
        existingAlert.remove();
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <i class="bi bi-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // 自動削除
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, duration);
}

/**
 * エラーメッセージを表示
 *
 * @param {string} message - 表示するメッセージ
 * @param {number} duration - 表示時間（ミリ秒、デフォルト5000）
 */
function showErrorMessage(message, duration = 5000) {
    // 既存のメッセージを削除
    const existingAlert = document.querySelector('.alert-danger.position-fixed');
    if (existingAlert) {
        existingAlert.remove();
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <i class="bi bi-exclamation-triangle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // 自動削除
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, duration);
}

/**
 * 情報メッセージを表示
 *
 * @param {string} message - 表示するメッセージ
 * @param {number} duration - 表示時間（ミリ秒、デフォルト3000）
 */
function showInfoMessage(message, duration = 3000) {
    // 既存のメッセージを削除
    const existingAlert = document.querySelector('.alert-info.position-fixed');
    if (existingAlert) {
        existingAlert.remove();
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <i class="bi bi-info-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // 自動削除
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, duration);
}
