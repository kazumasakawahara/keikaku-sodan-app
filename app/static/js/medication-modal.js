/**
 * 服薬情報登録・編集モーダル
 */

// 処方医一覧のキャッシュ
let doctorsCache = null;

/**
 * 処方医一覧を取得
 */
async function loadDoctors() {
    if (doctorsCache) {
        return doctorsCache;
    }

    try {
        const response = await fetch('/api/prescribing-doctors', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            doctorsCache = await response.json();
            return doctorsCache;
        }
    } catch (error) {
        console.error('処方医の取得エラー:', error);
    }
    return [];
}

/**
 * 服薬情報登録モーダルを表示
 */
async function showMedicationModal(userId, medicationId = null) {
    const doctors = await loadDoctors();
    const isEdit = medicationId !== null;
    let medication = null;

    // 編集モードの場合、既存データを取得
    if (isEdit) {
        try {
            const response = await fetch(`/api/medications/${medicationId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            if (response.ok) {
                medication = await response.json();
            }
        } catch (error) {
            console.error('服薬情報の取得エラー:', error);
            alert('服薬情報の取得に失敗しました');
            return;
        }
    }

    const modalHtml = `
        <div class="modal fade" id="medicationModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="bi bi-capsule"></i> ${isEdit ? '服薬情報編集' : '服薬情報登録'}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="medicationForm">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label for="medication_name" class="form-label">薬品名 <span class="text-danger">*</span></label>
                                    <div class="input-group">
                                        <input type="text" class="form-control" id="medication_name" name="medication_name"
                                               value="${medication?.medication_name || ''}" required>
                                        <button class="btn btn-outline-info" type="button" onclick="showDrugInfoModal(document.getElementById('medication_name').value)">
                                            <i class="bi bi-search"></i> 薬品情報
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <label for="generic_name" class="form-label">一般名</label>
                                    <input type="text" class="form-control" id="generic_name" name="generic_name"
                                           value="${medication?.generic_name || ''}">
                                </div>
                                <div class="col-md-4">
                                    <label for="dosage" class="form-label">用量</label>
                                    <input type="text" class="form-control" id="dosage" name="dosage"
                                           placeholder="例: 2mg" value="${medication?.dosage || ''}">
                                </div>
                                <div class="col-md-4">
                                    <label for="frequency" class="form-label">服用回数</label>
                                    <input type="text" class="form-control" id="frequency" name="frequency"
                                           placeholder="例: 1日2回" value="${medication?.frequency || ''}">
                                </div>
                                <div class="col-md-4">
                                    <label for="timing" class="form-label">服用タイミング</label>
                                    <input type="text" class="form-control" id="timing" name="timing"
                                           placeholder="例: 朝・夕食後" value="${medication?.timing || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label for="start_date" class="form-label">服用開始日</label>
                                    <input type="date" class="form-control" id="start_date" name="start_date"
                                           value="${medication?.start_date || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label for="end_date" class="form-label">服用終了日</label>
                                    <input type="date" class="form-control" id="end_date" name="end_date"
                                           value="${medication?.end_date || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label for="prescribing_doctor_id" class="form-label">処方医</label>
                                    <select class="form-select" id="prescribing_doctor_id" name="prescribing_doctor_id">
                                        <option value="">選択してください</option>
                                        ${doctors.map(d => `
                                            <option value="${d.id}" ${medication?.prescribing_doctor_id === d.id ? 'selected' : ''}>
                                                ${d.name} (${d.hospital_name || '病院名不明'})
                                            </option>
                                        `).join('')}
                                    </select>
                                    <small class="text-muted">
                                        <a href="#" onclick="showDoctorModal(); return false;">新しい処方医を登録</a>
                                    </small>
                                </div>
                                <div class="col-md-6">
                                    <label for="is_current" class="form-label">状態</label>
                                    <select class="form-select" id="is_current" name="is_current">
                                        <option value="true" ${medication?.is_current !== false ? 'selected' : ''}>現在服用中</option>
                                        <option value="false" ${medication?.is_current === false ? 'selected' : ''}>服用終了</option>
                                    </select>
                                </div>
                                <div class="col-12">
                                    <label for="purpose" class="form-label">処方目的</label>
                                    <textarea class="form-control" id="purpose" name="purpose" rows="2">${medication?.purpose || ''}</textarea>
                                </div>
                                <div class="col-12">
                                    <label for="notes" class="form-label">備考</label>
                                    <textarea class="form-control" id="notes" name="notes" rows="2">${medication?.notes || ''}</textarea>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">キャンセル</button>
                        <button type="button" class="btn btn-danger" onclick="saveMedication(${userId}, ${medicationId})">
                            <i class="bi bi-save"></i> 保存
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 既存のモーダルを削除
    const existingModal = document.getElementById('medicationModal');
    if (existingModal) {
        existingModal.remove();
    }

    // モーダルを追加
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // モーダルを表示
    const modal = new bootstrap.Modal(document.getElementById('medicationModal'));
    modal.show();

    // モーダルが閉じられたときにDOMから削除
    document.getElementById('medicationModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

/**
 * 服薬情報を保存
 */
async function saveMedication(userId, medicationId = null) {
    const form = document.getElementById('medicationForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const data = {
        user_id: userId,
        medication_name: formData.get('medication_name'),
        generic_name: formData.get('generic_name') || null,
        dosage: formData.get('dosage') || null,
        frequency: formData.get('frequency') || null,
        timing: formData.get('timing') || null,
        start_date: formData.get('start_date') || null,
        end_date: formData.get('end_date') || null,
        is_current: formData.get('is_current') === 'true',
        purpose: formData.get('purpose') || null,
        notes: formData.get('notes') || null,
        prescribing_doctor_id: formData.get('prescribing_doctor_id') ? parseInt(formData.get('prescribing_doctor_id')) : null
    };

    try {
        const url = medicationId ? `/api/medications/${medicationId}` : '/api/medications';
        const method = medicationId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert(medicationId ? '服薬情報を更新しました' : '服薬情報を登録しました');

            // モーダルを閉じる
            const modal = bootstrap.Modal.getInstance(document.getElementById('medicationModal'));
            modal.hide();

            // 服薬情報リストを再読み込み
            if (typeof loadMedications === 'function') {
                await loadMedications();
            }
        } else {
            const error = await response.json();
            alert(`保存に失敗しました: ${error.detail || '不明なエラー'}`);
        }
    } catch (error) {
        console.error('保存エラー:', error);
        alert('保存中にエラーが発生しました');
    }
}

/**
 * 処方医登録モーダルを表示
 */
function showDoctorModal(doctorId = null) {
    const isEdit = doctorId !== null;
    // TODO: 処方医の詳細を取得（編集モードの場合）

    const modalHtml = `
        <div class="modal fade" id="doctorModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="bi bi-person-badge"></i> ${isEdit ? '処方医編集' : '処方医登録'}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="doctorForm">
                            <div class="mb-3">
                                <label for="doctor_name" class="form-label">医師名 <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" id="doctor_name" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label for="hospital_name" class="form-label">医療機関名</label>
                                <input type="text" class="form-control" id="hospital_name" name="hospital_name">
                            </div>
                            <div class="mb-3">
                                <label for="department" class="form-label">診療科</label>
                                <input type="text" class="form-control" id="department" name="department"
                                       placeholder="例: 精神科">
                            </div>
                            <div class="mb-3">
                                <label for="doctor_phone" class="form-label">電話番号</label>
                                <input type="tel" class="form-control" id="doctor_phone" name="phone"
                                       placeholder="例: 093-123-4567">
                            </div>
                            <div class="mb-3">
                                <label for="doctor_address" class="form-label">住所</label>
                                <textarea class="form-control" id="doctor_address" name="address" rows="2"></textarea>
                            </div>
                            <div class="mb-3">
                                <label for="doctor_notes" class="form-label">備考</label>
                                <textarea class="form-control" id="doctor_notes" name="notes" rows="2"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">キャンセル</button>
                        <button type="button" class="btn btn-primary" onclick="saveDoctor()">
                            <i class="bi bi-save"></i> 保存
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

    // モーダルを追加
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // モーダルを表示
    const modal = new bootstrap.Modal(document.getElementById('doctorModal'));
    modal.show();

    // モーダルが閉じられたときにDOMから削除
    document.getElementById('doctorModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

/**
 * 処方医を保存
 */
async function saveDoctor() {
    const form = document.getElementById('doctorForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const data = {
        name: formData.get('name'),
        hospital_name: formData.get('hospital_name') || null,
        department: formData.get('department') || null,
        phone: formData.get('phone') || null,
        address: formData.get('address') || null,
        notes: formData.get('notes') || null
    };

    try {
        const response = await fetch('/api/prescribing-doctors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const newDoctor = await response.json();
            alert('処方医を登録しました');

            // キャッシュをクリア
            doctorsCache = null;

            // モーダルを閉じる
            const modal = bootstrap.Modal.getInstance(document.getElementById('doctorModal'));
            modal.hide();

            // 服薬情報モーダルの処方医リストを更新
            const doctorSelect = document.getElementById('prescribing_doctor_id');
            if (doctorSelect) {
                const doctors = await loadDoctors();
                doctorSelect.innerHTML = '<option value="">選択してください</option>' +
                    doctors.map(d => `
                        <option value="${d.id}" ${d.id === newDoctor.id ? 'selected' : ''}>
                            ${d.name} (${d.hospital_name || '病院名不明'})
                        </option>
                    `).join('');
            }
        } else {
            const error = await response.json();
            alert(`保存に失敗しました: ${error.detail || '不明なエラー'}`);
        }
    } catch (error) {
        console.error('保存エラー:', error);
        alert('保存中にエラーが発生しました');
    }
}

/**
 * 薬品情報検索モーダルを表示
 */
async function showDrugInfoModal(drugName = '') {
    if (!drugName || drugName.trim().length < 2) {
        alert('薬品名を2文字以上入力してください');
        return;
    }

    try {
        const response = await fetch(`/api/drug-info/search?query=${encodeURIComponent(drugName)}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            const results = await response.json();
            displayDrugInfoModal(results);
        } else {
            alert('薬品情報の取得に失敗しました');
        }
    } catch (error) {
        console.error('薬品情報取得エラー:', error);
        alert('薬品情報の取得中にエラーが発生しました');
    }
}

/**
 * 薬品情報モーダルを表示
 */
function displayDrugInfoModal(results) {
    let drugInfoHtml = '';

    if (results.length === 0) {
        drugInfoHtml = '<p class="text-muted">該当する薬品情報が見つかりませんでした</p>';
    } else {
        results.forEach((drug, index) => {
            drugInfoHtml += `
                <div class="card mb-3 ${index === 0 ? 'border-primary' : ''}">
                    <div class="card-header ${index === 0 ? 'bg-primary text-white' : 'bg-light'}">
                        <h6 class="mb-0">
                            <strong>${drug.name}</strong>
                            ${drug.generic_name ? `<span class="badge bg-secondary ms-2">${drug.generic_name}</span>` : ''}
                        </h6>
                    </div>
                    <div class="card-body">
                        ${drug.effects ? `
                            <div class="mb-3">
                                <strong><i class="bi bi-check-circle text-success"></i> 効能・効果:</strong>
                                <p class="mb-0 ms-4">${drug.effects}</p>
                            </div>
                        ` : ''}
                        ${drug.side_effects ? `
                            <div class="mb-3">
                                <strong><i class="bi bi-exclamation-triangle text-warning"></i> 副作用:</strong>
                                <p class="mb-0 ms-4">${drug.side_effects}</p>
                            </div>
                        ` : ''}
                        ${drug.dosage_form ? `
                            <div class="mb-3">
                                <strong><i class="bi bi-capsule"></i> 剤形:</strong>
                                <span class="ms-2">${drug.dosage_form}</span>
                            </div>
                        ` : ''}
                        ${drug.manufacturer ? `
                            <div class="mb-3">
                                <strong><i class="bi bi-building"></i> 製造販売元:</strong>
                                <span class="ms-2">${drug.manufacturer}</span>
                            </div>
                        ` : ''}
                        ${drug.warnings ? `
                            <div class="alert alert-warning mb-0">
                                <strong><i class="bi bi-shield-exclamation"></i> 注意事項:</strong>
                                <p class="mb-0 mt-2">${drug.warnings}</p>
                            </div>
                        ` : ''}
                        <div class="text-end mt-2">
                            <small class="text-muted">情報源: ${drug.source}</small>
                        </div>
                    </div>
                </div>
            `;
        });
    }

    const modalHtml = `
        <div class="modal fade" id="drugInfoModal" tabindex="-1">
            <div class="modal-dialog modal-lg modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header bg-info text-white">
                        <h5 class="modal-title">
                            <i class="bi bi-info-circle"></i> 薬品情報
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <i class="bi bi-info-circle"></i>
                            <strong>免責事項:</strong>
                            この情報は参考情報です。必ず医師・薬剤師の指示に従ってください。
                        </div>
                        ${drugInfoHtml}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">閉じる</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 既存のモーダルを削除
    const existingModal = document.getElementById('drugInfoModal');
    if (existingModal) {
        existingModal.remove();
    }

    // モーダルを追加
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // モーダルを表示
    const modal = new bootstrap.Modal(document.getElementById('drugInfoModal'));
    modal.show();

    // モーダルが閉じられたときにDOMから削除
    document.getElementById('drugInfoModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}
