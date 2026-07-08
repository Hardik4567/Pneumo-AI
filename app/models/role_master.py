from app.db.base_class import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, func, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

class RoleMaster(Base):
    __tablename__ = "role_master"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_unique_id = Column(String(255), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), unique=True, nullable=False)
    is_restricted = Column(Integer, default=0)
    is_deleted = Column(Integer, default=0)
    created_on = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer)

    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(BigInteger)

    deleted_on = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(BigInteger)

    users = relationship("UserMaster", back_populates="role")

