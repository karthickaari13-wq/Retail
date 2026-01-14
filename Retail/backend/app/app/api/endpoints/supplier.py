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
from api.deps import get_db,authenticate,Image_url,get_user_token,phoneNo_validation
token_header = APIKeyHeader(name="token", auto_error=False)
router = APIRouter()
@router.post("/create_supplier")
async def createSupplier(supplier_name:str=Form(...),address:str=Form(...),
                         email:EmailStr = Form(None),
                         image: UploadFile = File(None),
                         deleviery:str=Form(None),
                      mobile_number:str=Form(...),
                      db:Session=Depends(get_db),token: str = Security(token_header)):
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType != 1 :
        return {"status":0,"msg":"You are not authorized to create the supplier"}
    
    checksupplier = db.query(Supplier).filter(Supplier.status==1)
    if checksupplier.filter(Supplier.supplier_name == supplier_name).first():
        return {"status":0,"msg":"Given supplier_name is already exist"}
    if checksupplier.filter(Supplier.mobile_number == mobile_number).first():
        return {"status":0,"msg":"mobile_number is already exist"}
    if mobile_number:
            if " " in mobile_number:
                return {"status":0,"msg":"Don't give space between the phone Number"}
            if not phoneNo_validation(mobile_number):
                return {"status":0,"msg":"Give a valid Phone Number"}
    get_supplier_name=db.query(Supplier).filter(Supplier.supplier_name==supplier_name , Supplier.status==1).first()
    if get_supplier_name:
        return {"status":0,"msg":"Supplier name already exit."}
    if image:
        url=Image_url(image)
    create_supplier=Supplier(supplier_name=supplier_name,address=address,email=email,image=url,deleviery=deleviery,
                             mobile_number=mobile_number,status=1,created_at=datetime.now())
    db.add(create_supplier)
    db.commit()
    return {"status":1,"msg":"supplier created"}
     

@router.post("/update_supplier")
async def updateSupplier(Supplier_id:int=Form(...),
                          supplier_name:str=Form(None),
                          address:str=Form(None),
                          mobile_number:str=Form(None),
                          email:EmailStr = Form(None),
                          image: UploadFile = File(None),
                          deleviery:str=Form(None),
                          db:Session=Depends(get_db),
                          token: str = Security(token_header)
                          ):
    user = get_user_token(db,token=token)
    

    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType != 1:
        return {"status":0,"msg":"You are not authorized to update the supplier"}
    
    get_Supplier=db.query(Supplier).filter(Supplier.id==Supplier_id , Supplier.status==1).first()
    if get_Supplier:
        checksupplier = db.query(Supplier).filter(Supplier.status==1)
        if supplier_name:
            if checksupplier.filter(Supplier.supplier_name == supplier_name,Supplier.id!=Supplier_id).first():
                return {"status":0,"msg":"Given Supplier name is already exist"}

            get_Supplier.supplier_name=supplier_name
        if address:
            get_Supplier.address=address
        if email:
            get_Supplier.email=email
        if deleviery:
            get_Supplier.deleviery=deleviery
        if image:
            get_Supplier.image_url=image
        if mobile_number:
            if checksupplier.filter(Supplier.mobile_number == mobile_number,Supplier.id!=Supplier_id).first():
                return {"status":0,"msg":"Given Supplier mobile_number is already exist"}


            if " " in mobile_number:
                return {"status":0,"msg":"Don't give space between the phone Number"}
            if not phoneNo_validation(mobile_number):
                return {"status":0,"msg":"Give a valid Phone Number"}

        get_Supplier.updated_at=datetime.now()
        db.commit()
        return {"status":1, "msg":"supplier details updated successfully"}
    else:
        return {"status":0, "msg":"Given supplier id details not found"}


@router.post("/delete_supplier")
async def deleteSupplier(supplier_id:int=Form(...),
                          
                          db:Session=Depends(get_db),
                          token: str = Security(token_header)):
    user  = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType !=1:
        return {"status":0,"msg":"You are not authorized to delete the supplier"}
    
    supplier=db.query(Supplier).filter(Supplier.id==supplier_id,Supplier.status==1).first()
    if supplier:
        supplier.status=-1
    else:
        return {"status":0, "msg":"Given supplier id details not found"}

    db.commit()
    return {"status":1, "msg":"Supplier details successfully deleted"}
     
@router.post("/list_supplier_details")
async def list_supplier_details(db:Session=Depends(deps.get_db),
                   token: str = Security(token_header),page:int=1,
                   size:int=10,supplier_name:str=Form(None),address:str=Form(None),
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if  user.userType==1:
       
            get_supplier=db.query(Supplier).filter(Supplier.status==1)
            if supplier_name:
                get_supplier=get_supplier.filter(Supplier.supplier_name.like("%"+supplier_name+"%"))
            if address:
                get_supplier=get_supplier.filter(Supplier.address.like("%"+address+"%"))  
            get_supplier = get_supplier.order_by(Supplier.id.desc())
            totalCount= get_supplier.count()  
            total_page,offset,limit=get_pagination(totalCount,page,size)
            get_supplier=get_supplier.limit(limit).offset(offset).all()
            dataList =[]
            for row in get_supplier:
                
                dataList.append({"supplier_id":row.id,
                            "supplier_name":row.supplier_name,
                            "address":row.address,
                            "mobile_number":row.mobile_number,
                            "email":row.email,
                            "deleviery":row.deleviery,
                            "image_url":row.image_url,
                            "created_at":row.created_at})
            data=({"page":page,"size":size,"total_page":total_page,
                    "total_count":totalCount,
                    "items":dataList})
            return {"status":1,"msg":"Success","data":data}
        else:
            return {"status":0,"msg":"not authorized"}
    else:
        return({'status' :-1,
                'msg' :'Sorry! your login session expired. please login again.'})
