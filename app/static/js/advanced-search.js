// 高度な検索機能
// 利用者検索の複数条件対応とソート・ページネーション

let currentPage = 0;
const itemsPerPage = 20;
let currentFilters = {};
let currentSort = { by: 'id', order: 'asc' };
let searchTimeout = null;

/**
 * 高度な検索フォームの処理
 */
function handleAdvancedSearch(event) {
    if (event) {
        event.preventDefault();
    }

    // 簡易検索フォームからの呼び出しの場合
    const simpleForm = document.getElementById('simple-search-form');
    const advancedForm = document.getElementById('advanced-search-form');

    let formToUse = advancedForm;

    // イベントソースを判定
    if (event && event.target === simpleForm) {
        // 簡易検索の場合、検索語をname/name_kanaフィルターとして適用
        const searchInput = simpleForm.querySelector('input[name="search"]');
        const searchValue = searchInput ? searchInput.value.trim() : '';

        if (searchValue) {
            currentFilters = {
                search: searchValue  // APIで search パラメータを処理する必要があります
            };
        } else {
            currentFilters = {};
        }
    } else {
        // 高度な検索フォームの場合
        const formData = new FormData(advancedForm);

        currentFilters = {};
        for (const [key, value] of formData.entries()) {
            if (value) {
                currentFilters[key] = value;
            }
        }
    }

    currentPage = 0;
    loadUsers();
}

/**
 * 検索条件をクリア
 */
function clearSearch() {
    // 両方のフォームをリセット
    const simpleForm = document.getElementById('simple-search-form');
    const advancedForm = document.getElementById('advanced-search-form');

    if (simpleForm) simpleForm.reset();
    if (advancedForm) advancedForm.reset();

    currentFilters = {};
    currentPage = 0;
    loadUsers();
}

/**
 * ソート処理
 * @param {string} column - ソート対象カラム
 */
function handleSort(column) {
    if (currentSort.by === column) {
        // 同じカラムの場合は昇順/降順を切り替え
        currentSort.order = currentSort.order === 'asc' ? 'desc' : 'asc';
    } else {
        // 異なるカラムの場合は昇順でソート
        currentSort.by = column;
        currentSort.order = 'asc';
    }

    currentPage = 0;
    loadUsers();
    updateSortIcons();
}

/**
 * ソートアイコンを更新
 */
function updateSortIcons() {
    // すべてのソートアイコンをリセット
    document.querySelectorAll('.sort-icon').forEach(icon => {
        icon.className = 'sort-icon bi bi-arrow-down-up';
    });

    // アクティブなソートアイコンを更新
    const activeIcon = document.querySelector(`[data-sort="${currentSort.by}"] .sort-icon`);
    if (activeIcon) {
        activeIcon.className = currentSort.order === 'asc'
            ? 'sort-icon bi bi-arrow-up'
            : 'sort-icon bi bi-arrow-down';
    }
}

/**
 * 利用者一覧を読み込み
 */
async function loadUsers() {
    try {
        // クエリパラメータを構築
        const params = new URLSearchParams({
            skip: currentPage * itemsPerPage,
            limit: itemsPerPage,
            sort_by: currentSort.by,
            order: currentSort.order,
            ...currentFilters
        });

        const response = await fetch(`/api/users?${params}`);
        if (response.ok) {
            const users = await response.json();
            displayUsers(users);
            updatePagination(users.length);
        } else {
            alert('利用者データの取得に失敗しました');
        }
    } catch (error) {
        console.error('エラー:', error);
        alert('サーバーとの通信に失敗しました');
    }
}

/**
 * 利用者一覧を表示
 * @param {Array} users - 利用者データ配列
 */
