from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import model
from . import schemas
import math
import time 
import datetime 
from sqlalchemy import delete
from sqlalchemy import desc



def create_teacher(db: Session, teacher: schemas.TeacherCreate):
    
    db_teacher = model.Teacher(firstname=teacher.firstname,lastname=teacher.lastname,username=teacher.username hashedpassword=bcrypt.hash(user.password))
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher



def create_course(db: Session, course:schemas.CourseCreate):
    
    db_course = model.Course(coursename=course.coursename,coursedescription=course.coursedescription,courseobjective=course.courseobjective)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def create_assignmentquestion(db: Session ,courseid:int,teacherid:int):

    db_couresteacher = model.CourseTeacher(courseid=courseid,teacherid=teacherid)
    db.add(couresteacher)
    db.commit()
    db.refresh(couresteacher)
    return couresteacher     



