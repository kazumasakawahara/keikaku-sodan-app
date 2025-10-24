"""
相談記録スキーマ

相談記録関連のPydanticモデルを定義します。
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class ConsultationBase(BaseModel):
    """相談記録基本スキーマ"""
    consultation_date: date = Field(..., description="相談日")
    consultation_type: str = Field(..., pattern="^(来所|訪問|電話|その他)$", description="相談形態")
    content: str = Field(..., min_length=1, description="相談内容")
    response: Optional[str] = Field(None, description="対応内容")


class ConsultationCreate(ConsultationBase):
    """相談記録作成スキーマ"""
    user_id: int = Field(..., description="利用者ID")
    staff_id: int = Field(..., description="対応スタッフID")


class ConsultationUpdate(BaseModel):
    """相談記録更新スキーマ"""
    consultation_date: Optional[date] = None
    consultation_type: Optional[str] = Field(None, pattern="^(来所|訪問|電話|その他)$")
    content: Optional[str] = Field(None, min_length=1)
    response: Optional[str] = None


class ConsultationResponse(ConsultationBase):
    """相談記録レスポンススキーマ"""
    id: int
    user_id: int
    staff_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
