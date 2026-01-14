
from typing import Generator, Any, Optional
from fastapi.security import OAuth2PasswordBearer
import datetime
from sqlalchemy.orm import Session
from app import models
import random
from sqlalchemy import or_
from app.core import security
from app.core.config import settings
from app.database.session import SessionLocal
from datetime import datetime,timedelta
import hashlib
from app.models import ApiTokens,User
from app.core.config import settings
import os,sys

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()



def get_user_token(db: Session, *, token: str) :
    get_token=db.query(ApiTokens).filter(ApiTokens.token== token ,
                                            ApiTokens.status==1).first()

    if get_token: 
        return db.query(User).filter(User.id == get_token.user_id,
                                         User.status == 1).first()            
    else:
        return None

def get_by_user(db: Session, *, phone: str):
        
        getUser=db.query(models.User).\
            filter(models.User.status == 1,models.User.phone==phone).first()
        if not getUser:
             return None
    
        return getUser


def authenticate(db: Session, *, phone: str,
                  
                    ) -> Optional[models.User]:
       
        
        
        return  get_by_user(db, phone=phone)


def get_user_type(user_type: Any):
    if user_type == 1:
        return "Admin"

    elif user_type == 2:
        return "Customer"

    else:
        return ""

def verify_hash(hash_data:str, included_variable:str):

    included_variable = (included_variable + settings.SALT_KEY).encode("utf-8")
    real_hash = hashlib.sha1(included_variable).hexdigest()
    if hash_data == real_hash:
        return True
        
    return False

def checkSignature(signature:str, timestamp:str, device_id:str):

    included_variable = (device_id + timestamp + settings.SALT_KEY).encode("utf-8")
    real_hash = hashlib.sha1(included_variable).hexdigest()
    if signature == real_hash:
        return True
    return False


def get_otp():
    otp = ''
    reset = ""
    characters = '0123456789'
    char1 = 'qwertyuioplkjhgfdsazxcvbnm0123456789'
    char2 = 'QWERTYUIOPLKJHGFDSAZXCVBNM'
    reset_character = char1 + char2
    
    otp = random.randint(111111, 999999)
   
    for j in range(0, 20):
        reset += reset_character[random.randint(
            0, len(reset_character) - 1)]

    created_at = datetime.now(settings.tz_IN)
    expire_time = created_at +timedelta(minutes=2)
    expire_at = expire_time.strftime("%Y-%m-%d %H:%M:%S")
    otp_valid_upto = expire_time.strftime("%d-%m-%Y %I:%M %p")

    return [otp, reset , created_at, expire_time, expire_at, otp_valid_upto] 


def hms_to_s(s):
    t = 0
    for u in s.split(':'):
        t = 60 * t + int(u)
    return t

def phoneNo_validation(phonenumber:str):
    length = 10
    length_of_phonenumber =  len(phonenumber)
    if length == length_of_phonenumber:
        return True
    return False


def Image_url(image):
    
            if image:    
                data = image.filename
                name = data.split(".")[0]
                timestampData = int(datetime.utcnow().timestamp())    
                fileName =f"{str(timestampData)}_{data}"
                base_dir = r'D:\retail_image\image'

                try:
                    os.makedirs(base_dir, mode=0o777, exist_ok=True)
                except OSError as e:
                    sys.exit("Can't create {dir}: {err}".format(
                        dir=base_dir, err=e))
                
                file_path = os.path.join(base_dir, fileName)

                # Save the uploaded file to the target directory
                with open(file_path, "wb") as file:
                    file.write(image.file.read())


                url = f"D:\retail_image\image/{fileName}"
                return url
