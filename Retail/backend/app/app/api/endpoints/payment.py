from fastapi import APIRouter, Depends, Form,Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.models import ApiTokens,User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import or_
from pydantic import EmailStr
from api.deps import get_db,authenticate,get_by_user,get_user_token,phoneNo_validation
from fastapi.encoders import jsonable_encoder 
token_header = APIKeyHeader(name="token", auto_error=False)
router = APIRouter()
@router.post("/create_supplier_payment")
async def createSupplierPayment(suupier_order_id:int=Form(...),
                              payment_method:int=Form(...,description=("1 for gpay ,2 for phonepay,3 for cash in hand")),
                              bill_num:int=Form(...),

                              pay_amount:int= Form(...) ,db:Session=Depends(get_db),token: str = Security(token_header)  ):                  

               
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType == 4 :
        return {"status":0,"msg":"You are not authorized to create the payment"}
    get_payment=db.query(SupplierPayment).filter(SupplierPayment.SupplierOrder_id==suupier_order_id,SupplierPayment.payment_status==1).first()
    check_off_payment= db.query(SupplierPayment).filter(SupplierPayment.SupplierOrder_id==suupier_order_id,SupplierPayment.payment_status==0).first()
    if  get_payment :
        return {"status":0,"msg":"paid already"}
    get_data=db.query(SupplierOrder).filter(SupplierOrder.id==suupier_order_id,SupplierOrder.status==1).first()
    payment_status=False
    if get_data.total_amount-pay_amount==0:
        payment_status=True
    if check_off_payment:
        check_off_payment.total_paid=check_off_payment.total_paid+pay_amount
        
        check_off_payment.balance=check_off_payment.balance -pay_amount
        check_off_payment.updated_at=datetime.now()
        if check_off_payment.balance-pay_amount==0:
            check_off_payment.payment_status=1
        else:
            check_off_payment.payment_status=0
        get_data.balance=check_off_payment.balance-pay_amount
        db.commit()
        return {"status":1,"msg":"Payment  Done"}
    create_payment=SupplierPayment(payment_method=payment_method,
                                 bill_num=bill_num,
                                 total_paid=pay_amount,
                                 total_amount=get_data.total_amount,
                                 SupplierOrder_id=suupier_order_id,
                                 balance=get_data.total_amount-pay_amount,
                                 payment_status=1 if payment_status else 0,
                                 cretaed_at=datetime.now(),
                                 status=1)
    db.add(create_payment)
    get_data.balance=get_data.total_amount-pay_amount
    db.commit()
    return {"status":1,"msg":"Payment  Done"}


@router.post("/create_customer_payment")
async def createCustomerPayment(order_id:int=Form(...),
                              payment_method:int=Form(...,description=("1 for gpay ,2 for phonepay,3 for cash in hand")),
                              bill_num:int=Form(...),

                              pay_amount:int= Form(...) ,db:Session=Depends(get_db),token: str = Security(token_header)  ):                  

               
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType == 4 :
        return {"status":0,"msg":"You are not authorized to create the payment"}
    
    get_payment=db.query(Payment).filter(Payment.order_id==order_id,Payment.payment_status==1).first()
    check_off_payment= db.query(Payment).filter(Payment.order_id==order_id,Payment.payment_status==0).first()
    if  get_payment :
        return {"status":0,"msg":"paid already"}
    get_data=db.query(Order).filter(Order.id==order_id,Order.status==1).first()
    
    payment_status=False
    if get_data.total_Price-pay_amount==0:
        payment_status=True
    if check_off_payment:
        check_off_payment.total_paid=check_off_payment.total_paid+pay_amount
        
        check_off_payment.balance=check_off_payment.balance -pay_amount
        check_off_payment.updated_at=datetime.now()
        if check_off_payment.balance-pay_amount==0:
            check_off_payment.payment_status=1
        else:
            check_off_payment.payment_status=0
        get_data.balance=check_off_payment.balance-pay_amount
        db.commit()
        return {"status":1,"msg":"Payment  Done"}
    create_payment=Payment(payment_method=payment_method,
                                 bill_num=bill_num,
                                 total_paid=pay_amount,
                                 total_amount=get_data.total_Price,
                                 order_id=order_id,
                                 balance=get_data.total_Price-pay_amount,
                                 payment_status=1 if payment_status else 0,
                                 cretaed_at=datetime.now(),
                                 status=1)
    db.add(create_payment)
    get_data.balance=get_data.total_Price-pay_amount
    db.commit()
    return {"status":1,"msg":"Payment  Done"}



