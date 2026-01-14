from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime,DECIMAL
from sqlalchemy.orm import relationship
class SupplierPayment(Base):
    __tablename__="supplierpayments"
    id=Column(Integer,primary_key=True)
    SupplierOrder_id=Column(Integer,ForeignKey("supplierorders.id"))
    total_amount=Column(DECIMAL)
    payment_method=Column(Integer,comment="1 for gpay , 2 for paypal")
    total_paid=Column(DECIMAL)
    bill_num=Column(Integer)
    balance=Column(DECIMAL)
    updated_at=Column(DateTime)
    cretaed_at=Column(DateTime) 
    payment_status=Column(Integer,comment="1 fully paid, 0 not paid")
    status=Column(Integer,comment="1 conform, 0 not_conform")
    supplierorders=relationship("SupplierOrder",back_populates="supplierpayments")