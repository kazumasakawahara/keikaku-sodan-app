"""
利用者モデル

計画相談支援の利用者情報を管理します。
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):
    """
    利用者モデル

    計画相談支援を利用する方の基本情報を保持します。
    """
    __tablename__ = "users"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="利用者ID")

    # 基本情報
    name = Column(String(100), nullable=False, index=True, comment="氏名")
    name_kana = Column(String(100), comment="氏名（カナ）")
    birth_date = Column(Date, nullable=False, index=True, comment="生年月日")
    gender = Column(String(10), comment="性別")

    # 連絡先情報
    postal_code = Column(String(10), comment="郵便番号")
    address = Column(String(255), comment="住所")
    phone = Column(String(20), comment="電話番号")
    email = Column(String(255), comment="メールアドレス")

    # 緊急連絡先
    emergency_contact_name = Column(String(100), comment="緊急連絡先氏名")
    emergency_contact_phone = Column(String(20), comment="緊急連絡先電話番号")

    # 障害支援区分
    disability_support_level = Column(Integer, comment="障害支援区分 (1-6)")
    disability_support_certified_date = Column(Date, comment="障害支援区分認定日")
    disability_support_expiry_date = Column(Date, comment="障害支援区分有効期限")

    # 後見人情報
    guardian_type = Column(String(50), comment="後見人種別（成年後見人/保佐人/補助人）")
    guardian_name = Column(String(100), comment="後見人氏名")
    guardian_contact = Column(String(255), comment="後見人連絡先")

    # 担当スタッフ
    assigned_staff_id = Column(Integer, ForeignKey("staffs.id"), index=True, comment="担当スタッフID")

    # 削除フラグ
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment="削除フラグ")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    assigned_staff = relationship("Staff", back_populates="users", foreign_keys=[assigned_staff_id])
    notebooks = relationship("Notebook", back_populates="user")
    consultations = relationship("Consultation", back_populates="user")
    user_organizations = relationship("UserOrganization", back_populates="user")
    plans = relationship("Plan", back_populates="user")
    monitorings = relationship("Monitoring", back_populates="user")
    medications = relationship("Medication", back_populates="user")

    @property
    def age(self):
        """
        年齢を計算して返す

        Returns:
            int: 年齢
        """
        if not self.birth_date:
            return None

        today = date.today()
        age = today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
        return age

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age})>"


# インデックス定義
# SQLAlchemyでは、index=Trueをカラム定義に含めることで自動的にインデックスが作成されます
# 複合インデックスが必要な場合は、以下のようにIndex()を使用します
# from sqlalchemy import Index
# Index('idx_users_name_birth', User.name, User.birth_date)
