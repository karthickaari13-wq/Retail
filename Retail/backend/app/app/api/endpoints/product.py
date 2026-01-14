from fastapi import APIRouter, Depends, Form,Security,UploadFile,File
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
from app.schemas.order_product_details import supplier_order_detail
from api.deps import get_db,authenticate,get_by_user,get_user_token,Image_url
from fastapi.encoders import jsonable_encoder 
token_header = APIKeyHeader(name="token", auto_error=False)
router = APIRouter()
@router.post("/create_item_order")
async def create_item_order(
                         
                         base:supplier_order_detail,
                         db:Session=Depends(get_db),
                         token: str = Security(token_header)
                         ):
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}
    
    if user.userType in [3,4]:
        return {"status":0,"msg":"You are not authorized "}
    base=jsonable_encoder(base)
    store_id=base["store_id"]
    supplier_id=base["supplier_id"]
    create_SupplierOrder=SupplierOrder(supplier_id=supplier_id,store_id=store_id,
                                 order_date=datetime.now(),
                                 status=1,cretaed_at=datetime.now(),created_by=user.id)
    db.add(create_SupplierOrder)
    db.commit()
    for row in base["product_details"]:
        product_id=row['item_id']
        product_price=row["item_price"]
        qty=row["qty"]
        store_product = db.query(StoreProduct).filter(
                StoreProduct.store_id == store_id,
                StoreProduct.product_id == product_id,
                StoreProduct.status == 1
            ).first()
        if store_product:
                store_product.stock += qty
                store_product.product_price=product_price
                store_product.updated_at = datetime.now()
        else:
            create_StoreProduct=StoreProduct(store_id=store_id,
                                            stock=qty,
                                            product_price=product_price,
                                            product_id=product_id,
                                            status=1,created_at=datetime.now()
                                            )
            db.add(create_StoreProduct)
            db.commit()
        create_supplier_product=SupplierOrderItem(supplier_id=supplier_id,
                                                product_id=product_id,
                                                SupplierOrder_id=create_SupplierOrder.id,
                                                price=product_price,
                                                qty=qty,
                                                total_price=product_price*qty,
                                                status=1,created_at=datetime.now(),
                                                last_purcahsed=datetime.now()

                                                )
        db.add(create_supplier_product)
        db.commit()
    get_data=db.query(SupplierOrderItem).join(SupplierOrder,SupplierOrder.id==SupplierOrderItem.SupplierOrder_id).filter(SupplierOrder.status==1,SupplierOrder.id==create_SupplierOrder.id).all()
    total_price=0
    for row in get_data:
        total_price=total_price+row.total_price
   

    create_SupplierOrder.total_amount=total_price
    create_SupplierOrder.balance=total_price
    db.commit()
    
    return {"status":1,"msg":"item created"}


@router.post("/set_store_product_price")
async def set_store_product_price(
    product_id: int = Form(...),
    store_id: int = Form(...),
    selling_price: float = Form(...),
    db: Session = Depends(get_db),
    token: str = Security(token_header)
):
    user = get_user_token(db,token=token)
    

    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType ==4:
        return {"status":0,"msg":"You are not authorized "}
    get_StoreProduct=db.query(StoreProduct).filter(StoreProduct.product_id==product_id ,StoreProduct.store_id==store_id ,StoreProduct.status==1).first()
    
    if get_StoreProduct:
        get_StoreProduct.selling_price=selling_price
        db.commit()
        return {"status":1, "msg":"selling_price updated successfully"}
    else:
        return {"status":0,"msg":"store product not found "}


# @router.post("/update_product_order")
# async def update_product_order(product_id:int=Form(...),
#                           product_name:str=Form(None),
#                           product_price:int=Form(None),
#                           qty:int=Form(None),
#                           db:Session=Depends(get_db),
#                           token:str = Form(...)
#                           ):
#     user = get_user_token(db,token=token)
#     if not user:
#         return {"status":0,"msg":"Your login session expires.Please login again."}

#     if user.userType not in [3,4]:
#         return {"status":0,"msg":"You are not authorized to update the Product"}
    
