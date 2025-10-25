from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class PrescribingDoctor(Base):
    """処方医情報モデル"""
    __tablename__ = "prescribing_doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="医師名")
    hospital_name = Column(String(200), comment="医療機関名")
    department = Column(String(100), comment="診療科")
    phone = Column(String(20), comment="電話番号")
    address = Column(Text, comment="住所")
    notes = Column(Text, comment="備考")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="登録日時")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新日時")

    def __repr__(self):
        return f"<PrescribingDoctor(id={self.id}, name={self.name}, hospital={self.hospital_name})>"
