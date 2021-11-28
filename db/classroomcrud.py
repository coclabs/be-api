from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import model
from . import schemas
import math
import time
import datetime
from sqlalchemy import delete
from sqlalchemy import desc

from datetime import datetime


def get_all_course_teacher(db: Session, teacherid: int):
    return (
        db.query(model.Course)
        .join(model.CourseTeacher)
        .filter(model.CourseTeacher.teacherid == teacherid)
        .all()
    )


def get_all_course_student(db: Session, studentid: int):
    return (
        db.query(model.Course)
        .join(model.StudentEnrollCourse)
        .filter(model.StudentEnrollCourse.studentid == studentid)
        .all()
    )


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


def create_student_enroll_course(db: Session, studentid: int, courseid: int):
    db_studentenrollcourse = model.StudentEnrollCourse(
        studentid=studentid, courseid=courseid
    )
    db.add(db_studentenrollcourse)
    db.commit()
    db.refresh(db_studentenrollcourse)
    return db_studentenrollcourse


def create_course_assignment(db: Session, assignmentid: int, courseid: int):
    db_course_assignment = model.CourseAssignment(
        assignmentid=assignmentid, courseid=courseid
    )
    db.add(db_course_assignment)
    db.commit()
    db.refresh(db_course_assignment)
    return db_course_assignment


def read_course_assignment(db: Session, courseid: int):
    return (
        db.query(model.Assignment)
        .join(model.CourseAssignment)
        .filter(model.CourseAssignment.courseid == courseid)
        .filter(model.CourseAssignment.status == True)
        .all()
    )


def read_course_assignment_by_id(db: Session, courseid: int, assignmentid: int):
    return (
        db.query(model.CourseAssignment)
        .join(model.Assignment)
        .filter(
            model.CourseAssignment.courseid == courseid,
            model.CourseAssignment.assignmentid == assignmentid,
        )
        .first()
    )


def read_course_assignment_status(db: Session, assignmentid, courseid: int):
    return (
        db.query(model.CourseAssignment.status)
        .filter(
            model.CourseAssignment.courseid == courseid,
            model.CourseAssignment.assignmentid == assignmentid,
            model.CourseAssignment.status == True,
        )
        .first()
    )


def toggle_course_assignment(db: Session, courseid: int, assignmentid):

    status = (
        db.query(model.CourseAssignment.status)
        .filter(
            model.CourseAssignment.courseid == courseid,
            model.CourseAssignment.assignmentid == assignmentid,
        )
        .first()
    )

    if status[0] is True:
        x = False
    else:
        x = True

    print(x)

    db.query(model.CourseAssignment).filter(
        model.CourseAssignment.courseid == courseid,
        model.CourseAssignment.assignmentid == assignmentid,
    ).update({"status": (x)})
    db.commit()
    return 0


def read_students_notin_this_course(db: Session, courseid: int):

    return db.query(model.Student).all()


def read_course(db: Session, courseid: int):

    return db.query(model.Course).filter(model.Course.courseid == courseid).first()


