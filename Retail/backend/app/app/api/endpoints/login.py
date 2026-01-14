
from fastapi import APIRouter, Depends, Form,requests
from sqlalchemy.orm import Session
from app.models import ApiTokens,User,UserOtp
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import or_
import random
from datetime import datetime, timedelta, timezone
router = APIRouter()
dt = str(int(datetime.utcnow().timestamp()))

#Check Token
# @router.post("/check_token")
# async def checkToken(*,db: Session = Depends(deps.get_db),
#                       token: str = Form(...)):
    
#     checkToken = db.query(ApiTokens).filter(ApiTokens.token == token,
#                                            ApiTokens.status == 1).first()
#     if checkToken:
#         return {"status":1,"msg":"Success."}
#     else:
#         return {"status":0,"msg":"Failed."}

def generate_otp():
    return str(random.randint(100000, 999999))

@router.post("/login")
async def login(*,db: Session = Depends(deps.get_db),
                number: str = Form(None),
               
               ):
    
    
    
    user = deps.authenticate(db,phone = number)
    if  user==None:
        return {"status": 0,"msg": "Invalid mobilenumber ."}
    
    else:
        
        otp = generate_otp()  # e.g. 6-digit
        expire_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        user.otp = otp
        user.otpExpireAt = expire_at

       
        db.commit()
        await send_mail(
        receiver_email=user.email,
        message=f"Your OTP is {otp}. Valid for 5 minutes."
        )

        return {
        "status": 1,
        "msg": "OTP sent successfully",
        "otp":otp,
        "user_id":user.id,
        "mobile_number":user.phone}
        
    
    
#2.Logout
@router.post("/logout")
async def logout(db: Session = Depends(deps.get_db),
                 token: str = Form(...)):

    user = deps.get_user_token(db = db,token = token)
    if user:
        check_token = db.query(ApiTokens).\
            filter(ApiTokens.token == token,ApiTokens.status == 1).first()

        if check_token:
            check_token.status = -1
            db.commit()
            return ({"status": 1,"msg": "Success."}) 
        else:
            return ({"status": 0,"msg": "Failed."})
    else:
        return ({"status":0,"msg":"Invalid user."})
    




    
@router.post("/resend_otp")
async def resendOtp(db:Session = Depends(deps.get_db),
                    number:str= Form(...)):
    user = deps.authenticate(db,phone = number)
    if not user:
        return {"status": 0,"msg": "Invalid mobilenumber ."}
    
    else:
        
        otp = generate_otp()  
        expire_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        user.otp = otp
        user.otpExpireAt = expire_at

       
        db.commit()
        await send_mail(
        receiver_email=user.email,
        message=f"Your OTP is {otp}. Valid for 5 minutes."
        )

        return {
        "status": 1,
        "msg": "OTP sent successfully",
        "otp":otp,
        "user_id":user.id}
        
 


@router.post("/verify_otp")
def verify_otp(
    db: Session = Depends(deps.get_db),
    user_id:int=Form(...),
    otp: str = Form(...),
    
):
    user = db.query(User).filter(
        User.status == 1,User.id==user_id
    ).first()

    if not user:
        return {"status": 0, "msg": "Invalid session"}

   
    if user.otp != otp:
        return {"status": 0, "msg": "Invalid OTP"}
    otp_expiry = user.otpExpireAt

    otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)
    if otp_expiry < datetime.now(timezone.utc):
        return {"status": 0, "msg": "OTP expired"}


    user.otp = None
    user.otpExpireAt = None
    user.reset_key = None

    key = ''
    char1 = '0123456789abcdefghijklmnopqrstuvwxyz'
    char2 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    characters = char1 + char2
    for i in range(0, 30):
        key += characters[random.randint(
                0, len(characters) - 1)]
        
    


    
    addToken = ApiTokens(
        user_id=user_id,
        token=key,
        created_at=datetime.now(timezone.utc), 
        validity=1,
        status=1
    )

    db.add(addToken)
    db.commit()
    return {'status':1,
        'token': key,
        "user_id":user.id,
        "user_type":user.userType,
        'msg': 'Successfully LoggedIn.',  
        'status': 1
        }


