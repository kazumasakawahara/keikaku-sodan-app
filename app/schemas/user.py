"""
利用者スキーマ

利用者関連のPydanticモデルを定義します。
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """利用者基本スキーマ"""
    name: str = Field(..., min_length=1, max_length=100, description="氏名")
    name_kana: Optional[str] = Field(None, max_length=100, description="氏名（カナ）")
    birth_date: date = Field(..., description="生年月日")
    gender: Optional[str] = Field(None, pattern="^(男性|女性|その他)$", description="性別")
    postal_code: Optional[str] = Field(None, max_length=10, description="郵便番号")
    address: Optional[str] = Field(None, max_length=255, description="住所")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    email: Optional[EmailStr] = Field(None, description="メールアドレス")
    emergency_contact_name: Optional[str] = Field(None, max_length=100, description="緊急連絡先氏名")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="緊急連絡先電話番号")
    disability_support_level: Optional[int] = Field(None, ge=1, le=6, description="障害支援区分")
    disability_support_certified_date: Optional[date] = Field(None, description="障害支援区分認定日")
    disability_support_expiry_date: Optional[date] = Field(None, description="障害支援区分有効期限")
    disability_characteristics: Optional[str] = Field(None, description="障害特性")
    interest_bias: Optional[str] = Field(None, description="興味の偏り")
    guardian_type: Optional[str] = Field(None, max_length=50, description="後見人種別")
    guardian_name: Optional[str] = Field(None, max_length=100, description="後見人氏名")
    guardian_contact: Optional[str] = Field(None, max_length=255, description="後見人連絡先")
    assigned_staff_id: Optional[int] = Field(None, description="担当スタッフID")


class UserCreate(UserBase):
    """利用者作成スキーマ"""
    pass


class UserUpdate(BaseModel):
    """利用者更新スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_kana: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(男性|女性|その他)$")
    postal_code: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    disability_support_level: Optional[int] = Field(None, ge=1, le=6)
    disability_support_certified_date: Optional[date] = None
    disability_support_expiry_date: Optional[date] = None
    disability_characteristics: Optional[str] = None
    interest_bias: Optional[str] = None
    guardian_type: Optional[str] = Field(None, max_length=50)
    guardian_name: Optional[str] = Field(None, max_length=100)
    guardian_contact: Optional[str] = Field(None, max_length=255)
    assigned_staff_id: Optional[int] = None


class UserResponse(UserBase):
    """利用者レスポンススキーマ"""
    id: int
    age: Optional[int] = Field(None, description="年齢")
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """利用者一覧レスポンススキーマ"""
    id: int
    name: str
    name_kana: Optional[str]
    age: Optional[int]
    birth_date: Optional[date]
    gender: Optional[str]
    phone: Optional[str]
    assigned_staff_id: Optional[int]
    disability_support_level: Optional[int]
    is_deleted: bool

    class Config:
        from_attributes = True
