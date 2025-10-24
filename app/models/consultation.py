"""
相談記録モデル

利用者との相談内容を記録します。
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Consultation(Base):
    """
    相談記録モデル

    利用者との相談内容、対応記録を保持します。
    """
    __tablename__ = "consultations"

    # 主キー
    id = Column(Integer, primary_key=True, index=True, comment="相談記録ID")

    # 外部キー
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="利用者ID")
    staff_id = Column(Integer, ForeignKey("staffs.id"), nullable=False, index=True, comment="対応スタッフID")

    # 相談情報
    consultation_date = Column(Date, nullable=False, index=True, comment="相談日")
    consultation_type = Column(String(20), nullable=False, comment="相談形態（来所/訪問/電話/その他）")
    content = Column(Text, nullable=False, comment="相談内容")
    response = Column(Text, comment="対応内容")

    # 削除フラグ
    is_deleted = Column(Boolean, default=False, nullable=False, comment="削除フラグ")

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新日時")

    # リレーションシップ
    user = relationship("User", back_populates="consultations")
    staff = relationship("Staff", back_populates="consultations")

    def __repr__(self):
        return f"<Consultation(id={self.id}, user_id={self.user_id}, date={self.consultation_date}, type={self.consultation_type})>"


# 複合インデックスの定義
Index('idx_consultations_user_date', Consultation.user_id, Consultation.consultation_date)
Index('idx_consultations_staff_date', Consultation.staff_id, Consultation.consultation_date)
