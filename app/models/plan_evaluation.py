"""
計画評価モデル

サービス利用計画の達成状況を管理します。
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.connection import Base


class PlanEvaluation(Base):
    """
    計画評価モデル

    サービス利用計画の達成状況や評価を記録します。
    """
    __tablename__ = "plan_evaluations"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="評価ID")

    # 外部キー
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, index=True, comment="計画ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="利用者ID")
    staff_id = Column(Integer, ForeignKey("staffs.id"), nullable=False, comment="評価者スタッフID")

    # 評価情報
    evaluation_date = Column(Date, nullable=False, index=True, comment="評価日")
    achievement_status = Column(String(50), nullable=False, comment="達成状況 (達成/一部達成/未達成/継続中)")
    achievement_details = Column(Text, comment="達成状況詳細")

    # 各目標の達成度
    goal_1_achievement = Column(String(50), comment="目標1達成度")
    goal_1_notes = Column(Text, comment="目標1備考")
    goal_2_achievement = Column(String(50), comment="目標2達成度")
    goal_2_notes = Column(Text, comment="目標2備考")
    goal_3_achievement = Column(String(50), comment="目標3達成度")
    goal_3_notes = Column(Text, comment="目標3備考")

    # 総合評価
    overall_evaluation = Column(Text, comment="総合評価")
    challenges = Column(Text, comment="課題・問題点")
    next_actions = Column(Text, comment="次期計画への提言")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    plan = relationship("Plan", back_populates="evaluations")
    user = relationship("User")
    staff = relationship("Staff")

    def __repr__(self):
        return f"<PlanEvaluation(id={self.id}, plan_id={self.plan_id}, status={self.achievement_status})>"
