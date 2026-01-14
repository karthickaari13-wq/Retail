from fastapi import APIRouter, Depends, Form,Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.models import ApiTokens,User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime ,timedelta
from app.utils import *
from sqlalchemy import or_,func


from app.schemas.order_product_details import customer_order_detail
from api.deps import get_db,authenticate,get_by_user,get_user_token,phoneNo_validation
from fastapi.encoders import jsonable_encoder
token_header = APIKeyHeader(name="token", auto_error=False)

router = APIRouter()
@router.post("/create_customer_order")
async def createCustomerOrder(base:customer_order_detail,db:Session=Depends(get_db),
                              token: str = Security(token_header)):
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}
    base=jsonable_encoder(base)
    store_id=base["store_id"]
    customer_name=base["customer_name"]
    mobile_number=base["mobile_number"]
    address=base["address"]
    create_customer=Customer(name=customer_name,
                             mobile=mobile_number,
                             address=address,
                             created_at=datetime.now(),
                             status=1
                             )
    db.add(create_customer)
    db.commit()
    create_order=Order(
        customer_id=create_customer.id,
        store_id=store_id,
        order_date=datetime.now(),
        cretaed_at=datetime.now(),
        status=1,
        created_by=user.id

    )
    db.add(create_order)
    db.commit()
    

    for row in base["product_details"]:
        product_id=row["item_id"]
        qty=row["qty"]
        get_product=db.query(StoreProduct).filter(StoreProduct.product_id==product_id,StoreProduct.status==1).first()
        if get_product.stock<qty:
            return {"status":0,"msg":"low stock"}
        create_orderItem=OrderItem(product_id=product_id,
                              order_id= create_order.id,
                              quantity=qty,
                              total_price=get_product.selling_price*qty,
                              cretaed_at=datetime.now(),
                              status=1
                              )
        db.add(create_orderItem)
        get_product.stock=get_product.stock-qty
        db.commit()
    total_price = (
        db.query(func.sum(OrderItem.total_price))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.status == 1,
            OrderItem.order_id == create_order.id
        )
        .scalar()
        ) or 0
    create_order.total_Price=total_price
    create_order.balance=total_price
    db.commit()
    return {"status":1,"msg":"order created sucessfully"}


@router.post("/list_customer_order") 
async def list_customer_order(db:Session=Depends(deps.get_db),
                   token: str = Security(token_header),page:int=1,
                   size:int=10,
                   store_id:int=Form(...),
                   last_2days_data:int=Form(None)
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.userType in [3,4]:
            return {"status":0,"msg":"You are not authorized to delete the Product"}

        two_days_ago = datetime.now() - timedelta(days=2)
        list_data=db.query(Customer,Order,Store,OrderItem,Item,Category,StoreProduct)\
            .join(Order,Customer.id==Order.customer_id)\
                .join(Store,Order.store_id==Store.id)\
                    .join(OrderItem,OrderItem.order_id==Order.id)\
                        .join(Item,Item.id==OrderItem.product_id)\
                            .join(Category,Category.id==Item.category_id)\
                                .join(StoreProduct,Item.id==StoreProduct.product_id).filter(Order.status==1,Order.store_id==store_id)
      
    
        if last_2days_data:
            list_data=list_data.filter(Order.order_date >= two_days_ago)
        
        list_data = list_data.order_by(Order.id.desc())
        totalCount= list_data.count()  
        total_page,offset,limit=get_pagination(totalCount,page,size)
        list_data=list_data.limit(limit).offset(offset).all()
       
        orders = {}
        for customer,order,store,orderitem,product,categoery,storeproduct in list_data:
            order_id = order.id
            if order_id not in orders:
                 orders[order_id] ={"Order_id":order.id,
                                    "order_date":order.order_date,
                                     "customer_name":customer.name,
                                    "customer_number":customer.mobile,
                                    "customer_address":customer.address,
                                    "total_amount":order.total_Price,
                                     "store_name":store.store_name,
                                    "store_address":store.address,
                                    "products": []
                                    }
            orders[order_id]["products"].append({
                        "item_id": product.id,
                        "item_name":product.product_name,
                        "item_price":storeproduct.selling_price,
                        "category_name":categoery.category_name,
                        "total_price":orderitem.total_price,
                        "quantity":orderitem.quantity,
            
            })
                 
        data = {
            "page": page,
            "size": size,
            "total_page": total_page,
            "total_count": totalCount,
            "items": list(orders.values())
        }

        return {
            "status": 1,
            "msg": "Success",
            "data": data
        }  
        
    else:
        return({'status' :-1,
                'msg' :'Sorry! your login session expired. please login again.'})
