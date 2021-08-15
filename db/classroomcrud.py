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

    db_teacher = model.Teacher(
        firstname=teacher.firstname,
        lastname=teacher.lastname,
        username=teacher.username,
        hashedpassword=bcrypt.hash(teacher.password),
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


def create_course(db: Session, course: schemas.CourseTeacherCreate):

    db_course = model.Course(
        coursename=course.coursename,
        coursedescription=course.coursedescription,
        courseobjective=course.courseobjective,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def create_course_teacher(db: Session, courseid: int, teacherid: int):

    db_couresteacher = model.CourseTeacher(courseid=courseid, teacherid=teacherid)
    db.add(db_couresteacher)
    db.commit()
    db.refresh(db_couresteacher)
    return db_couresteacher


def create_student(db: Session, student: schemas.StudentCreate):

    db_student = model.Student(
        firstname=student.firstname,
        lastname=student.lastname,
        username=student.username,
        hashedpassword=bcrypt.hash(student.password),
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
