from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class Medication(Base):
    """服薬情報モデル"""
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="利用者ID")
    prescribing_doctor_id = Column(Integer, ForeignKey("prescribing_doctors.id", ondelete="SET NULL"), comment="処方医ID")

    medication_name = Column(String(200), nullable=False, comment="薬品名")
    generic_name = Column(String(200), comment="一般名")
    dosage = Column(String(100), comment="用量 (例: 1錠)")
    frequency = Column(String(100), comment="服用回数 (例: 1日3回)")
    timing = Column(String(100), comment="服用タイミング (例: 食後)")

    start_date = Column(Date, comment="服用開始日")
    end_date = Column(Date, comment="服用終了日")
    is_current = Column(Boolean, default=True, comment="現在服用中かどうか")

    purpose = Column(Text, comment="処方目的")
    notes = Column(Text, comment="備考")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="登録日時")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新日時")

    # リレーションシップ
    user = relationship("User", back_populates="medications")
    prescribing_doctor = relationship("PrescribingDoctor")
    changes = relationship("MedicationChange", back_populates="medication", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Medication(id={self.id}, name={self.medication_name}, user_id={self.user_id})>"
