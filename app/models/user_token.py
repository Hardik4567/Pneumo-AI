from sqlalchemy import event
from app.db.base_class import Base
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

class UserToken(Base):
    __tablename__ = "user_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user_master.id"), nullable=False)
    otp = Column(String(6), nullable=True)
    token = Column(String(500), nullable=True)
    token_type = Column(String(20), nullable=False, default="REFRESH")
    is_revoked = Column(Integer, default=0)
    exp_date = Column(TIMESTAMP, nullable=False, index=True)
    created_on = Column(TIMESTAMP, nullable=False, server_default=func.now())
    user = relationship("UserMaster", back_populates="tokens")


# ✅ Automatically set exp_date = created_on + 2 minutes before insert
@event.listens_for(UserToken, "before_insert")
def set_expiry_date(mapper, connection, target):
    if not target.created_on:
        target.created_on = datetime.now()
    if target.token_type == "OTP":
        target.exp_date = target.created_on + timedelta(minutes=2)
    elif target.token_type == "ACCESS":
        target.exp_date = target.created_on + timedelta(minutes=15)
    else:
        target.exp_date = target.created_on + timedelta(days=7)