def create_course(db: Session, course: schemas.CourseTeacherCreate):

    db_course = model.Course(
        coursename=course.coursename,
        coursedescription=course.coursedescription,
        courseobjective=course.courseobjective,
        imagesrc=course.imagesrc,
        coursecode=course.coursecode,
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
        avatar=student.avatar,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def create_student_assignment(
    db: Session,
    courseid: int,
    assignmentid: int,
    totalscore: int,
    studentid: int,
    totalcorrect: int,
    totalnotcorrect: int,
):

    db_student_assignment = model.StudentAssignment(
        courseid=courseid,
        assignmentid=assignmentid,
        totalscore=totalscore,
        studentid=studentid,
        totalcorrect=totalcorrect,
        totalnotcorrect=totalnotcorrect,
    )
    db.add(db_student_assignment)
    db.commit()
    db.refresh(db_student_assignment)
    return db_student_assignment


def read_student_assignment(db: Session, courseid: int, studentid: int):
    return (
        db.query(model.StudentAssignment, model.Assignment)
        .join(model.Student)
        .join(model.Assignment)
        .filter(
            model.StudentAssignment.courseid == courseid,
            model.Student.studentid == studentid,
        )
        .order_by(model.StudentAssignment.created_at)
        .all()
    )


def read_student_assignment_question_by_id_studentassignmentid(
    db: Session, studentid: int, studentassignmentid: int
):
    return (
        db.query(model.StudentAssignmentQuestion)
        .join(model.StudentAssignment)
        .filter(model.StudentAssignment.studentid == studentid)
        .filter(
            model.StudentAssignmentQuestion.studentassigmentid == studentassignmentid
        )
        .all()
    )


def count_attempt(db: Session, studentid: int, assignmentid: int):
    db.query(model.StudentAssignment).filter(
        model.Student.studentid == studentid,
        model.StudentAssignment.assignmentid == assignmentid,
    )
    return (
        db.query(model.StudentAssignment)
        .filter(
            model.Student.studentid == studentid,
            model.StudentAssignment.assignmentid == assignmentid,
        )
        .count()
    )


def create_student_assignmentquestion(
    db: Session,
    studentassignmentid: int,
    questionnumber: int,
    studentscore: int,
    testresult: str,
    studentanswer: str,
    totalcorrect: int,
    totalnotcorrect: int,
):

    db_student_assignment_question = model.StudentAssignmentQuestion(
        studentassigmentid=studentassignmentid,
        questionnumber=questionnumber,
        studentscore=studentscore,
        testresult=testresult,
        studentanswer=studentanswer,
        totalcorrect=totalcorrect,
        totalnotcorrect=totalnotcorrect,
    )
    db.add(db_student_assignment_question)
    db.commit()
    db.refresh(db_student_assignment_question)
    return db_student_assignment_question


def update_student_assignment(
    db: Session,
    courseid: int,
    studentassignmentid: int,
    totalscore: int,
    totalcorrect: int,
    totalnotcorrect: int,
):
    db.query(model.StudentAssignment).filter(
        model.StudentAssignment.courseid == courseid,
        model.StudentAssignment.studentassigmentid == studentassignmentid,
    ).update({"totalscore": (totalscore)})
    db.query(model.StudentAssignment).filter(
        model.StudentAssignment.courseid == courseid,
        model.StudentAssignment.studentassigmentid == studentassignmentid,
    ).update({"totalcorrect": (totalcorrect)})
    db.query(model.StudentAssignment).filter(
        model.StudentAssignment.courseid == courseid,
        model.StudentAssignment.studentassigmentid == studentassignmentid,
    ).update({"totalnotcorrect": (totalnotcorrect)})

    db.commit()


def create_studentassignmentrecord(
    db: Session,
    courseid: int,
    assignmentid: int,
    max: int,
    min: int,
    allscore: int,
    attempt: int,
):

    db_student_assignment_record = model.StudentAssignmentRecord(
        courseid=courseid,
        assignmentid=assignmentid,
        max=max,
        min=min,
        allscore=allscore,
        attempt=attempt,
        firstdonetime=datetime.now(),
        lastdonetime=datetime.now(),
    )
    db.add(db_student_assignment_record)
    db.commit()
    db.refresh(db_student_assignment_record)
    return db_student_assignment_record


def read_student_assignment_record_by_assignmentid(db: Session, assignmentid: int):
    return (
        db.query(model.StudentAssignmentRecord)
        .filter(model.StudentAssignmentRecord.assignmentid == assignmentid)
        .first()
    )


def read_all_student_assignment_record(db: Session, courseid: int):
    return (
        db.query(model.StudentAssignmentRecord)
        .filter(model.StudentAssignmentRecord.courseid == courseid)
        .all()
    )


def update_student_assignment_record(
    db: Session,
    courseid: int,
    assignmentid: int,
    max: int,
    min: int,
    allscore: int,
    attempt: int,
):
    db.query(model.StudentAssignmentRecord).filter(
        model.StudentAssignmentRecord.courseid == courseid,
        model.StudentAssignmentRecord.assignmentid == assignmentid,
    ).update({"max": (max)})

    db.query(model.StudentAssignmentRecord).filter(
        model.StudentAssignmentRecord.courseid == courseid,
        model.StudentAssignmentRecord.assignmentid == assignmentid,
    ).update({"min": (min)})

    db.query(model.StudentAssignmentRecord).filter(
        model.StudentAssignmentRecord.courseid == courseid,
        model.StudentAssignmentRecord.assignmentid == assignmentid,
    ).update({"allscore": (allscore)})

    db.query(model.StudentAssignmentRecord).filter(
        model.StudentAssignmentRecord.courseid == courseid,
        model.StudentAssignmentRecord.assignmentid == assignmentid,
    ).update({"attempt": (attempt)})

    db.query(model.StudentAssignmentRecord).filter(
        model.StudentAssignmentRecord.courseid == courseid,
        model.StudentAssignmentRecord.assignmentid == assignmentid,
    ).update({"lastdonetime": (datetime.now())})

    db.commit()


def read_all_student_in_course(db: Session, courseid: int):

    return (
        db.query(model.Student)
        .join(
            model.StudentEnrollCourse,
            model.Student.studentid == model.StudentEnrollCourse.studentid,
        )
        .filter(model.StudentEnrollCourse.courseid == courseid)
        .all()
    )


def read_record_student(db: Session, assignmentid: int):
    return (
        db.query(model.StudentAssignment.studentid)
        .filter(model.StudentAssignment.assignmentid == assignmentid)
        .all()
    )


def read_student(db: Session, studentid: int):
    return db.query(model.Student).filter(model.Student.studentid == studentid).first()
