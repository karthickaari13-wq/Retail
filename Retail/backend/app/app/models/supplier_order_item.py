from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class SupplierOrderItem(Base):
    __tablename__="supplier_order_items"
    id=Column(Integer,primary_key=True)
    supplier_id=Column(Integer,ForeignKey("suppliers.id"))
    product_id=Column(Integer,ForeignKey("items.id"))
    SupplierOrder_id=Column(Integer,ForeignKey("supplierorders.id"))
    price=Column(Integer)
    qty=Column(Integer)
    total_price=Column(Integer)
    last_purcahsed=Column(DateTime)                                                             
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    status=Column(Integer,comment="1 active, 0 delete")
    suppliers=relationship("Supplier",back_populates="supplier_order_items")
    items=relationship("Item",back_populates="supplier_order_items")
    supplierorders=relationship("SupplierOrder",back_populates="supplier_order_items")