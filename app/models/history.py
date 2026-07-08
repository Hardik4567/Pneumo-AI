from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    BigInteger
)
from sqlalchemy.sql import func

from app.db.base_class import Base

from sqlalchemy.orm import relationship


class History(Base):
    __tablename__ = "history"

    history_id = Column(Integer, primary_key=True, index=True)

    # Logged-in user
    user_id = Column(
        BigInteger,
        ForeignKey("user_master.id"),
        nullable=True
    )

    # Patient Details
    patient_name = Column(String(100), nullable=False)
    patient_age = Column(Integer, nullable=False)
    patient_gender = Column(String(20), nullable=False)

    # X-ray Details
    image_name = Column(String(255), nullable=False)
    image_path = Column(String(500), nullable=True)

    # AI Prediction
    detected_disease = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)

    heatmap_path = Column(String(500), nullable=True)
    report_path = Column(String(500), nullable=True)

    processing_time = Column(Float, nullable=True)

    prediction_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("UserMaster", back_populates="history")


    reports = relationship(
        "Report",
        back_populates="history",
        cascade="all, delete-orphan"
    )