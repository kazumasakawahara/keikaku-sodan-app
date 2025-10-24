"""
関係機関スキーマ

関係機関関連のPydanticモデルを定義します。
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class OrganizationBase(BaseModel):
    """関係機関基本スキーマ"""
    name: str = Field(..., min_length=1, max_length=255, description="機関名")
    type: str = Field(..., description="種別")
    postal_code: Optional[str] = Field(None, max_length=10, description="郵便番号")
    address: Optional[str] = Field(None, max_length=255, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    fax: Optional[str] = Field(None, max_length=20, description="FAX番号")
    email: Optional[EmailStr] = Field(None, description="メールアドレス")
    contact_person: Optional[str] = Field(None, max_length=100, description="担当者氏名")
    contact_person_phone: Optional[str] = Field(None, max_length=20, description="担当者電話番号")
    notes: Optional[str] = Field(None, description="備考")


class OrganizationCreate(OrganizationBase):
    """関係機関作成スキーマ"""
    pass


class OrganizationUpdate(BaseModel):
    """関係機関更新スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    postal_code: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    fax: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_person_phone: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    """関係機関レスポンススキーマ"""
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
