"""
スタッフスキーマ

スタッフ関連のPydanticモデルを定義します。
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class StaffBase(BaseModel):
    """スタッフ基本スキーマ"""
    name: str = Field(..., min_length=1, max_length=100, description="氏名")
    email: Optional[EmailStr] = Field(None, description="メールアドレス")
    role: str = Field(default="staff", pattern="^(admin|staff)$", description="権限")
    hire_date: Optional[date] = Field(None, description="採用年月日")
    qualifications: Optional[List[str]] = Field(None, description="資格リスト")
    resignation_date: Optional[date] = Field(None, description="退職日")


class StaffCreate(StaffBase):
    """スタッフ作成スキーマ"""
    username: str = Field(..., min_length=3, max_length=100, description="ログインユーザー名")
    password: str = Field(..., min_length=6, description="パスワード")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """パスワードの検証"""
        if len(v) < 6:
            raise ValueError("パスワードは6文字以上である必要があります")
        return v


class StaffUpdate(BaseModel):
    """スタッフ更新スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|staff)$")
    is_active: Optional[bool] = None
    hire_date: Optional[date] = None
    qualifications: Optional[List[str]] = None
    resignation_date: Optional[date] = None


class StaffPasswordChange(BaseModel):
    """パスワード変更スキーマ"""
    current_password: str = Field(..., description="現在のパスワード")
    new_password: str = Field(..., min_length=6, description="新しいパスワード")


class StaffResponse(StaffBase):
    """スタッフレスポンススキーマ"""
    id: int
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj):
        """モデル変換時にqualificationsをリストに変換"""
        if hasattr(obj, 'qualifications') and obj.qualifications:
            if isinstance(obj.qualifications, str):
                obj.qualifications = [q.strip() for q in obj.qualifications.split(',') if q.strip()]
        return super().model_validate(obj)


class StaffLogin(BaseModel):
    """ログインスキーマ"""
    username: str = Field(..., min_length=1, description="ユーザー名")
    password: str = Field(..., min_length=1, description="パスワード")


class StaffLoginResponse(StaffResponse):
    """ログインレスポンススキーマ"""
    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")