#     get_product=db.query(Product).filter(Product.id==product_id , Product.status==1).first()
#     if not get_product:
#         return {"status":0, "msg":"Given Product id details not found"}
#     if get_product:
#         get_SupplierProduct=db.query(SupplierProduct).filter(SupplierProduct.product_id==product_id , Product.status==1).first()
#     if product_name:
#         get_product.product_name=product_name
#     if product_price:
#         get_product.product_price=product_price
#     if qty:
#         get_product.qty=qty
#     get_product.updated_at=datetime.now()
#     db.commit()
#     if get_SupplierProduct:
#         if product_price:
#             get_SupplierProduct.price=product_price
#         if qty:
#             get_SupplierProduct.qty=qty
        
#         get_SupplierProduct.total_price=get_product.product_price*get_product.qty
#         get_SupplierProduct.updated_at=datetime.now()
#     return {"status":1, "msg":"Product details updated successfully"}
    
   


# @router.post("/delete_product_order")
# async def delete_product_order(product_id:int=Form(...),
#                           db:Session=Depends(get_db),
#                           token:str = Form(...)):
#     user  = get_user_token(db,token=token)
#     if not user:
#         return {"status":0,"msg":"Your login session expires.Please login again."}

#     if user.userType == 3 or user.userType ==4:
#         return {"status":0,"msg":"You are not authorized to delete the Product"}
    
#     product, store_product, supplier_product = (
#     db.query(Product, StoreProduct, SupplierProduct)
#     .join(StoreProduct, Product.id == StoreProduct.product_id)
#     .join(SupplierProduct, Product.id == SupplierProduct.product_id)
#     .filter(Product.id == product_id, Product.status == 1)
#     .first()
# )

#     if product:
#         product.status = -1
#         store_product.status = -1
#         supplier_product.status = -1

#         db.commit()
#         return {"status":1, "msg":"Product details successfully deleted"}
#     else:
#         return {"status":0, "msg":"Given Product id details not found"}

   


