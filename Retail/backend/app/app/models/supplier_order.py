from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class SupplierOrder(Base):
    __tablename__="supplierorders"
    id=Column(Integer,primary_key=True)
    supplier_id=Column(Integer,ForeignKey("suppliers.id"))
    store_id=Column(Integer,ForeignKey("stores.id"))
    total_amount=Column(Integer) 
    bill_number=Column(String(20))
    balance=Column(Integer)
    qty=Column(Integer)
    order_date=Column(DateTime) 
    cretaed_at=Column(DateTime) 
    updated_at=Column(DateTime)
    created_by=Column(Integer,ForeignKey("user.id"))
    status=Column(Integer,comment="1 active, 0 delete")
    items=relationship("Item",back_populates="supplierorders")
    user=relationship("User",back_populates="supplierorders")
    suppliers=relationship("Supplier",back_populates="supplierorders")
    supplierpayments=relationship("SupplierPayment",back_populates="supplierorders")
    supplier_order_items=relationship("SupplierOrderItem",back_populates="supplierorders")
    stores=relationship("Store",back_populates="supplierorders")