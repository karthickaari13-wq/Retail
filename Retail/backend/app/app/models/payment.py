from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime,DECIMAL
from sqlalchemy.orm import relationship
class Payment(Base):
    __tablename__="payments"
    id=Column(Integer,primary_key=True)
    order_id=Column(Integer,ForeignKey("orders.id"))
    total_amount=Column(DECIMAL)
    payment_method=Column(Integer,comment="1 for gpay , 2 for paypal")
    total_paid=Column(DECIMAL)
    balance=Column(DECIMAL)
    updated_at=Column(DateTime)
    cretaed_at=Column(DateTime) 
    bill_num=Column(Integer)
    payment_status=Column(Integer,comment="1 fully paid, 0 not paid")

    status=Column(Integer,comment="1 conform, 0 not_conform")
    orders=relationship("Order",back_populates="payments")