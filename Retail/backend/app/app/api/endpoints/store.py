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
from api.deps import get_db,authenticate,get_by_user,get_user_token,Image_url
token_header = APIKeyHeader(name="token", auto_error=False)
router = APIRouter()
@router.post("/create_store")
async def createStore(store_name:str=Form(...),address:str=Form(...),
                      gst:str=Form(...),
                      gst_pan:str=Form(...),
                      
                      store_image: UploadFile = File(None),
                      db:Session=Depends(get_db),token: str = Security(token_header)):
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType != 1 :
        return {"status":0,"msg":"You are not authorized to create the store"}
    if store_image:
        url=Image_url(store_image)
    get_store=db.query(Store).filter(Store.store_name==store_name , Store.status==1).first()
    if get_store:
        return {"status":0,"msg":"Store name already exit."}

    create_store=Store(store_name=store_name,address=address,
                       gst=gst,gst_pan=gst_pan,store_image=url,
                       
                       status=1,created_at=datetime.now())
    db.add(create_store)
    db.commit()
    return {"status":1,"msg":"store created"}
     

@router.post("/update_store")
async def updateStore(store_id:int=Form(...),
                          store_name:str=Form(None),
                          address:str=Form(None),
                          store_image: UploadFile = File(None),
                          gst:str=Form(...),
                          gst_pan:str=Form(...),
                          db:Session=Depends(get_db),
                          token: str = Security(token_header)
                          ):
    user = get_user_token(db,token=token)
    

    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType != 1:
        return {"status":0,"msg":"You are not authorized to create the store"}
    
    get_store=db.query(Store).filter(Store.id==store_id , Store.status==1).first()
    checkstore = db.query(Store).filter(Store.status==1,Store.store_name==store_name,Store.id!=store_id).first()
    if checkstore:
        return {"status":0,"msg":"Store name already exit."}

    if get_store:
        if store_name:
            get_store.store_name=store_name
        if address:
            get_store.address=address
        if gst:
            get_store.gst=gst
        if gst_pan:
            get_store.gst_pan=gst_pan
        if store_image:
            url=Image_url(store_image)
            get_store.store_image=url
        get_store.updated_at=datetime.now()
        db.commit()
        return {"status":1, "msg":"Store details updated successfully"}
    else:
        return {"status":0, "msg":"Given store id details not found"}


@router.post("/delete_store")
async def deletestore(store_id:int=Form(...),
                          
                          db:Session=Depends(get_db),
                          token: str = Security(token_header)):
    user  = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType !=1:
        return {"status":0,"msg":"You are not authorized to create the Store"}
    
    store=db.query(Store).filter(Store.id==store_id,Store.status==1).first()
    if store:
        store.status=-1
    else:
        return {"status":0, "msg":"Given store id details not found"}

    db.commit()
    return {"status":1, "msg":"store details successfully deleted"}
     
@router.post("/list_store_details")
async def list_store_details(db:Session=Depends(deps.get_db),
                   token: str = Security(token_header),page:int=1,
                   size:int=10,store_name:str=Form(None),address:str=Form(None),
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if  user.userType==1:
       
            get_store=db.query(Store).filter(Store.status==1)
            if store_name:
                get_store=get_store.filter(Store.store_name.like("%"+store_name+"%"))
            if address:
                get_store=get_store.filter(Store.address.like("%"+address+"%"))  
            get_store = get_store.order_by(Store.id.desc())
            totalCount= get_store.count()  
            total_page,offset,limit=get_pagination(totalCount,page,size)
            get_store=get_store.limit(limit).offset(offset).all()
            dataList =[]
            for row in get_store:
                
                dataList.append({"store_id":row.id,
                            "store_name":row.store_name,
                            "address":row.address,
                            "gst":row.gst,
                            "gst_pan":row.gst_pan,
                            "store_image_url":row.store_image,
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
