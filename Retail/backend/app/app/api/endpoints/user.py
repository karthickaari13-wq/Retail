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
token_header = APIKeyHeader(name="token", auto_error=False)
router = APIRouter()

@router.post("/create_user")
async def createUser(db:Session=Depends(get_db),
                     
                     name:str=Form(...),
                   
                     password:str=Form(...),
                     user_type:int=Form(...,description=("2>owner, 3>cashier,4>StaffMember")),
                     email:EmailStr=Form(None),
                     phone_no:str=Form(...),
                     address:str=Form(None),
                     language:str=Form(None),
                     store_id:int=Form(...),
                     pincode:int=Form(None),
                     country:str=Form(None),
                     city:str=Form(None),
                     latitude:str=Form(None),
                     longitude:str=Form(None),
                     token: str = Security(token_header)

                     ):
    
    hashPassword = get_password_hash(password)
    user = get_user_token(db,token=token)
    

    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}

    if user.userType == 3 or user.userType ==4:
        return {"status":0,"msg":"You are not authorized to create the user"}
    if user.userType == 2:
        if user_type==2:
            return {"status":0,"msg":"You are not authorized to create the owner"}
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        return {"status":0,"msg":"Store not found"}

    getUser =  get_by_user(db,phone=phone_no)
    if getUser:
        return {"status":0,"msg":"Given Phone number is already exist"}
    checkUser = db.query(User).filter(User.status==1)

    if checkUser.filter(User.email == email).first():
        return {"status":0,"msg":"Given Email is already exist"}
    if " " in phone_no:
        return {"status":0,"msg":"Don't give space between the phone Number"}
    if not phoneNo_validation(phone_no):
        return {"status":0,"msg":"Give a valid Phone Number"}
    addUser =  User(
                    
                    name = name,
                    userType=user_type,
                    phone=phone_no,
                    email=email,
                    address=address,
                    language=language,
                    password=hashPassword,
                    created_at = datetime.now(),
                    status =1,
                    store_id=store_id,
                    latitude=latitude,
                    longitude=longitude,
                    pincode=pincode,
                    country=country,
                    city=city
                    )
    db.add(addUser)
    db.commit()
    return {
        "status" : 1,
        "msg":"User created successfully"
    }

@router.post("/update_user")
async def updateUser(db:Session=Depends(get_db),
                     
                     userId:int=Form(...),
                     name:str = Form(None),
                     email:EmailStr = Form(None),
                     phone_no:str= Form(None),
                     address:str=Form(None),
                     language:str=Form(None),
                     store_id:int=Form(None),
                     pincode:int=Form(None),
                     country:str=Form(None),
                     city:str=Form(None),
                     latitude:str=Form(None),
                     longitude:str=Form(None),
                     token: str = Security(token_header)
                     
                     
                     
                     ):
    
    user  = get_user_token(db,token=token)

    if not user:
        return {"status":0,"msg":"Account details not found"}
    
    if user.userType == 3 or user.userType ==4:
        return {"status":0,"msg":"You are not allowed to update the user"}
    
    checkUser = db.query(User).filter(User.status==1)

    getUser = checkUser.filter(User.id == userId,User.status==1).first()

    if not getUser:
        return {"status":0,"msg":"Given user id details not found"}
    if user.userType == 2:
        if getUser.user_type==2:
            return {"status":0,"msg":"You are not authorized to udate the owner"}


    
    if email:
        if checkUser.filter(User.email == email,User.id!=userId).first():
            return {"status":0,"msg":"Given Email is already exist"}
        getUser.email = email
    if phone_no:
        if checkUser.filter(User.phone==phone_no,User.id!=userId).first():
            return {"status":0,"msg":"Givenn Phone Number is already exist"}
        if " " in phone_no:
            return {"status":0,"msg":"Don't give space between the phone Number"}
        if not phoneNo_validation(phone_no):
            return {"status":0,"msg":"Give a valid Phone Number"}
        getUser.phone =  phone_no
    
    if name:
        getUser.name=name

    if store_id:
        getUser.store_id=store_id

    if address:
        getUser.address=address
    
    if language:
        getUser.language=language
    if latitude:
        getUser.latitude=latitude
    if longitude:
        getUser.longitude=longitude
    if pincode:
        getUser.pincode=pincode
    if country:
        getUser.country=country
    if city:
        getUser.city=city



    getUser.updated_at=datetime.now()
    

    db.commit()

    return {"status":1, "msg":"User details updated successfully"}



