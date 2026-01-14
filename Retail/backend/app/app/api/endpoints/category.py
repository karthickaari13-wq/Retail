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
@router.post("/create_category")
async def createCategory(category_name:str=Form(...),
                         image: UploadFile = File(None),
                         description:str=Form(None),db:Session=Depends(get_db),token: str = Security(token_header)):
    user = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType in [3,4]:
        return {"status":0,"msg":"You are not authorized to create the category"}
    checkcategory_name = db.query(Category).filter(Category.status==1,Category.category_name==category_name).first()
    if checkcategory_name:
        return {"status":0,"msg":"Given Category is already exist"}
    if image:
       url=Image_url(image)
    create_category=Category(category_name=category_name,
                             image_url=url,description=description,

                             status=1,created_at=datetime.now())
    db.add(create_category)
    db.commit()
    return {"status":1,"msg":"category created"}
     

@router.post("/update_category")
async def updateCategory(category_id:int=Form(...),
                          category_name:str=Form(None),
                          image: UploadFile = File(None),
                         description:str=Form(None),
                          db:Session=Depends(get_db),
                          token: str = Security(token_header)
                          ):
    user = get_user_token(db,token=token)
    

    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType in [3,4]:
        return {"status":0,"msg":"You are not authorized to create the category"}
    
    get_category=db.query(Category).filter(Category.id==category_id , Category.status==1).first()
    if not get_category:
        return {"status":0, "msg":"Given category id details not found"}


    if category_name:
        checkcategory_name = db.query(Category).filter(Category.status==1,Category.category_name==category_name,Category.id!=category_id ).first()
        if checkcategory_name:
            return {"status":0,"msg":"Given Category is already exist"}
    if get_category:
        get_category.category_name=category_name
    if image:
        url=Image_url(image)
        get_category.image_url=url
    if description:
        get_category.description=description
    get_category.updated_at=datetime.now()
    db.commit()
    return {"status":1, "msg":"Category details updated successfully"}
    
       

@router.post("/delete_category")
async def deleteCategory(category_id:int=Form(...),
                          
                          db:Session=Depends(get_db),
                          token: str = Security(token_header)):
    user  = get_user_token(db,token=token)
    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType in [3,4]:
        return {"status":0,"msg":"You are not authorized to create the category"}
    
    category=db.query(Category).filter(Category.id==category_id,Category.status==1).first()
    if category:
        category.status=-1
    else:
        return {"status":0, "msg":"Given category id details not found"}

    db.commit()
    return {"status":1, "msg":"Category deleted successfully"}
     
@router.post("/list_category_details")
async def list_category_details(db:Session=Depends(deps.get_db),
                   token: str = Security(token_header),page:int=1,
                   size:int=10,category_name:str=Form(None),
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if  user.userType not in [3,4]:
       
            categoery=db.query(Category).filter(Category.status==1)
            if category_name:
                categoery=categoery.filter(Category.category_name.like("%"+category_name+"%"))
            categoery = categoery.order_by(Category.id.desc())
            totalCount= categoery.count()  
            total_page,offset,limit=get_pagination(totalCount,page,size)
            categoery=categoery.limit(limit).offset(offset).all()
            dataList =[]
            for row in categoery:
                
                dataList.append({"category_id":row.id,
                            "category_name":row.category_name,
                            "image_url":row.image_url,
                            "description":row.description,
                            "created_at":row.created_at})
            data=({"page":page,"size":size,"total_page":total_page,
                    "total_count":totalCount,
                    "items":dataList})
            return {"status":1,"msg":"Success","data":data}
        else:
            return {"status":0,"msg":"only owner and  admin can  access"}
    else:
        return({'status' :-1,
                'msg' :'Sorry! your login session expired. please login again.'})