function displayUsers(users) {
    const tbody = document.getElementById('users-table-body');

    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    検索条件に一致する利用者が見つかりませんでした
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>
                <a href="/users/${user.id}" class="text-decoration-none">
                    ${user.name}
                </a>
            </td>
            <td>${user.name_kana || '-'}</td>
            <td>${user.age !== null ? user.age + '歳' : '-'}</td>
            <td>${user.disability_support_level ? '区分' + user.disability_support_level : '-'}</td>
            <td>
                <a href="/users/${user.id}" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-eye"></i> 詳細
                </a>
            </td>
        </tr>
    `).join('');
}

/**
 * ページネーションを更新
 * @param {number} itemCount - 現在のページのアイテム数
 */
function updatePagination(itemCount) {
    const pagination = document.getElementById('pagination');
    const hasPrev = currentPage > 0;
    const hasNext = itemCount === itemsPerPage;

    let html = '<ul class="pagination justify-content-center mb-0">';

    // 前へボタン
    if (hasPrev) {
        html += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${currentPage - 1}); return false;">
                    <i class="bi bi-chevron-left"></i> 前へ
                </a>
            </li>
        `;
    } else {
        html += `
            <li class="page-item disabled">
                <span class="page-link">
                    <i class="bi bi-chevron-left"></i> 前へ
                </span>
            </li>
        `;
    }

    // ページ番号
    html += `
        <li class="page-item active">
            <span class="page-link">${currentPage + 1}</span>
        </li>
    `;

    // 次へボタン
    if (hasNext) {
        html += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${currentPage + 1}); return false;">
                    次へ <i class="bi bi-chevron-right"></i>
                </a>
            </li>
        `;
    } else {
        html += `
            <li class="page-item disabled">
                <span class="page-link">
                    次へ <i class="bi bi-chevron-right"></i>
                </span>
            </li>
        `;
    }

    html += '</ul>';
    pagination.innerHTML = html;
}

/**
 * ページ変更
 * @param {number} page - 移動先のページ番号
 */
function changePage(page) {
    currentPage = page;
    loadUsers();
    window.scrollTo(0, 0);
}

/**
 * 高度な検索フォームの表示/非表示切り替え
 */
function toggleAdvancedSearch() {
    const form = document.getElementById('advanced-search-collapse');
    const bsCollapse = new bootstrap.Collapse(form, {
        toggle: true
    });
}

/**
 * リアルタイム検索サジェスト機能の初期化
 */
function initializeSearchSuggestions() {
    const searchInput = document.querySelector('#simple-search-form input[name="search"]');

    if (!searchInput) {
        return;
    }

    // サジェスト表示用のdiv要素を作成
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.id = 'search-suggestions';
    suggestionsDiv.className = 'list-group';
    suggestionsDiv.style.display = 'none';

    // body直下に配置して、z-index問題を回避
    document.body.appendChild(suggestionsDiv);

    // 検索入力欄の位置を動的に計算して配置
    function updateSuggestionsPosition() {
        const rect = searchInput.getBoundingClientRect();
        suggestionsDiv.style.position = 'fixed';
        suggestionsDiv.style.top = (rect.bottom + 5) + 'px';
        suggestionsDiv.style.left = rect.left + 'px';
        suggestionsDiv.style.width = rect.width + 'px';
    }

    // 入力イベントでリアルタイム検索
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();

        if (query.length < 1) {
            suggestionsDiv.style.display = 'none';
            return;
        }

        // デバウンス（150ms）- より高速に
        searchTimeout = setTimeout(() => {
            fetchSuggestions(query);
        }, 150);
    });

    // 候補リストの mousedown イベントで直接遷移
    suggestionsDiv.addEventListener('mousedown', function(e) {
        // リンク要素を取得
        const link = e.target.closest('a');
        if (link && link.href) {
            // 即座にページ遷移
            e.preventDefault();
            window.location.href = link.href;
        }
    });

    // フォーカスアウト時に候補を非表示（遅延を長めに）
    searchInput.addEventListener('blur', function() {
        setTimeout(() => {
            suggestionsDiv.style.display = 'none';
        }, 500);
    });

    // フォーカス時に既に入力されている場合は候補を表示
    searchInput.addEventListener('focus', function() {
        const query = this.value.trim();
        if (query.length >= 1 && suggestionsDiv.children.length > 0) {
            suggestionsDiv.style.display = 'block';
        }
    });
}

/**
 * 検索候補を取得してサジェスト表示
 * @param {string} query - 検索キーワード
 */
async function fetchSuggestions(query) {
    const suggestionsDiv = document.getElementById('search-suggestions');

    if (!suggestionsDiv) {
        return;
    }

    try {
        const response = await fetch(`/api/users?search=${encodeURIComponent(query)}&limit=10`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('検索に失敗しました');
        }

        const users = await response.json();
        displaySuggestions(users);
    } catch (error) {
        console.error('検索エラー:', error);
        suggestionsDiv.innerHTML = '<div class="list-group-item text-danger">検索中にエラーが発生しました</div>';
        suggestionsDiv.style.display = 'block';
    }
}

/**
 * 検索候補を画面に表示
 * @param {Array} users - 利用者データ配列
 */
function displaySuggestions(users) {
    const suggestionsDiv = document.getElementById('search-suggestions');

    if (!suggestionsDiv) {
        return;
    }

    if (users.length === 0) {
        suggestionsDiv.innerHTML = '<div class="list-group-item text-muted">該当する利用者が見つかりません</div>';
        suggestionsDiv.style.display = 'block';
        return;
    }

    suggestionsDiv.innerHTML = users.map(user => `
        <a href="/users/${user.id}" class="list-group-item list-group-item-action" style="padding: 12px 16px;">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong style="font-size: 1.05rem; color: #212529;">${escapeHtml(user.name)}</strong>
                    ${user.name_kana ? `<small class="text-muted" style="margin-left: 8px;">（${escapeHtml(user.name_kana)}）</small>` : ''}
                </div>
                <div class="text-end">
                    <small class="text-muted">年齢: ${user.age !== null ? user.age + '歳' : '不明'}</small>
                    ${user.disability_support_level ? `<br><small class="text-muted">区分${user.disability_support_level}</small>` : ''}
                </div>
            </div>
        </a>
    `).join('');

    // 位置を更新してから表示（IME候補との干渉を避けるため下げて右にずらす）
    const searchInput = document.querySelector('#simple-search-form input[name="search"]');
    if (searchInput) {
        const rect = searchInput.getBoundingClientRect();
        suggestionsDiv.style.position = 'fixed';
        suggestionsDiv.style.top = (rect.bottom + 40) + 'px';
        suggestionsDiv.style.left = (rect.left + 80) + 'px';
        suggestionsDiv.style.width = rect.width + 'px';
    }
    suggestionsDiv.style.display = 'block';
}

/**
 * HTMLエスケープ処理
 * @param {string} text - エスケープ対象のテキスト
 * @returns {string} エスケープ済みテキスト
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ページ読み込み時にサジェスト機能を初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSearchSuggestions);
} else {
    initializeSearchSuggestions();
}
