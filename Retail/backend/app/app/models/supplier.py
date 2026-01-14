from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class Supplier(Base):
    __tablename__="suppliers"
    id=Column(Integer,primary_key=True)
    supplier_name=Column(String(200))
    mobile_number=Column(String(200))
    address=Column(String(200))
    email=Column(String(200))
    deleviery=Column(String(200))
    image_url=Column(String(200))
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    status=Column(Integer,comment="1 active, 0 delete")
    supplier_order_items=relationship("SupplierOrderItem",back_populates="suppliers")
    supplierorders=relationship("SupplierOrder",back_populates="suppliers")