from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class MedicationChange(Base):
    """服薬変更履歴モデル"""
    __tablename__ = "medication_changes"

    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, comment="服薬情報ID")

    change_date = Column(Date, nullable=False, comment="変更日")
    change_type = Column(String(50), nullable=False, comment="変更種別 (新規/変更/中止)")
    previous_value = Column(Text, comment="変更前の内容")
    new_value = Column(Text, comment="変更後の内容")
    reason = Column(Text, comment="変更理由")
    notes = Column(Text, comment="備考")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="登録日時")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新日時")

    # リレーションシップ
    medication = relationship("Medication", back_populates="changes")

    def __repr__(self):
        return f"<MedicationChange(id={self.id}, type={self.change_type}, date={self.change_date})>"
