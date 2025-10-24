"""
関係機関モデル

サービス事業所、医療機関、後見人などの関係機関情報を管理します。
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Organization(Base):
    """
    関係機関モデル

    利用者に関係する事業所、医療機関、後見人などの情報を保持します。
    """
    __tablename__ = "organizations"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="関係機関ID")

    # 基本情報
    name = Column(String(255), nullable=False, index=True, comment="機関名")
    type = Column(String(50), nullable=False, index=True, comment="種別（サービス事業所/医療機関/後見人/その他）")

    # 連絡先情報
    postal_code = Column(String(10), comment="郵便番号")
    address = Column(String(255), comment="住所")
    phone = Column(String(20), comment="電話番号")
    fax = Column(String(20), comment="FAX番号")
    email = Column(String(255), comment="メールアドレス")

    # 担当者情報
    contact_person = Column(String(100), comment="担当者氏名")
    contact_person_phone = Column(String(20), comment="担当者電話番号")

    # その他
    notes = Column(Text, comment="備考")

    # 削除フラグ
    is_deleted = Column(Boolean, default=False, nullable=False, comment="削除フラグ")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    user_organizations = relationship("UserOrganization", back_populates="organization")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, type={self.type})>"
