// 計画相談支援 利用者管理システム - メインJavaScript

/**
 * 認証チェック
 * ログインしていない場合はログインページにリダイレクト
 */
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me');

        if (response.ok) {
            const staff = await response.json();
            // ナビゲーションバーにユーザー名を表示
            const userNameElement = document.getElementById('current-user-name');
            if (userNameElement) {
                userNameElement.textContent = staff.name;
            }

            // 管理者の場合、スタッフ管理メニューを表示
            if (staff.role === 'admin') {
                const staffsMenuItem = document.getElementById('staffs-menu-item');
                if (staffsMenuItem) {
                    staffsMenuItem.style.display = 'block';
                }
            }

            // ローカルストレージに保存（他のページでも使用可能に）
            localStorage.setItem('currentUser', JSON.stringify(staff));

            return staff;
        } else {
            // 未認証の場合、ログインページにリダイレクト
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
            return null;
        }
    } catch (error) {
        console.error('認証チェックエラー:', error);
        if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
        }
        return null;
    }
}

/**
 * ログアウト
 */
async function logout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
        });

        if (response.ok) {
            // ローカルストレージをクリア
            localStorage.removeItem('currentUser');
            window.location.href = '/login';
        } else {
            alert('ログアウトに失敗しました');
        }
    } catch (error) {
        console.error('ログアウトエラー:', error);
        alert('サーバーとの通信に失敗しました');
    }
}

/**
 * 現在のユーザー情報を取得
 * @returns {object|null} ユーザー情報
 */
function getCurrentUser() {
    const userJson = localStorage.getItem('currentUser');
    return userJson ? JSON.parse(userJson) : null;
}

/**
 * 日付を日本語形式でフォーマット
 * @param {string} dateString - ISO形式の日付文字列
 * @returns {string} フォーマットされた日付
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * エラーメッセージを表示
 * @param {string} message - エラーメッセージ
 */
function showError(message) {
    alert(message);
}

/**
 * 成功メッセージを表示
 * @param {string} message - 成功メッセージ
 */
function showSuccess(message) {
    alert(message);
}

/**
 * 確認ダイアログを表示
 * @param {string} message - 確認メッセージ
 * @returns {boolean} ユーザーの選択
 */
function confirm(message) {
    return window.confirm(message);
}

/**
 * ローディング表示を切り替え
 * @param {string} elementId - 要素ID
 * @param {boolean} show - 表示/非表示
 */
function toggleLoading(elementId, show) {
    const element = document.getElementById(elementId);
    if (element) {
        if (show) {
            element.classList.remove('d-none');
        } else {
            element.classList.add('d-none');
        }
    }
}

/**
 * APIリクエストのヘルパー関数
 * @param {string} url - APIエンドポイント
 * @param {object} options - fetchオプション
 * @returns {Promise<object>} レスポンス
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'リクエストに失敗しました');
        }

        // 204 No Contentの場合は空オブジェクトを返す
        if (response.status === 204) {
            return {};
        }

        return await response.json();
    } catch (error) {
        console.error('API リクエストエラー:', error);
        throw error;
    }
}

/**
 * クエリパラメータを取得
 * @param {string} name - パラメータ名
 * @returns {string|null} パラメータ値
 */
function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * 空の値を'-'に変換
 * @param {any} value - 値
 * @returns {string} 表示用の値
 */
function displayValue(value) {
    return value || '-';
}

/**
 * デバウンス関数
 * @param {Function} func - 実行する関数
 * @param {number} wait - 待機時間（ミリ秒）
 * @returns {Function} デバウンスされた関数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ページロード時の処理
document.addEventListener('DOMContentLoaded', () => {
    // ツールチップの初期化（Bootstrap 5）
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // ポップオーバーの初期化（Bootstrap 5）
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// グローバルエラーハンドラ
window.addEventListener('unhandledrejection', (event) => {
    console.error('未処理のPromise拒否:', event.reason);
});
