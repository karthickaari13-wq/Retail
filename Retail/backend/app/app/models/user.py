
from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime,Text,Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.types import TINYINT

class User(Base):
    __tablename__ = "user"
    id = Column(Integer,primary_key=True)
    userType =Column(TINYINT,comment="1->SuperAdmin,2->owner,3->cashier,4 ->labour")
    name = Column(String(200))
    email = Column(String(255))
    phone = Column(String(20))
    password=Column(String(200))
    address=Column(String(20))
    language=Column(String(20))
    otp = Column(String(20))
    otpExpireAt = Column(DateTime)
    otpVerifiedStatus = Column(TINYINT, default = 0, comment="0->No, 1->Yes")
    otp_verified_at = Column(DateTime)
    created_at=Column(DateTime)
    latitude = Column(String(20))
    longitude = Column(String(20))
    pincode = Column(Integer)
    country = Column(String(20))
    city = Column(String(20))

    store_id=Column(Integer,ForeignKey("stores.id"))
    updated_at=Column(DateTime)
    status=Column(TINYINT,comment="-1->delete,1->active,0->inactive")

    api_tokens=relationship("ApiTokens",back_populates="user")
    orders=relationship("Order",back_populates="user")
    stores=relationship("Store",back_populates="user")
    supplierorders=relationship("SupplierOrder",back_populates="user")
    userotp=relationship("UserOtp",back_populates="user")
