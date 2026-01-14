from fastapi import APIRouter, Depends, Form,Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.models import ApiTokens,User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import or_, func
from pydantic import EmailStr
from api.deps import get_db,authenticate,get_by_user,get_user_token,phoneNo_validation
token_header = APIKeyHeader(name="token", auto_error=False)
router = APIRouter()
@router.post("/dashboard_count")
async def dashboard_count(store_id:int=Form(...),db:Session=Depends(get_db),token: str = Security(token_header)):
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType in [3,4]:
        return {"status":0,"msg":"You are not authorized "}
    due_amount_customer = (
        db.query(func.sum(Order.balance))
        .filter(
            Order.store_id == store_id,
            Order.status == 1
        )
        .scalar())
    
        
    due_amount_supplier = (
        db.query(func.sum(SupplierOrder.balance))
        .filter(
            SupplierOrder.store_id == store_id,
            SupplierOrder.status == 1
        )
        .scalar())
    
    out_of_stock = (
    db.query(StoreProduct)
    .join(Item, StoreProduct.product_id == Item.id)
    .filter(
        StoreProduct.stock <= 0,
        StoreProduct.store_id == store_id
    )
    .all()
                )
    low_Stock = (
    db.query(StoreProduct)
    .join(Item, StoreProduct.product_id == Item.id)
    .filter(
        StoreProduct.stock <= 5,
        StoreProduct.store_id == store_id
    )
    .all()
                )

    return {
        "status": 1,
        
        "out_of_Stock": len(out_of_stock),

        "low_Stock": len(low_Stock),

        "due_amount_customer": due_amount_customer or 0,
        "due_amount_supplier": due_amount_supplier or 0,

    }

  
       

@router.post("/list_customer_due_details")
async def list_customer_due_details(db:Session=Depends(deps.get_db),
                   token: str = Security(token_header),page:int=1,
                   size:int=10,store_id:int=Form(...),customer_id:int=Form(None)
                  
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.userType in [3,4]:
            return {"status":0,"msg":"You are not authorized to delete the Product"}

        list_data=db.query(Customer,Order,Store,OrderItem,Item,Category,StoreProduct)\
            .join(Order,Customer.id==Order.customer_id)\
                .join(Store,Order.store_id==Store.id)\
                    .join(OrderItem,OrderItem.order_id==Order.id)\
                        .join(Item,Item.id==OrderItem.product_id)\
                            .join(Category,Category.id==Item.category_id)\
                                .join(StoreProduct,Item.id==StoreProduct.product_id).filter(Order.status==1,Order.balance>0,Store.id==store_id)
        if customer_id:
            list_data=list_data.filter(Customer.id==customer_id)
       
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
                                    "balance":order.balance,
                                     "store_name":store.store_name,
                                    "store_address":store.address,
                                    "products": []
                                    }
            orders[order_id]["products"].append({
                        "item_id": product.id,
                        "item_name":product.product_name,
                        "item_price":storeproduct.product_price,
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




@router.post("/list_supplier_due_details")
async def list_supplier_due_details(db:Session=Depends(deps.get_db),
                   token: str = Security(token_header),page:int=1,
                   size:int=10,store_id:int=Form(...),
                   supplier_id:int=Form(None)


                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.userType ==4:
            return {"status":0,"msg":"You are not autho the Product"}

        
        
        list_data = (
        db.query(
            SupplierOrder,
            SupplierOrderItem,
            Item,
            Category,
            Store,
            Supplier
        )
        .join(SupplierOrderItem, SupplierOrder.id == SupplierOrderItem.SupplierOrder_id)
        .join(Item, Item.id == SupplierOrderItem.product_id)
        .join(Category, Category.id == Item.category_id)
        .join(Store, Store.id == SupplierOrder.store_id)
        .join(Supplier, Supplier.id == SupplierOrder.supplier_id)
        .filter(SupplierOrder.status == 1,SupplierOrder.balance>0,Store.id==store_id)
                 )
        if supplier_id:
            list_data=list_data.filter(Supplier.id==supplier_id)

        list_data = list_data.order_by(SupplierOrder.id.desc())
        totalCount= list_data.count() 
        total_page,offset,limit=get_pagination(totalCount,page,size)
        list_data=list_data.limit(limit).offset(offset).all()
        
        orders = {}
        for so, sp, p, c, st, s in list_data:
            if so.id not in orders:
                orders[so.id] = {
                    "supplier_order_id": so.id,
                    "store_name": st.store_name,
                    "store_address": st.address,
                    "supplier_name": s.supplier_name,
                    "supplier_mobile_number": s.mobile_number,
                    "supplier_address": s.address,
                    "total_amount": so.total_amount,
                    "balance":so.balance,
                    "products": []
                }

            orders[so.id]["products"].append({
                "item_id": p.id,
                "item_name": p.product_name,
                "purchase_price": sp.price,          
                "quantity": sp.qty,                  
                "category_name": c.category_name,
                "total_price": sp.total_price
            })
        return {
        "status": 1,
        "msg": "Success",
        "data": {
            "page": page,
            "size": size,
            "total_page": total_page,
            "total_count": totalCount,
            "items": list(orders.values())
        }
    }
            


# @router.post("/Low_Stock")
# async def Low_Stock(store_id:int=Form(...),db:Session=Depends(get_db),token: str = Security(token_header)):
#     user = get_user_token(db,token=token)
#     if not user:
#         return {"status":0,"msg":"Your login session expires.Please login again."}

#     if user.userType in [3,4]:
#         return {"status":0,"msg":"You are not authorized "}
#     get_data = (
#     db.query(StoreProduct)
#     .join(Product, StoreProduct.product_id == Product.id)
#     .filter(
#         StoreProduct.stock <= 5,
#         StoreProduct.store_id == store_id
#     )
#     .all()
#                 )

#     return {
#         "status": 1,
        
#         "Low_stock": len(get_data)
#     }



# @router.post("/out_of_Stock")
# async def out_of_Stock(store_id:int=Form(...),db:Session=Depends(get_db),token: str = Security(token_header)):
#     user = get_user_token(db,token=token)
#     if not user:
#         return {"status":0,"msg":"Your login session expires.Please login again."}

#     if user.userType in [3,4]:
#         return {"status":0,"msg":"You are not authorized "}
    
#     get_data = (
#     db.query(StoreProduct)
#     .join(Product, StoreProduct.product_id == Product.id)
#     .filter(
#         StoreProduct.stock <= 0,
#         StoreProduct.store_id == store_id
#     )
#     .all()
#                 )

#     return {
#         "status": 1,
        
#         "out_of_Stock": len(get_data)
#     }