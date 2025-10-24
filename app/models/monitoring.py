"""
モニタリング記録モデル

サービス利用計画のモニタリング記録を管理します。
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Monitoring(Base):
    """
    モニタリング記録モデル

    サービス利用計画に対するモニタリング（継続的な評価と見直し）の記録を管理します。
    """
    __tablename__ = "monitorings"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="モニタリングID")

    # 関連情報
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, index=True, comment="計画ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="利用者ID")
    staff_id = Column(Integer, ForeignKey("staffs.id"), nullable=False, index=True, comment="実施者スタッフID")

    # モニタリング基本情報
    monitoring_date = Column(Date, nullable=False, index=True, comment="モニタリング実施日")
    monitoring_type = Column(String(20), nullable=False, comment="モニタリング種別（定期/随時）")

    # モニタリング内容
    service_usage_status = Column(Text, comment="サービス利用状況")
    goal_achievement = Column(Text, comment="目標達成状況")
    satisfaction = Column(
        String(20),
        comment="満足度（満足/やや満足/普通/やや不満/不満）"
    )
    changes_in_needs = Column(Text, comment="ニーズの変化")
    issues_and_concerns = Column(Text, comment="課題・問題点")

    # 今後の方針
    future_policy = Column(Text, comment="今後の方針")
    plan_revision_needed = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="計画変更の必要性"
    )

    # 次回モニタリング予定
    next_monitoring_date = Column(Date, index=True, comment="次回モニタリング予定日")

    # 削除フラグ
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment="削除フラグ")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    plan = relationship("Plan", back_populates="monitorings")
    user = relationship("User", back_populates="monitorings")
    staff = relationship("Staff", back_populates="monitorings")

    @property
    def is_overdue(self):
        """
        次回モニタリングが期限超過しているかを判定

        Returns:
            bool: 期限超過ならTrue
        """
        if not self.next_monitoring_date:
            return False

        return date.today() > self.next_monitoring_date

    def __repr__(self):
        return f"<Monitoring(id={self.id}, plan_id={self.plan_id}, date={self.monitoring_date}, type={self.monitoring_type})>"
