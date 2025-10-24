"""
利用者-関係機関中間テーブルモデル

利用者と関係機関の紐付けと関係性を管理します。
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.connection import Base


class UserOrganization(Base):
    """
    利用者-関係機関中間テーブルモデル

    利用者と関係機関の関連情報（利用状況、頻度など）を保持します。
    """
    __tablename__ = "user_organizations"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="ID")

    # 外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="利用者ID")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True, comment="関係機関ID")

    # 関係情報
    relationship_type = Column(String(50), comment="関係種別（通所/入院/主治医/後見人など）")
    start_date = Column(Date, comment="利用開始日")
    end_date = Column(Date, comment="利用終了日")
    frequency = Column(String(50), comment="頻度（週5日/月2回など）")
    notes = Column(Text, comment="備考")

    # 削除フラグ
    is_deleted = Column(Boolean, default=False, nullable=False, comment="削除フラグ")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    user = relationship("User", back_populates="user_organizations")
    organization = relationship("Organization", back_populates="user_organizations")

    def __repr__(self):
        return f"<UserOrganization(id={self.id}, user_id={self.user_id}, organization_id={self.organization_id}, type={self.relationship_type})>"


# 複合インデックスの定義
Index('idx_user_organizations_user_org', UserOrganization.user_id, UserOrganization.organization_id)
