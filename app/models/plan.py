"""
サービス利用計画モデル

計画相談支援における利用者のサービス利用計画を管理します。
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Plan(Base):
    """
    サービス利用計画モデル

    利用者のサービス利用計画書を管理します。
    初回計画と更新計画を区別し、計画の作成から承認までのライフサイクルを管理します。
    """
    __tablename__ = "plans"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="計画ID")

    # 関連情報
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="利用者ID")
    staff_id = Column(Integer, ForeignKey("staffs.id"), nullable=False, index=True, comment="作成者スタッフID")

    # 計画基本情報
    plan_type = Column(String(20), nullable=False, comment="計画種別（初回/更新）")
    plan_number = Column(String(50), unique=True, index=True, comment="計画番号（例: 2025-001）")
    created_date = Column(Date, nullable=False, comment="計画作成日")
    start_date = Column(Date, nullable=False, index=True, comment="計画開始日")
    end_date = Column(Date, nullable=False, index=True, comment="計画終了日")

    # 利用者の状況
    current_situation = Column(Text, comment="現在の状況")
    hopes_and_needs = Column(Text, comment="本人・家族の希望やニーズ")

    # 総合的な援助方針
    support_policy = Column(Text, comment="総合的な援助方針")

    # 目標設定
    long_term_goal = Column(Text, comment="長期目標")
    long_term_goal_period = Column(String(50), comment="長期目標期間（例: 6ヶ月）")
    short_term_goal = Column(Text, comment="短期目標")
    short_term_goal_period = Column(String(50), comment="短期目標期間（例: 3ヶ月）")

    # サービス内容（JSON形式で複数サービスを保存）
    # 例: [{"service_type": "生活介護", "provider": "事業所名", "frequency": "週5回", "hours": "6時間/日"}]
    services = Column(JSON, comment="サービス内容（JSON形式）")

    # 承認状況
    approval_status = Column(
        String(20),
        nullable=False,
        default="作成中",
        index=True,
        comment="承認状況（作成中/承認済み/実施中/終了）"
    )
    approval_date = Column(Date, comment="承認日")

    # 削除フラグ
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment="削除フラグ")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    user = relationship("User", back_populates="plans")
    staff = relationship("Staff", back_populates="plans")
    monitorings = relationship("Monitoring", back_populates="plan", cascade="all, delete-orphan")
    evaluations = relationship("PlanEvaluation", back_populates="plan", cascade="all, delete-orphan")

    @property
    def is_active(self):
        """
        計画が有効期間内かどうかを判定

        Returns:
            bool: 有効期間内ならTrue
        """
        if not self.start_date or not self.end_date:
            return False

        today = date.today()
        return self.start_date <= today <= self.end_date

    @property
    def can_edit(self):
        """
        編集可能かどうかを判定

        Returns:
            bool: 編集可能ならTrue（承認済みまたは実施中の計画は編集不可）
        """
        return self.approval_status == "作成中"

    def __repr__(self):
        return f"<Plan(id={self.id}, plan_number={self.plan_number}, user={self.user_id}, status={self.approval_status})>"
