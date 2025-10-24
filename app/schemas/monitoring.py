"""
モニタリング記録のスキーマ定義

APIリクエスト・レスポンスのデータ検証に使用します。
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class MonitoringBase(BaseModel):
    """モニタリングの基本情報"""
    plan_id: int = Field(..., description="計画ID")
    user_id: int = Field(..., description="利用者ID")
    monitoring_date: date = Field(..., description="モニタリング実施日")
    monitoring_type: str = Field(..., description="モニタリング種別（定期/随時）")
    service_usage_status: Optional[str] = Field(None, description="サービス利用状況")
    goal_achievement: Optional[str] = Field(None, description="目標達成状況")
    satisfaction: Optional[str] = Field(None, description="満足度")
    changes_in_needs: Optional[str] = Field(None, description="ニーズの変化")
    issues_and_concerns: Optional[str] = Field(None, description="課題・問題点")
    future_policy: Optional[str] = Field(None, description="今後の方針")
    plan_revision_needed: bool = Field(False, description="計画変更の必要性")
    next_monitoring_date: Optional[date] = Field(None, description="次回モニタリング予定日")

    @validator("monitoring_type")
    def validate_monitoring_type(cls, v):
        """モニタリング種別のバリデーション"""
        if v not in ["定期", "随時"]:
            raise ValueError("モニタリング種別は「定期」または「随時」である必要があります")
        return v

    @validator("satisfaction")
    def validate_satisfaction(cls, v):
        """満足度のバリデーション"""
        if v is not None and v not in ["満足", "やや満足", "普通", "やや不満", "不満"]:
            raise ValueError("満足度は「満足」「やや満足」「普通」「やや不満」「不満」のいずれかである必要があります")
        return v

    @validator("next_monitoring_date")
    def validate_next_monitoring_date(cls, v, values):
        """次回モニタリング日のバリデーション"""
        if v is not None and "monitoring_date" in values and v <= values["monitoring_date"]:
            raise ValueError("次回モニタリング予定日は実施日より後である必要があります")
        return v


class MonitoringCreate(MonitoringBase):
    """モニタリング作成時のリクエストスキーマ"""
    staff_id: int = Field(..., description="実施者スタッフID")


class MonitoringUpdate(BaseModel):
    """モニタリング更新時のリクエストスキーマ"""
    monitoring_date: Optional[date] = None
    monitoring_type: Optional[str] = None
    service_usage_status: Optional[str] = None
    goal_achievement: Optional[str] = None
    satisfaction: Optional[str] = None
    changes_in_needs: Optional[str] = None
    issues_and_concerns: Optional[str] = None
    future_policy: Optional[str] = None
    plan_revision_needed: Optional[bool] = None
    next_monitoring_date: Optional[date] = None


class MonitoringResponse(MonitoringBase):
    """モニタリングレスポンススキーマ"""
    id: int
    staff_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    is_overdue: bool

    class Config:
        from_attributes = True
