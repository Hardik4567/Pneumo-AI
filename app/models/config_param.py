from app.db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, TIMESTAMP, func, BigInteger, ForeignKey


class ConfigParam(Base):
    __tablename__ = "config_param"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(10), unique=True, nullable=False)
    config_group_id = Column(BigInteger, ForeignKey("config_group.id"), nullable=False)
    param_unique_id = Column(String(255), default=0)
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

    group = relationship(
        "ConfigGroup", foreign_keys=[config_group_id], back_populates="param")