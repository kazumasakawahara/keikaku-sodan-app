"""処方医API"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.prescribing_doctor import PrescribingDoctor
from app.models.staff import Staff
from app.schemas.prescribing_doctor import (
    PrescribingDoctor as PrescribingDoctorSchema,
    PrescribingDoctorCreate,
    PrescribingDoctorUpdate
)
from app.api.auth import get_current_staff

router = APIRouter(prefix="/prescribing-doctors", tags=["prescribing_doctors"])


@router.get("", response_model=List[PrescribingDoctorSchema])
def list_prescribing_doctors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """処方医一覧取得"""
    doctors = db.query(PrescribingDoctor).offset(skip).limit(limit).all()
    return doctors


@router.get("/{doctor_id}", response_model=PrescribingDoctorSchema)
def get_prescribing_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """処方医詳細取得"""
    doctor = db.query(PrescribingDoctor).filter(PrescribingDoctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="処方医が見つかりません"
        )
    return doctor


@router.post("", response_model=PrescribingDoctorSchema, status_code=status.HTTP_201_CREATED)
def create_prescribing_doctor(
    doctor_data: PrescribingDoctorCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """処方医登録"""
    doctor = PrescribingDoctor(**doctor_data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.put("/{doctor_id}", response_model=PrescribingDoctorSchema)
def update_prescribing_doctor(
    doctor_id: int,
    doctor_data: PrescribingDoctorUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """処方医更新"""
    doctor = db.query(PrescribingDoctor).filter(PrescribingDoctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="処方医が見つかりません"
        )

    update_data = doctor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescribing_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """処方医削除"""
    doctor = db.query(PrescribingDoctor).filter(PrescribingDoctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="処方医が見つかりません"
        )

    db.delete(doctor)
    db.commit()
    return None
