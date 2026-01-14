from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class Order(Base):
    __tablename__="orders"
    id=Column(Integer,primary_key=True)
    customer_id=Column(Integer,ForeignKey("customers.id"))
    store_id=Column(Integer,ForeignKey("stores.id"))
    bill_number=Column(String(20))
    total_Price=Column(Integer)
    balance=Column(Integer)
    order_date=Column(DateTime) 
    cretaed_at=Column(DateTime) 
    updated_at=Column(DateTime)
    created_by=Column(Integer,ForeignKey("user.id"))
    status=Column(Integer,comment="1 active, 0 delete")

    user=relationship("User",back_populates="orders")
    customers=relationship("Customer",back_populates="orders")
    orderitems=relationship("OrderItem",back_populates="orders")
    payments=relationship("Payment",back_populates="orders")
    stores=relationship("Store",back_populates="orders")