@router.post("/list_user")
async def list_user(db:Session=Depends(deps.get_db),
                   page:int=1,
                   size:int=10,
                   userType:int=Form(...,description=("1>superadmin 2>owner, 3>cashier,4>StaffMember"))
                   ,name:str=Form(None),
                   phoneNumber:int=Form(None),
                   token: str = Security(token_header)
                   ):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.userType  in [3, 4]:
            return {"status":0,"msg":"not authorized"}

        if user.userType==2:
            if  userType==1:
                return {"status":0,"msg":"not authorized"}
            
        getuser =  db.query(User).\
            filter(User.userType == userType,
                User.status ==1 )
        if user.userType==2:
           
            getuser =  db.query(User).\
        filter(User.userType == userType,
            User.status ==1,User.store_id==user.store_id)
        

        if name:
            getuser = getuser.filter(User.name.like("%"+name+"%"))
        if phoneNumber:
            getuser = getuser.filter(User.phone.like("%"+str(phoneNumber)+"%"))
        getuser = getuser.order_by(User.id.desc())
        totalCount= getuser.count()
        total_page,offset,limit=get_pagination(totalCount,page,size)
        getuser=getuser.limit(limit).offset(offset).all()
        dataList =[]

        for row in getuser:
            dataList.append({
                "user_id" :row.id,
                "name":row.name,
                "userType":row.userType,
                "mobile":row.phone,
                "email":row.email,
                "phone_number":row.phone,
                "address":row.address ,
                "address":row.language ,
                "status":row.status,
                "user_type":row.userType,
                "latitude":row.latitude,
                "longitude":row.longitude,
                "pincode":row.pincode,
                "country":row.country,
                "city":row.city,


            })
        data=({"page":page,"size":size,"total_page":total_page,
                "total_count":totalCount,
                "items":dataList})
        return {"status":1,"msg":"Success","data":data}
        
    else:
        return({'status' :-1,
                'msg' :'Sorry! your login session expired. please login again.'}) 
    

@router.post("/delete_user")
async def deleteUser(db:Session=Depends(get_db),
                     userId:int=Form(...),
                     token: str = Security(token_header)
                     ):
    
    user  = get_user_token(db,token=token)

    if not user:
        return {"status":0,"msg":"Your login session expires.Please login again."}
    
    if user.userType  in [3, 4]:
            return {"status":0,"msg":"not authorized"}
    
    if user.userType == 1  :
        getUser = db.query(User).filter(User.id == userId,User.status == 1).first()

        if not getUser :
            return {"status":0, "msg":"Given user id details not found"}
    if user.userType == 2 :
        getUser = db.query(User).filter(User.id == userId,User.status == 1,User.store_id==user.store_id).first()

        if not getUser :
            return {"status":0, "msg":"Given user id details not found"}
    getUser.status = -1
    db.commit()
    return {"status":1, "msg":"User details successfully deleted"}
    

@router.post("/view_user")
async def view_user(db:Session=Depends(get_db),
                     userId:int=Form(...),
                     token: str = Security(token_header)):
    user=deps.get_user_token(db=db,token=token)
    if not user:
        return({'status' :-1,
                'msg' :'Sorry! your login session expired. please login again.'}) 
    if user.userType  in [3, 4]:
            return {"status":0,"msg":"not authorized"}
    getuser =  db.query(User).\
                filter(User.id == userId,
                    User.status ==1 ).first()
    if not getuser :
            return {"status":0, "msg":"Given user id details not found"}
    dataList={
        "user_id" :getuser.id,
        "name":getuser.name,
        "address":getuser.address,
        "language":getuser.language,
        "email":getuser.email,
        "phone_number":getuser.phone,
        "store_id":getuser.store_id ,
        "status":getuser.status,
        "created_at":getuser.created_at
    }
    
    return {"status":1,"msg":"Success","data":dataList}







    
    