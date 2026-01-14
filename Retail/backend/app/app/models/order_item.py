from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class OrderItem(Base):
    __tablename__="orderitems"
    id=Column(Integer,primary_key=True)
    product_id=Column(Integer,ForeignKey("items.id"))
    order_id=Column(Integer,ForeignKey("orders.id"))
    quantity=Column(Integer)
    total_price=Column(Integer)
    
    cretaed_at=Column(DateTime)
    status=Column(Integer,comment="1 active, 0 delete")
    orders=relationship("Order",back_populates="orderitems")
    items=relationship("Item",back_populates="orderitems")

