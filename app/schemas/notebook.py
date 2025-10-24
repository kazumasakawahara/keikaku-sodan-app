"""
手帳スキーマ

手帳関連のPydanticモデルを定義します。
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotebookBase(BaseModel):
    """手帳基本スキーマ"""
    notebook_type: str = Field(..., description="手帳種別")
    grade: Optional[str] = Field(None, max_length=20, description="等級・程度")
    issue_date: Optional[date] = Field(None, description="交付日")
    renewal_date: Optional[date] = Field(None, description="更新日")
    notes: Optional[str] = Field(None, description="備考")


class NotebookCreate(NotebookBase):
    """手帳作成スキーマ"""
    user_id: int = Field(..., description="利用者ID")


class NotebookUpdate(BaseModel):
    """手帳更新スキーマ"""
    notebook_type: Optional[str] = None
    grade: Optional[str] = Field(None, max_length=20)
    issue_date: Optional[date] = None
    renewal_date: Optional[date] = None
    notes: Optional[str] = None


class NotebookResponse(NotebookBase):
    """手帳レスポンススキーマ"""
    id: int
    user_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
