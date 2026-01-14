from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class StoreProduct(Base):
    __tablename__="storeproducts"
    id=Column(Integer,primary_key=True)
    store_id=Column(Integer,ForeignKey("stores.id"))
    product_id=Column(Integer,ForeignKey("items.id"))
    product_price=Column(Integer)
    selling_price=Column(Integer)
    stock=Column(Integer)
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    status=Column(Integer,comment="1 active, 0 delete")
    stores=relationship("Store",back_populates="storeproducts")
    items=relationship("Item",back_populates="storeproducts")