from app.db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, TIMESTAMP, func, BigInteger


class ConfigGroup(Base):
    __tablename__ = "config_group"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(10), unique=True, nullable=False)
    group_unique_id = Column(String(100), nullable=False)

    is_deleted = Column(Integer, default=0)
    created_on = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer)

    updated_on = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
    updated_by = Column(Integer)

    deleted_on = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_by = Column(Integer)

    param = relationship(
        "ConfigParam", back_populates="group")
