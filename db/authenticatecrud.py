from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import model
from . import schemas
import math
import time 
import datetime 
from sqlalchemy import delete
from sqlalchemy import desc

def authenticate_teacher(db, username: str, password: str):
    teacher = db.query(model.Teacher).filter(model.Teacher.username == username).first()
    if not teacher:
        return False
        
    if not bcrypt.verify(password,teacher.hashedpassword):
        return False
    return teacher

def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password,hashed_password)


def get_teacher_by_username(db: Session, username:str):
    return db.query(model.Teacher).filter(model.Teacher.username == username).first()