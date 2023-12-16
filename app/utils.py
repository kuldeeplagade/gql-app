from functools import wraps
import string
from random import choices
import jwt
from datetime import datetime,timedelta,timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from graphql import GraphQLError
from argon2 import PasswordHasher
from app.settings.config import TOKEN_EXPIRATION_TIME_MINITES,SECRET_KEY,ALGORITHM
from app.db.database import Session
from app.db.models import Employer,User



def generate_token(email):
    #now+token lifespan
    expiration_time =datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_TIME_MINITES)
    
    payload={
        "sub":email,
        "exp":expiration_time
    }
    
    token=jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    return token


def hash_password(pwd):
    ph=PasswordHasher()
    return ph.hash(pwd)

def varify_password(pwd_hash,pwd):
    ph=PasswordHasher()
    try:
        ph.verify(pwd_hash, pwd)
    except VerifyMismatchError:
        raise GraphQLError("Invalid Password")

def get_authenticated_user(context):
    request_object=context.get('request')
    auth_header=request_object.headers.get('Authorization')
    
    if auth_header:
        token=auth_header.split(" ")[1]
        
        try:
            payload=jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
            
            if datetime.now(timezone.utc)>datetime.fromtimestamp(payload['exp'], tz=timezone.utc):
                raise GraphQLError("Token Has Expired")
        
            session=Session()
            user= session.query(User).filter(User.email==payload.get('sub')).first()
            
            if not user:
                raise GraphQLError("Could Not Authenticate user")
            
            return user 
        except jwt.exceptions.InvalidSignatureError:
            raise GraphQLError("Invalid Authentiacton token")
    else:
        raise("Missing Authnetication Token") 

def admin_user(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        info =args[1]
        user=get_authenticated_user(info.context)
        
        if user.role!="admin":
            raise GraphQLError("You are not Athorized to perform this action")
        return func(*args ,*kwargs)
    
    return wrapper  
    
def  authd_user(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        info=args[1]
        get_authenticated_user(info.context)
        return func(*args,**kwargs)
    return wrapper

def authd_user_same_as(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        info =args[1]
        user=get_authenticated_user(info.context)
        uid=kwargs.get("user_id")
        
        if user.id!=uid:
            raise GraphQLError("You are not Athorized to perform this action")
        return func(*args ,*kwargs)
    
    return wrapper  
        