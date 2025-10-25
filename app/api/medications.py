"""服薬情報API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models.medication import Medication
from app.models.prescribing_doctor import PrescribingDoctor
from app.models.user import User
from app.models.staff import Staff
from app.schemas.medication import (
    Medication as MedicationSchema,
    MedicationCreate,
    MedicationUpdate,
    MedicationWithDoctor
)
from app.api.auth import get_current_staff

router = APIRouter(prefix="/medications", tags=["medications"])


@router.get("", response_model=List[MedicationWithDoctor])
def list_medications(
    user_id: Optional[int] = Query(None, description="利用者IDで絞り込み"),
    is_current: Optional[bool] = Query(None, description="現在服用中のみ"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """服薬情報一覧取得"""
    query = db.query(Medication).options(joinedload(Medication.prescribing_doctor))

    if user_id is not None:
        query = query.filter(Medication.user_id == user_id)

    if is_current is not None:
        query = query.filter(Medication.is_current == is_current)

    medications = query.order_by(Medication.start_date.desc()).offset(skip).limit(limit).all()

    # 処方医情報を含めたレスポンスを作成
    result = []
    for med in medications:
        med_dict = {
            **MedicationSchema.model_validate(med).model_dump(),
            "prescribing_doctor_name": med.prescribing_doctor.name if med.prescribing_doctor else None,
            "prescribing_doctor_hospital": med.prescribing_doctor.hospital_name if med.prescribing_doctor else None
        }
        result.append(MedicationWithDoctor(**med_dict))

    return result


@router.get("/{medication_id}", response_model=MedicationWithDoctor)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """服薬情報詳細取得"""
    medication = db.query(Medication).options(
        joinedload(Medication.prescribing_doctor)
    ).filter(Medication.id == medication_id).first()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服薬情報が見つかりません"
        )

    med_dict = {
        **MedicationSchema.model_validate(medication).model_dump(),
        "prescribing_doctor_name": medication.prescribing_doctor.name if medication.prescribing_doctor else None,
        "prescribing_doctor_hospital": medication.prescribing_doctor.hospital_name if medication.prescribing_doctor else None
    }

    return MedicationWithDoctor(**med_dict)


@router.post("", response_model=MedicationSchema, status_code=status.HTTP_201_CREATED)
def create_medication(
    medication_data: MedicationCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """服薬情報登録"""
    # 利用者の存在確認
    user = db.query(User).filter(User.id == medication_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="利用者が見つかりません"
        )

    # 処方医の存在確認（指定されている場合）
    if medication_data.prescribing_doctor_id:
        doctor = db.query(PrescribingDoctor).filter(
            PrescribingDoctor.id == medication_data.prescribing_doctor_id
        ).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="処方医が見つかりません"
            )

    medication = Medication(**medication_data.model_dump())
    db.add(medication)
    db.commit()
    db.refresh(medication)
    return medication


@router.put("/{medication_id}", response_model=MedicationSchema)
def update_medication(
    medication_id: int,
    medication_data: MedicationUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """服薬情報更新"""
    from app.models.medication_change import MedicationChange
    from datetime import date

    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服薬情報が見つかりません"
        )

    # 処方医の存在確認（指定されている場合）
    if medication_data.prescribing_doctor_id is not None:
        doctor = db.query(PrescribingDoctor).filter(
            PrescribingDoctor.id == medication_data.prescribing_doctor_id
        ).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="処方医が見つかりません"
            )

    # 変更履歴の記録（更新される各フィールドについて）
    update_data = medication_data.model_dump(exclude_unset=True)
    change_date = date.today()

    for field, new_value in update_data.items():
        old_value = getattr(medication, field, None)

        # 値が変更された場合のみ履歴を記録
        if old_value != new_value:
            change_type = _get_change_type(field)

            # 変更履歴レコードを作成
            medication_change = MedicationChange(
                medication_id=medication_id,
                change_date=change_date,
                change_type=change_type,
                previous_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None,
                notes=f"{_get_field_label(field)}の変更"
            )
            db.add(medication_change)

    # 服薬情報を更新
    for field, value in update_data.items():
        setattr(medication, field, value)

    db.commit()
    db.refresh(medication)
    return medication


def _get_change_type(field: str) -> str:
    """フィールド名から変更タイプを取得"""
    change_type_map = {
        'medication_name': '薬品名変更',
        'generic_name': '一般名変更',
        'dosage': '用量変更',
        'frequency': '服用回数変更',
        'timing': '服用タイミング変更',
        'start_date': '開始日変更',
        'end_date': '終了日変更',
        'is_current': '服用状態変更',
        'purpose': '処方目的変更',
        'notes': '備考変更',
        'prescribing_doctor_id': '処方医変更'
    }
    return change_type_map.get(field, 'その他の変更')


def _get_field_label(field: str) -> str:
    """フィールド名から日本語ラベルを取得"""
    label_map = {
        'medication_name': '薬品名',
        'generic_name': '一般名',
        'dosage': '用量',
        'frequency': '服用回数',
        'timing': '服用タイミング',
        'start_date': '開始日',
        'end_date': '終了日',
        'is_current': '服用状態',
        'purpose': '処方目的',
        'notes': '備考',
        'prescribing_doctor_id': '処方医'
    }
    return label_map.get(field, field)


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """服薬情報削除"""
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服薬情報が見つかりません"
        )

    db.delete(medication)
    db.commit()
    return None
