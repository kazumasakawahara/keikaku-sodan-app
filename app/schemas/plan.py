"""
サービス利用計画のスキーマ定義

APIリクエスト・レスポンスのデータ検証に使用します。
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class ServiceDetail(BaseModel):
    """サービス内容の詳細"""
    service_type: str = Field(..., description="サービス種別（例: 生活介護、就労継続支援B型）")
    provider: str = Field(..., description="提供事業所名")
    frequency: Optional[str] = Field(None, description="頻度（例: 週5回）")
    hours: Optional[str] = Field(None, description="時間（例: 6時間/日）")
    purpose: Optional[str] = Field(None, description="利用目的")


class PlanBase(BaseModel):
    """計画の基本情報"""
    user_id: int = Field(..., description="利用者ID")
    plan_type: str = Field(..., description="計画種別（初回/更新）")
    plan_number: str = Field(..., description="計画番号")
    created_date: date = Field(..., description="計画作成日")
    start_date: date = Field(..., description="計画開始日")
    end_date: date = Field(..., description="計画終了日")
    current_situation: Optional[str] = Field(None, description="現在の状況")
    hopes_and_needs: Optional[str] = Field(None, description="本人・家族の希望やニーズ")
    support_policy: Optional[str] = Field(None, description="総合的な援助方針")
    long_term_goal: Optional[str] = Field(None, description="長期目標")
    long_term_goal_period: Optional[str] = Field(None, description="長期目標期間")
    short_term_goal: Optional[str] = Field(None, description="短期目標")
    short_term_goal_period: Optional[str] = Field(None, description="短期目標期間")
    services: Optional[List[Dict[str, Any]]] = Field(None, description="サービス内容")

    @validator("plan_type")
    def validate_plan_type(cls, v):
        """計画種別のバリデーション"""
        if v not in ["初回", "更新"]:
            raise ValueError("計画種別は「初回」または「更新」である必要があります")
        return v

    @validator("end_date")
    def validate_dates(cls, v, values):
        """日付の整合性チェック"""
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("計画終了日は開始日より後である必要があります")
        return v


class PlanCreate(PlanBase):
    """計画作成時のリクエストスキーマ"""
    staff_id: int = Field(..., description="作成者スタッフID")


class PlanUpdate(BaseModel):
    """計画更新時のリクエストスキーマ"""
    plan_type: Optional[str] = None
    plan_number: Optional[str] = None
    created_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current_situation: Optional[str] = None
    hopes_and_needs: Optional[str] = None
    support_policy: Optional[str] = None
    long_term_goal: Optional[str] = None
    long_term_goal_period: Optional[str] = None
    short_term_goal: Optional[str] = None
    short_term_goal_period: Optional[str] = None
    services: Optional[List[Dict[str, Any]]] = None
    approval_status: Optional[str] = None
    approval_date: Optional[date] = None


class PlanResponse(PlanBase):
    """計画レスポンススキーマ"""
    id: int
    staff_id: int
    approval_status: str
    approval_date: Optional[date] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool
    can_edit: bool

    class Config:
        from_attributes = True


class PlanApprove(BaseModel):
    """計画承認のリクエストスキーマ"""
    approval_date: date = Field(..., description="承認日")
    approval_status: str = Field("承認済み", description="承認状況")

    @validator("approval_status")
    def validate_approval_status(cls, v):
        """承認状況のバリデーション"""
        if v not in ["承認済み", "実施中", "終了"]:
            raise ValueError("承認状況は「承認済み」「実施中」「終了」のいずれかである必要があります")
        return v
