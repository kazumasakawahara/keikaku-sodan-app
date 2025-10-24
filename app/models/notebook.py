"""
手帳モデル

療育手帳・精神障害者保健福祉手帳の情報を管理します。
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Notebook(Base):
    """
    手帳モデル

    利用者が保持する手帳（療育手帳、精神障害者保健福祉手帳）の情報を保持します。
    """
    __tablename__ = "notebooks"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="手帳ID")

    # 外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="利用者ID")

    # 手帳情報
    notebook_type = Column(String(50), nullable=False, comment="手帳種別（療育手帳/精神障害者保健福祉手帳）")
    grade = Column(String(20), comment="等級・程度")
    issue_date = Column(Date, comment="交付日")
    renewal_date = Column(Date, comment="更新日")
    notes = Column(Text, comment="備考")

    # 削除フラグ
    is_deleted = Column(Boolean, default=False, nullable=False, comment="削除フラグ")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    user = relationship("User", back_populates="notebooks")

    def __repr__(self):
        return f"<Notebook(id={self.id}, user_id={self.user_id}, type={self.notebook_type}, grade={self.grade})>"
