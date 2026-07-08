from app.db.base_class import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, func, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

class UserMaster(Base):
    __tablename__ = "user_master"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger, ForeignKey("role_master.id"), nullable=False)

    full_name = Column(String(255), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email_id = Column(String(100), unique=True, nullable=False, index=True)
    mobile_number = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    profile_image = Column(String(255), nullable=True)

    is_active = Column(Integer, default=1)
    is_deleted = Column(Integer, default=0)
    email_verified = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)

    last_login = Column(TIMESTAMP, nullable=True)
    account_locked_until = Column(TIMESTAMP, nullable=True)

    created_on = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(BigInteger)

    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(BigInteger)

    deleted_on = Column(TIMESTAMP, nullable=True, default=None)
    deleted_by = Column(BigInteger)

    role = relationship("RoleMaster", back_populates="users")
    history = relationship("History", back_populates="user", cascade="all, delete-orphan")
    tokens = relationship("UserToken", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")