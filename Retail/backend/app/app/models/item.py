from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class Item(Base):
    __tablename__="items"
    id=Column(Integer,primary_key=True)
    product_name=Column(String(20))
    product_price=Column(Integer)
    qty=Column(Integer)

    mrp=Column(String(20))
    tax_product=Column(String(20))
    discount_percent=Column(String(20))
    stock_qty=Column(String(20))
    reopen_level=Column(String(20))
    expiry_date=Column(String(20))
    brand=Column(String(20))
    manufacture=Column(String(20))
    image_url=Column(String(200))
    weight=Column(String(200))
    discription=Column(String(200))

    category_id=Column(Integer,ForeignKey("categorys.id"))
    supplier_order_id=Column(Integer,ForeignKey("supplierorders.id"))
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    status=Column(Integer,comment="1 active, 0 delete")
    categorys=relationship("Category",back_populates="items")
    orderitems=relationship("OrderItem",back_populates="items")
    storeproducts=relationship("StoreProduct",back_populates="items")
    supplier_order_items=relationship("SupplierOrderItem",back_populates="items")
    supplierorders=relationship("SupplierOrder",back_populates="items")