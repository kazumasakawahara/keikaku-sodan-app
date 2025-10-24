// ダッシュボードグラフ作成
// Chart.jsを使用した統計データの可視化

/**
 * 相談記録種別の円グラフを作成
 * @param {Object} data - 種別ごとのカウントデータ
 */
function createConsultationTypeChart(data) {
    const ctx = document.getElementById('consultationTypeChart');
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#0d6efd',
                    '#198754',
                    '#ffc107',
                    '#dc3545',
                    '#0dcaf0',
                    '#6c757d'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: '相談記録の種別割合'
                }
            }
        }
    });
}

/**
 * 計画承認状況の棒グラフを作成
 * @param {Object} data - 状態ごとのカウントデータ
 */
function createPlanStatusChart(data) {
    const ctx = document.getElementById('planStatusChart');
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '計画数',
                data: values,
                backgroundColor: '#0d6efd',
                borderColor: '#0d6efd',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: '計画の承認状況'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

/**
 * 月次相談件数の折れ線グラフを作成
 * @param {Array} data - 月ごとのデータ配列
 */
function createMonthlyConsultationChart(data) {
    const ctx = document.getElementById('monthlyConsultationChart');
    if (!ctx) return;

    const labels = data.map(d => d.month);
    const values = data.map(d => d.count);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '相談件数',
                data: values,
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                borderColor: '#0d6efd',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: '月次相談件数推移'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

/**
 * 年齢層別利用者数のドーナツグラフを作成
 * @param {Object} data - 年齢層ごとのカウントデータ
 */
function createAgeGroupChart(data) {
    const ctx = document.getElementById('ageGroupChart');
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#0d6efd',
                    '#198754',
                    '#ffc107',
                    '#dc3545',
                    '#6c757d'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: '年齢層別利用者数'
                }
            }
        }
    });
}

/**
 * 最近閲覧した利用者のネットワーク図サムネイルを表示
 */
async function loadRecentNetworks() {
    try {
        // 利用者一覧を取得（最大5名）
        const response = await fetch('/api/users?limit=5');
        if (!response.ok) {
            throw new Error('利用者データの取得に失敗しました');
        }

        const users = await response.json();
        const container = document.getElementById('recent-networks-container');

        if (!users || users.length === 0) {
            container.innerHTML = '<p class="text-muted">表示する利用者がありません</p>';
            return;
        }

        // カード形式で表示
        let html = '<div class="row g-3">';
        for (const user of users) {
            html += `
                <div class="col-md-4 col-lg-3">
                    <div class="card h-100 shadow-sm network-card">
                        <div class="card-body text-center">
                            <div class="network-icon mb-3">
                                <i class="bi bi-diagram-3-fill text-info" style="font-size: 3rem;"></i>
                            </div>
                            <h6 class="card-title">${user.name}</h6>
                            <p class="card-text small text-muted">
                                ${user.gender || '不明'} / ${user.age ? user.age + '歳' : '年齢不明'}
                            </p>
                            <div class="d-grid gap-2">
                                <a href="/users/${user.id}/network" class="btn btn-sm btn-outline-info">
                                    <i class="bi bi-eye"></i> 図を表示
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        html += '</div>';

        container.innerHTML = html;
    } catch (error) {
        console.error('エラー:', error);
        const container = document.getElementById('recent-networks-container');
        container.innerHTML = '<p class="text-danger">ネットワーク図の読み込みに失敗しました</p>';
    }
}
