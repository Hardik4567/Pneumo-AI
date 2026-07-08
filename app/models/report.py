from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func
)

from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Report(Base):
    __tablename__ = "report"

    report_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    history_id = Column(
        Integer,
        ForeignKey("history.history_id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("user_master.id"),
        nullable=False
    )

    report_name = Column(
        String(255),
        nullable=False
    )

    report_path = Column(
        String(500),
        nullable=False
    )

    report_type = Column(
        String(50),
        default="PDF"
    )

    created_on = Column(
        DateTime,
        server_default=func.now()
    )

    updated_on = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    history = relationship(
        "History",
        back_populates="reports"
    )

    user = relationship(
        "UserMaster",
        back_populates="reports"
    )