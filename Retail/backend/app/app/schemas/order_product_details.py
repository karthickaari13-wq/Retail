from pydantic import BaseModel,Field
from typing  import Annotated
from datetime import datetime
from typing import Optional
class supplier_order_item(BaseModel):
    item_id: int 
    item_price: int
    qty:int
    
    
   

class supplier_order_detail(BaseModel):
   
    product_details: list[supplier_order_item]
    supplier_id:int
    
    store_id:int
   

class customer_order_item(BaseModel):
    item_id: int
    qty:int
  

class customer_order_detail(BaseModel):
   
    product_details: list[customer_order_item]
    
    store_id:int
    customer_name:str
    mobile_number:str
    address:str
    
    
