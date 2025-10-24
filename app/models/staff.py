"""
スタッフモデル

相談支援専門員の情報を管理します。
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Staff(Base):
    """
    スタッフモデル

    相談支援専門員と管理者の情報を保持します。
    """
    __tablename__ = "staffs"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="スタッフID")

    # 認証情報
    username = Column(String(100), unique=True, nullable=False, index=True, comment="ログインユーザー名")
    password_hash = Column(String(255), nullable=False, comment="パスワードハッシュ")

    # 基本情報
    name = Column(String(100), nullable=False, comment="氏名")
    role = Column(String(20), nullable=False, default="staff", comment="権限 (admin/staff)")
    email = Column(String(255), comment="メールアドレス")

    # ステータス
    is_active = Column(Boolean, default=True, nullable=False, comment="有効フラグ")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    users = relationship("User", back_populates="assigned_staff", foreign_keys="User.assigned_staff_id")
    consultations = relationship("Consultation", back_populates="staff")
    plans = relationship("Plan", back_populates="staff")
    monitorings = relationship("Monitoring", back_populates="staff")

    def __repr__(self):
        return f"<Staff(id={self.id}, username={self.username}, name={self.name}, role={self.role})>"
