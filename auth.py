from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
import json
from fastapi.encoders import jsonable_encoder


router = APIRouter(prefix="/auth",tags=['auth'])


SECRET_KEY = "jgdflkgjdflsgjldfsjgfskgfadsfrweoqajlgdfgpnaskjglsdfjglsdfjlgjsdfgkljsdfgjsdflgjsdf"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated = "auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

 
class CreateUserRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str 
    #grant_type: str = "password"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
 



@router.post("/signup",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,create_user_request:CreateUserRequest):
    create_user_model = Users(username=create_user_request.username,hash_password = bcrypt_context.hash(create_user_request.password))
    db.add(create_user_model)
    db.commit()



@router.post("/token",response_model=Token)
async def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()], db:db_dependency):
        #return {form_data.username}
        user = authenticate_user(form_data.username,form_data.password,db)#.get(form_data.username)
        #return {json.dumps(user_dict)}
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password with system")

        token = create_access_token(user.username,user.id,timedelta(minutes=20 ))
        return {"access_token": token, "token_type": "bearer"}


# @app.get("/user-list--")
# async def get_users(form_data:oauth2_bearer,  db:db_dependency):
#     users = db.query(Users).all()
#     return {"status_code":status.HTTP_200_OK,"content": jsonable_encoder(users)}


def authenticate_user(username:str,password:str,db):
    auser = db.query(Users).filter(Users.username==username).first()
    if not auser:
        return False
    if not bcrypt_context.verify(password,auser.hash_password):
        return False
    return auser

def create_access_token(uname:str, uid=int, expire_time=timedelta):
    encode = {'sub':uname,'id':uid }
    exp_time = datetime.now( ) + expire_time
    encode.update({'exp':exp_time})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

def get_current_user(usertoken:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload= jwt.decode(usertoken,SECRET_KEY,algorithms=ALGORITHM)
        username = payload.get('sub')
        user_id = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Payload information")
        return {'username': username,'id':user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not Validate user")



   