from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class Store(Base):
    __tablename__="stores"
    id=Column(Integer,primary_key=True)
    store_name=Column(String(200))
    address=Column(String(200))
    stock=Column(Integer)
    gst=Column(String(200))
    gst_pan=Column(String(200))
    store_image=Column(String(200))
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    status=Column(Integer,comment="1 active, 0 delete")
    user=relationship("User",back_populates="stores")
    storeproducts=relationship("StoreProduct",back_populates="stores")
    orders=relationship("Order",back_populates="stores")
    supplierorders=relationship("SupplierOrder",back_populates="stores")