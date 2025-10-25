/**
 * 処方医モーダル管理
 */

let currentDoctorId = null;

/**
 * 処方医モーダルを表示
 */
function showDoctorModal(doctor = null) {
    currentDoctorId = doctor?.id || null;

    const modalHtml = `
        <div class="modal fade" id="doctorModal" tabindex="-1" aria-labelledby="doctorModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title" id="doctorModalLabel">
                            <i class="bi bi-person-badge"></i> ${doctor ? '処方医編集' : '処方医登録'}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="閉じる"></button>
                    </div>
                    <div class="modal-body">
                        <form id="doctorForm">
                            <div class="row g-3">
                                <!-- 医師名 -->
                                <div class="col-md-6">
                                    <label for="doctor_name" class="form-label">医師名 <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="doctor_name" name="name" 
                                           value="${doctor?.name || ''}" required>
                                </div>

                                <!-- 医療機関名 -->
                                <div class="col-md-6">
                                    <label for="hospital_name" class="form-label">医療機関名 <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="hospital_name" name="hospital_name"
                                           value="${doctor?.hospital_name || ''}" required>
                                </div>

                                <!-- 診療科 -->
                                <div class="col-md-6">
                                    <label for="specialty" class="form-label">診療科</label>
                                    <input type="text" class="form-control" id="specialty" name="specialty"
                                           value="${doctor?.specialty || ''}" placeholder="例: 精神科、内科">
                                </div>

                                <!-- 電話番号 -->
                                <div class="col-md-6">
                                    <label for="phone" class="form-label">電話番号</label>
                                    <input type="tel" class="form-control" id="phone" name="phone"
                                           value="${doctor?.phone || ''}" placeholder="例: 093-123-4567">
                                </div>

                                <!-- 住所 -->
                                <div class="col-12">
                                    <label for="address" class="form-label">住所</label>
                                    <input type="text" class="form-control" id="address" name="address"
                                           value="${doctor?.address || ''}" placeholder="例: 北九州市小倉北区○○町1-2-3">
                                </div>

                                <!-- 備考 -->
                                <div class="col-12">
                                    <label for="notes" class="form-label">備考</label>
                                    <textarea class="form-control" id="notes" name="notes" rows="3">${doctor?.notes || ''}</textarea>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle"></i> キャンセル
                        </button>
                        <button type="button" class="btn btn-primary" onclick="saveDoctorData()">
                            <i class="bi bi-check-circle"></i> ${doctor ? '更新' : '登録'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 既存のモーダルを削除
    const existingModal = document.getElementById('doctorModal');
    if (existingModal) {
        existingModal.remove();
    }

    // 新しいモーダルを追加
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // モーダルを表示
    const modal = new bootstrap.Modal(document.getElementById('doctorModal'));
    modal.show();

    // モーダルが閉じられた時にDOMから削除
    document.getElementById('doctorModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

/**
 * 処方医データを保存
 */
async function saveDoctorData() {
    const form = document.getElementById('doctorForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = {
        name: document.getElementById('doctor_name').value.trim(),
        hospital_name: document.getElementById('hospital_name').value.trim(),
        specialty: document.getElementById('specialty').value.trim() || null,
        phone: document.getElementById('phone').value.trim() || null,
        address: document.getElementById('address').value.trim() || null,
        notes: document.getElementById('notes').value.trim() || null
    };

    try {
        let response;
        if (currentDoctorId) {
            // 更新
            response = await fetch(`/api/prescribing-doctors/${currentDoctorId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(formData)
            });
        } else {
            // 新規登録
            response = await fetch('/api/prescribing-doctors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(formData)
            });
        }

        if (response.ok) {
            alert(currentDoctorId ? '処方医情報を更新しました' : '処方医を登録しました');
            
            // モーダルを閉じる
            const modal = bootstrap.Modal.getInstance(document.getElementById('doctorModal'));
            modal.hide();

            // 一覧を再読み込み（処方医一覧画面の場合）
            if (typeof loadDoctors === 'function') {
                loadDoctors();
            }

            // 処方医セレクトボックスを更新（服薬情報モーダルの場合）
            if (typeof loadDoctorOptions === 'function') {
                await loadDoctorOptions();
            }
        } else if (response.status === 401) {
            alert('認証エラー: 再度ログインしてください');
            window.location.href = '/login';
        } else {
            const error = await response.json();
            throw new Error(error.detail || '処方医の保存に失敗しました');
        }
    } catch (error) {
        console.error('処方医保存エラー:', error);
        alert('処方医の保存に失敗しました: ' + error.message);
    }
}
