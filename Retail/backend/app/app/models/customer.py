from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class Customer(Base):
    __tablename__="customers"
    id=Column(Integer,primary_key=True)
    name=Column(String(20))
    mobile=Column(Integer)
    address=Column(Integer)
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    status=Column(Integer,comment="1 active, 0 delete")
    orders=relationship("Order",back_populates="customers")