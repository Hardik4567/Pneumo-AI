from app.db.base_class import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, func, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

class PrivilegesMaster(Base):
    __tablename__ = "privileges_master"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    privilege_unique_id = Column(String(255), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), unique=True, nullable=False)
    menu_id = Column(BigInteger,ForeignKey("menu_hierarchy.id"), nullable=False)
    is_deleted = Column(Integer, default=0)
    created_on = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer)

    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(BigInteger)

    deleted_on = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(BigInteger)

    role_mappings = relationship("RolePrivilegesMapping", back_populates="privilege")

