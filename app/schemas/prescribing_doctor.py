"""処方医スキーマ"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PrescribingDoctorBase(BaseModel):
    """処方医基本スキーマ"""
    name: str = Field(..., max_length=100, description="医師名")
    hospital_name: Optional[str] = Field(None, max_length=200, description="医療機関名")
    department: Optional[str] = Field(None, max_length=100, description="診療科")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    address: Optional[str] = Field(None, description="住所")
    notes: Optional[str] = Field(None, description="備考")


class PrescribingDoctorCreate(PrescribingDoctorBase):
    """処方医作成スキーマ"""
    pass


class PrescribingDoctorUpdate(BaseModel):
    """処方医更新スキーマ"""
    name: Optional[str] = Field(None, max_length=100, description="医師名")
    hospital_name: Optional[str] = Field(None, max_length=200, description="医療機関名")
    department: Optional[str] = Field(None, max_length=100, description="診療科")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    address: Optional[str] = Field(None, description="住所")
    notes: Optional[str] = Field(None, description="備考")


class PrescribingDoctor(PrescribingDoctorBase):
    """処方医レスポンススキーマ"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
