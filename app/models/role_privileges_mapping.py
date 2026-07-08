from app.db.base_class import Base
from sqlalchemy import Column, Integer, TIMESTAMP, func, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

class RolePrivilegesMapping(Base):
    __tablename__ = "role_privileges_mapping"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger,ForeignKey("role_master.id"), nullable=False)
    privilege_id = Column(BigInteger,ForeignKey("privileges_master.id"), nullable=False)
    is_deleted = Column(Integer, default=0)
    created_on = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer)

    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(BigInteger)

    deleted_on = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(BigInteger)

    role = relationship("RoleMaster")
    privilege = relationship("PrivilegesMaster", back_populates="role_mappings")

