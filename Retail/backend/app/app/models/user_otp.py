from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime,Text,Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.types import TINYINT

class UserOtp(Base):
    __tablename__ = "userotp"
    id = Column(Integer,primary_key=True)
    otp = Column(String(20))
    otpExpireAt = Column(DateTime)
    otpVerifiedStatus = Column(TINYINT, default = 0, comment="0->No, 1->Yes")
    otp_verified_at = Column(DateTime)
    created_at=Column(DateTime)
    user_id=Column(Integer,ForeignKey("user.id"))
    updated_at=Column(DateTime)
    status=Column(TINYINT,comment="-1->delete,1->active,0->inactive")
    user=relationship("User",back_populates="userotp")