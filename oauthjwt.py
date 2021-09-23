from datetime import datetime, timedelta
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from userdb import usercrud, userdatabase, userschemas, userdatabase
from sqlalchemy.orm import Session
from typing import List
from passlib.hash import bcrypt

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

db = userdatabase.SessionLocal()


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


def get_user(db, username: str):
    userobj = usercrud.get_user_by_email(db, username)
    return userobj


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/")
async def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code="status.HTTP_401_UNAUTHORIZED",
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token")
def login_for_access_token(user: userschemas.UserCreate):

    user = authenticate_user(db, user.email, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"accesstoken": access_token}


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100,  current_user: User =  Depends(get_current_user)  ):


# items = crud.get_items(db, skip=skip, limit=limit)
# return items


@app.post("/users/", response_model=userschemas.User)
def create_user(user: userschemas.UserCreate):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return usercrud.create_user(db=db, user=user)


# @app.get("/users/me", response_model=schemas.User)
# def read_user( current_user: User = Depends(get_current_user)):


@app.get("/users/", response_model=List[userschemas.User])
def read_users(skip: int = 0, limit: int = 100):
    users = usercrud.get_users(db, skip=skip, limit=limit)
    return users


# แก้เป็นข้องuserนั้น
# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#    current_user: User = Depends(get_current_user), item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)
