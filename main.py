# from typing import Annotated
# from fastapi import Depends, FastAPI,HTTPException,status
# from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
# from pydantic import BaseModel
# import json


# fake_users_records = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "fakehashedsecret", # password = secret
#         "disabled": False,
#     },
#     "alice": {
#         "username": "alice",
#         "full_name": "Alice Wonderson",
#         "email": "alice@example.com",
#         "hashed_password": "fakehashedsecret2", # password = secret2
#         "disabled": False,
#     },
# }


# app = FastAPI()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# class User(BaseModel):
#         username:str
#         email:str | None = None
#         full_name:str | None = None
#         disabled: bool | None = None
    
# class UserInDB(User):
#         hashed_password:str


# def get_user(dbrecords,username:str):
#     if username in dbrecords:
#         user_dict = dbrecords[username]
#         return UserInDB(**user_dict)


# def fake_hash_password(password:str):
#         return "fakehashed"+password

# def fake_decode_token(token):
#         user = get_user(fake_users_records, token)
#         return user

# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user

# async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)],):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# @app.post("/token")
# async def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()]):
#         #return {form_data.username}
#         user_dict = fake_users_records[form_data.username]#.get(form_data.username)
#         #return {json.dumps(user_dict)}
#         if not user_dict:
#             raise HTTPException(status_code=400, detail="Incorrect username or password")
#         user = UserInDB(**user_dict)
#         hashed_password = fake_hash_password(form_data.password)
#         if not hashed_password == user.hashed_password:
#             raise HTTPException(status_code=400, detail="Incorrect password")

#         return {"access_token": user.username, "token_type": "bearer"}



# @app.get("/users/me")
# async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
#     return current_user


# @app.get("/items/")
# async def read_items(token:Annotated[str,Depends(oauth2_scheme)]):
#         return {"token":"token"}




from fastapi import FastAPI,status,Depends,HTTPException
from database import engine, SessionLocal
from typing import Annotated
import models
from sqlalchemy.orm import Session
import auth
from auth import get_db, get_current_user
from fastapi.encoders import jsonable_encoder


app = FastAPI()

app.include_router(auth.router)


models.Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
current_user_dependency = Annotated[dict,Depends(get_current_user)]


@app.get("/current-user",status_code=status.HTTP_200_OK)
async def user(user:current_user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    return {"User":user}


@app.get("/user-list")
async def get_users(user:current_user_dependency,  db:db_dependency):
    users = db.query(models.Users).all()
    return {"status_code":status.HTTP_200_OK,"content": jsonable_encoder(users)}









