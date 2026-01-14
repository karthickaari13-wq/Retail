from app.database  import Base
from sqlalchemy import Column,String,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
class Category(Base):
    __tablename__="categorys"
    id=Column(Integer,primary_key=True)
    category_name=Column(String(20))
    status=Column(Integer,comment="1 active, 0 delete")
    image_url=Column(String(200))
    description=Column(String(200))
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    items=relationship("Item",back_populates="categorys")
    
