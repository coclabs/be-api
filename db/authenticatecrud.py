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

    if not bcrypt.verify(password, teacher.hashedpassword):
        return False
    return teacher


def authenticate_student(db, username: str, password: str):
    student = db.query(model.Student).filter(model.Student.username == username).first()
    if not student:
        return False

    if not bcrypt.verify(password, student.hashedpassword):
        return False
    return student


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)


def get_teacher_by_username(db: Session, username: str):
    return db.query(model.Teacher).filter(model.Teacher.username == username).first()


def get_teacher_by_id(db: Session, id: int):
    return db.query(model.Teacher).filter(model.Teacher.teacherid == id).first()


def get_student_by_id(db: Session, id: int):
    return db.query(model.Student).filter(model.Student.studentid == id).first()


def get_student_by_username(db: Session, username: str):
    return db.query(model.Student).filter(model.Student.username == username).first()