@router.post("/list_item_order")
async def list_item_order(
    db: Session = Depends(deps.get_db),
    token: str = Security(token_header),
    page: int = 1,
    size: int = 10,
    store_id: int = Form(...)
):
    user = deps.get_user_token(db=db, token=token)
    if not user:
        return {"status": 0, "msg": "Invalid token"}

    if user.userType in [3, 4]:
        return {"status": 0, "msg": "You are not authorized"}

    query = (
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
        .filter(SupplierOrder.status == 1)
    )

  
    if store_id:
        query = query.filter(Store.id == store_id)

   

    total_count = query.count()
    total_page, offset, limit = get_pagination(total_count, page, size)

    results = (
        query.order_by(SupplierOrder.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    orders = {}

    for so, sp, p, c, st, s in results:
        if so.id not in orders:
            orders[so.id] = {
                "supplier_order_id": so.id,
                "store_name": st.store_name,
                "store_address": st.address,
                "supplier_name": s.supplier_name,
                "supplier_mobile_number": s.mobile_number,
                "supplier_address": s.address,
                "total_amount": so.total_amount,
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
            "total_count": total_count,
            "items": list(orders.values())
        }
    }



@router.post("/create_item")
async def createItem(item_name:str=Form(...),
                     mrp:str=Form(None),
                     tax_product:str=Form(None),
                     discount_percent:str=Form(None),
                     reopen_level:str=Form(None),
                     brand:str=Form(None),
                     manufacture:str=Form(None),
                     weight:str=Form(None),
                     discription:str=Form(None),
                     image: UploadFile = File(None),

                     
                        category_id:int=Form(...),
                        db:Session=Depends(get_db),token: str = Security(token_header)):
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType in [3,4]:
        return {"status":0,"msg":"You are not authorized to create the item"}
    chechProduct_name = db.query(Item).filter(Item.status==1,Item.product_name==item_name).first()
    if chechProduct_name:
        return {"status":0,"msg":"Given item name is already exist"}
    if image:
        url=Image_url(image)
    create_product=Item(product_name=item_name,mrp=mrp,
                        tax_product=tax_product,
                        discount_percent=discount_percent,
                        reopen_level=reopen_level,
                        brand=brand,
                        manufacture=manufacture,
                        weight=weight,
                        discription=discription,
                        image_url=url,
                           category_id=category_id,status=1,created_at=datetime.now())
    db.add(create_product)
    db.commit()
    return {"status":1,"msg":"item created"}
     

    
@router.post("/update_item")
async def updateItem(item_id:int=Form(...),
                          item_name:str=Form(None),
                          mrp:str=Form(None),
                            tax_product:str=Form(None),
                            discount_percent:str=Form(None),
                            reopen_level:str=Form(None),
                            brand:str=Form(None),
                            manufacture:str=Form(None),
                            weight:str=Form(None),
                            discription:str=Form(None),
                            image: UploadFile = File(None),
                          category_id:int=Form(None),
                          db:Session=Depends(get_db),
                          token: str = Security(token_header)
                          ):
    user = get_user_token(db,token=token)
    

    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType in [3,4]:
        return {"status":0,"msg":"You are not authorized to update the Item"}
    
    get_product=db.query(Item).filter(Item.id==item_id , Item.status==1).first()
    if get_product:
        if item_name:
            checkproduct_name = db.query(Item).filter(Item.status==1,Item.product_name==item_name,Item.id!=item_id ).first()
            if checkproduct_name:
                return {"status":0,"msg":"Given Item is already exist"}

            get_product.product_name=item_name
        if category_id:
            get_product.category_id=category_id
        if mrp:
            get_product.mrp=mrp
        if tax_product:
            get_product.tax_product=tax_product
        if discount_percent:
            get_product.discount_percent=discount_percent
        if reopen_level:
            get_product.reopen_level=reopen_level
        if brand:
            get_product.brand=brand
        if manufacture:
            get_product.manufacture=manufacture
        if weight:
            get_product.weight=weight
        if image:
            get_product.discription=discription
            
        if discription:
            url=Image_url(image)
            get_product.image_url=url
        get_product.updated_at=datetime.now()
        db.commit()
        return {"status":1, "msg":"Item details updated successfully"}
    else:
        return {"status":0, "msg":"Given Item id details not found"}


@router.post("/delete_item")
async def deleteItem(item_id:int=Form(...),
                          
                          db:Session=Depends(get_db),
                          token: str = Security(token_header)):
    user  = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType in [3,4]:
        return {"status":0,"msg":"You are not authorized to delete the item"}
    
    get_product=db.query(Item).filter(Item.id==item_id,Item.status==1).first()
    if get_product:
        get_product.status=-1
        db.commit()

    else:
        return {"status":0, "msg":"Given item id details not found"}

    db.commit()
    return {"status":1, "msg":"item deleted successfully "}
     



@router.post("/list_item_details")
async def list_Item_details(db:Session=Depends(deps.get_db),
                   token: str = Security(token_header),page:int=1,
                   size:int=10,category_name:str=Form(None),
                   item_name:str=Form(None),
                   
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if  user.userType not in [3,4]:
       
            list_data=db.query(Category,Item,).join(Category,Category.id==Item.category_id)\
                .filter(Item.status==1)
            
            if item_name:
                list_data=list_data.filter(Item.product_name.like("%"+item_name+"%"))

            if category_name:
                list_data=list_data.filter(Category.category_name.like("%"+category_name+"%"))
            
            list_data = list_data.order_by(Item.id.desc())
            totalCount= list_data.count()  
            total_page,offset,limit=get_pagination(totalCount,page,size)
            list_data=list_data.limit(limit).offset(offset).all()
            dataList =[]
            for category,product in list_data:
                
                dataList.append({"category_id":category.id,
                            "category_name":category.category_name,
                            "item_id":product.id,
                            "item_name":product.product_name,
                            "tax_product":product.tax_product,
                        "discount_percent":product.discount_percent,
                        "reopen_level":product.reopen_level,
                        "brand":product.brand,
                        "manufacture":product.manufacture,
                        "weight":product.weight,
                        "discription":product.discription,
                        "image_url":product.image_url
                            
                            })
            data=({"page":page,"size":size,"total_page":total_page,
                    "total_count":totalCount,
                    "items":dataList})
            return {"status":1,"msg":"Success","data":data}
        else:
            return {"status":0,"msg":"only owner and  admin can  access"}
    else:
        return({'status' :-1,
                'msg' :'Sorry! your login session expired. please login again.'})

