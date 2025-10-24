"""
利用者-関係機関スキーマ

利用者と関係機関の紐付け関連のPydanticモデルを定義します。
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserOrganizationBase(BaseModel):
    """利用者-関係機関基本スキーマ"""
    relationship_type: Optional[str] = Field(None, max_length=50, description="関係種別")
    start_date: Optional[date] = Field(None, description="利用開始日")
    end_date: Optional[date] = Field(None, description="利用終了日")
    frequency: Optional[str] = Field(None, max_length=50, description="頻度")
    notes: Optional[str] = Field(None, description="備考")


class UserOrganizationCreate(UserOrganizationBase):
    """利用者-関係機関作成スキーマ"""
    user_id: int = Field(..., description="利用者ID")
    organization_id: int = Field(..., description="関係機関ID")


class UserOrganizationResponse(UserOrganizationBase):
    """利用者-関係機関レスポンススキーマ"""
    id: int
    user_id: int
    organization_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