@router.post("/list_customer_Payment_details")
async def list_customer_Payment_details(db:Session=Depends(deps.get_db),
                  token: str = Security(token_header),page:int=1,
                   size:int=10,
                   store_id:int=Form(...),
                   customer_id:int=Form(None)
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if  user.userType == 4:
            return {"status":0,"msg":"You are not authorized "}
    
       
        list_data=db.query(Customer,Order,Store,OrderItem,Item,Category,Payment)\
            .join(Order,Customer.id==Order.customer_id)\
                .join(Store,Order.store_id==Store.id)\
                    .join(OrderItem,OrderItem.order_id==Order.id)\
                        .join(Item,Item.id==OrderItem.product_id)\
                            .join(Category,Category.id==Item.category_id)\
                                .join(Payment,Payment.order_id==Order.id).filter(Order.status==1,Payment.status==1)
        if store_id:
            list_data=list_data.filter(Store.id==store_id)
        if customer_id:
            list_data=list_data.filter(Customer.id==customer_id)
        list_data = list_data.order_by(Category.id.desc())
        totalCount= list_data.count()  
        total_page,offset,limit=get_pagination(totalCount,page,size)
        list_data=list_data.limit(limit).offset(offset).all()
        orders = {}
        for customer,order,store,orderitem,product,categoery,payment in list_data:
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
                                    "payment_method":payment.payment_method,
                                    "total_paid":payment.total_paid,
                                    "balance":payment.balance,
                                    "products": []
                                    }
            orders[order_id]["products"].append({
                        "item_id": product.id,
                        "item_name":product.product_name,
                        "item_price":product.product_price,
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
    


     
# @router.post("/list_Supplier_Payment_details")
# async def list_Supplier_Payment_details(db:Session=Depends(deps.get_db),
#                    token: str = Security(token_header),page:int=1,
#                    size:int=10
#                    ):
#     user=deps.get_user_token(db=db,token=token)
#     if user:
#         if user.userType in [3,4]:
#             return {"status":0,"msg":"You are not authorized to delete the Product"}

        
#         list_data=    db.query(SupplierOrder,Product,Category, StoreProduct,Store, SupplierProduct,Supplier,SupplierPayment).join(SupplierOrder,SupplierOrder.id==Product.supplier_order_id)\
#             .join(Category,Category.id==Product.category_id)\
#             .join(StoreProduct, Product.id == StoreProduct.product_id)\
#                 .join(Store,Store.id==StoreProduct.store_id)\
#                 .join(SupplierProduct, Product.id == SupplierProduct.product_id)\
#                 .join(Supplier,Supplier.id==SupplierProduct.supplier_id)\
#                 .join(SupplierPayment,SupplierPayment.SupplierOrder_id==SupplierOrder.id)\
#                     .filter( SupplierOrder.status == 1,SupplierPayment.status==1)
#         if user.userType==2:
#             list_data=list_data.filter(Store.id==user.store_id)

#         list_data = list_data.order_by(SupplierOrder.id.desc())
#         totalCount= list_data.count() 
#         total_page,offset,limit=get_pagination(totalCount,page,size)
#         list_data=list_data.limit(limit).offset(offset).all()
        
#         orders = {}
#         for supplier_order, product, category, storeproduct, store, supplierProduct, supplier,payment in list_data:
#             order_id = supplier_order.id

#             if order_id not in orders:
#                 orders[order_id] = {
#                     "supplier_order_id": order_id,
#                     "store_name": store.store_name,
#                     "store_address": store.address,
#                     "supplier_name": supplier.supplier_name,
#                     "supplier_mobile_number": supplier.mobile_number,
#                     "supplier_address": supplier.address,
#                     "total_amount":supplier_order.total_amount,
#                     "payment_method":payment.payment_method,
#                     "total_paid":payment.total_paid,
#                     "bill_num":payment.bill_num,
#                     "balance":payment.balance,

#                     "products": []
#                 }

#             orders[order_id]["products"].append({
#                 "product_id": product.id,
#                 "product_name": product.product_name,
#                 "product_price": product.product_price,
#                 "quantity": product.qty,
#                 "category_name": category.category_name,
#                 "total_price": supplierProduct.total_price
#             })

#         data = {
#             "page": page,
#             "size": size,
#             "total_page": total_page,
#             "total_count": totalCount,
#             "items": list(orders.values())
#         }

#         return {
#             "status": 1,
#             "msg": "Success",
#             "data": data
#         }
    



     
@router.post("/list_Supplier_Payment_details")
async def list_Supplier_Payment_details(db:Session=Depends(deps.get_db),
                   token: str = Security(token_header),page:int=1,
                   size:int=10,store_id:int=Form(...),
                   supplier_id:int=Form(None)
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.userType in [3,4]:
            return {"status":0,"msg":"You are not authorized to delete the Product"}

        
       
        list_data = (
        db.query(
            SupplierOrder,
            SupplierOrderItem,
            Item,
            Category,
            Store,
            Supplier,SupplierPayment

        )
        .join(SupplierOrderItem, SupplierOrder.id == SupplierOrderItem.SupplierOrder_id)
        .join(Item, Item.id == SupplierOrderItem.product_id)
        .join(Category, Category.id == Item.category_id)
        .join(Store, Store.id == SupplierOrder.store_id)
        .join(Supplier, Supplier.id == SupplierOrder.supplier_id)
        .join(SupplierPayment,SupplierPayment.SupplierOrder_id==SupplierOrder.id)\
        .filter(SupplierOrder.status == 1,SupplierPayment.status==1)
          )
        if store_id:
            list_data=list_data.filter(Store.id==store_id)
        if supplier_id:
            list_data=list_data.filter(Supplier.id==supplier_id)


        list_data = list_data.order_by(SupplierOrder.id.desc())
        totalCount= list_data.count() 
        total_page,offset,limit=get_pagination(totalCount,page,size)
        list_data=list_data.limit(limit).offset(offset).all()
        
        orders = {}
        for supplier_order,supplierProduct, product, category, store, supplier,payment in list_data:
            order_id = supplier_order.id

            if order_id not in orders:
                orders[order_id] = {
                    "supplier_order_id": order_id,
                    "store_name": store.store_name,
                    "store_address": store.address,
                    "supplier_name": supplier.supplier_name,
                    "supplier_mobile_number": supplier.mobile_number,
                    "supplier_address": supplier.address,
                    "total_amount":supplier_order.total_amount,
                    "payment_method":payment.payment_method,
                    "total_paid":payment.total_paid,
                    "bill_num":payment.bill_num,
                    "balance":payment.balance,

                    "products": []
                }

            orders[order_id]["products"].append({
                "item_id": product.id,
                "item_name": product.product_name,
                "item_price": product.product_price,
                "quantity": product.qty,
                "category_name": category.category_name,
                "total_price": supplierProduct.total_price
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