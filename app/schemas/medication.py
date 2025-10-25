"""服薬情報スキーマ"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class MedicationBase(BaseModel):
    """服薬情報基本スキーマ"""
    medication_name: str = Field(..., max_length=200, description="薬品名")
    generic_name: Optional[str] = Field(None, max_length=200, description="一般名")
    dosage: Optional[str] = Field(None, max_length=100, description="用量")
    frequency: Optional[str] = Field(None, max_length=100, description="服用回数")
    timing: Optional[str] = Field(None, max_length=100, description="服用タイミング")
    start_date: Optional[date] = Field(None, description="服用開始日")
    end_date: Optional[date] = Field(None, description="服用終了日")
    is_current: bool = Field(True, description="現在服用中かどうか")
    purpose: Optional[str] = Field(None, description="処方目的")
    notes: Optional[str] = Field(None, description="備考")
    prescribing_doctor_id: Optional[int] = Field(None, description="処方医ID")


class MedicationCreate(MedicationBase):
    """服薬情報作成スキーマ"""
    user_id: int = Field(..., description="利用者ID")


class MedicationUpdate(BaseModel):
    """服薬情報更新スキーマ"""
    medication_name: Optional[str] = Field(None, max_length=200, description="薬品名")
    generic_name: Optional[str] = Field(None, max_length=200, description="一般名")
    dosage: Optional[str] = Field(None, max_length=100, description="用量")
    frequency: Optional[str] = Field(None, max_length=100, description="服用回数")
    timing: Optional[str] = Field(None, max_length=100, description="服用タイミング")
    start_date: Optional[date] = Field(None, description="服用開始日")
    end_date: Optional[date] = Field(None, description="服用終了日")
    is_current: Optional[bool] = Field(None, description="現在服用中かどうか")
    purpose: Optional[str] = Field(None, description="処方目的")
    notes: Optional[str] = Field(None, description="備考")
    prescribing_doctor_id: Optional[int] = Field(None, description="処方医ID")


class Medication(MedicationBase):
    """服薬情報レスポンススキーマ"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MedicationWithDoctor(Medication):
    """処方医情報を含む服薬情報スキーマ"""
    prescribing_doctor_name: Optional[str] = None
    prescribing_doctor_hospital: Optional[str] = None

    class Config:
        from_attributes = True
