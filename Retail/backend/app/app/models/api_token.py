from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime,Text,Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.types import TINYINT

class ApiTokens(Base):
    __tablename__ = "api_tokens"
    id=Column(Integer,primary_key=True)
    user_id=Column(Integer,ForeignKey("user.id"))
    
    token=Column(String(100))
    created_at=Column(DateTime)
    validity=Column(TINYINT(1),comment="0-Expired, 1- Lifetime", nullable=False)
    status=Column(TINYINT(1),comment="1-active, -1 inactive, 0- deleted", nullable=False)

    user=relationship("User",back_populates="api_tokens")
    