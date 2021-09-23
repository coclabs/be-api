from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import model
from . import schemas
import math
import time
import datetime
from sqlalchemy import delete
from sqlalchemy import desc
from typing import List, Tuple


def get_user(db: Session, user_id: int):
    return db.query(model.User).filter(model.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(model.User).filter(model.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):

    db_user = model.User(email=user.email, hashed_password=bcrypt.hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = model.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


######### Question and test
def create_question(db: Session, question: schemas.QuestionForm):

    db_user = model.Question(
        questioninit=question.questioninit,
        questiontopic=question.questiontopic,
        questiondescription=question.questiondescription,
        questiondifficulty=question.questiondifficulty,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_question_test(db: Session, test: schemas.TestForm, question_id: int):
    db_test = model.Test(**test.dict(), question_id=question_id)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def get_tests(db: Session, question_id: int):
    return db.query(model.Test).filter(model.Test.question_id == question_id).all()


def create_tag(db: Session, tag: schemas.TagForm):

    db_test = model.Tag(tagid=tag.tagid, tagname=tag.tagname)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def create_questiontag(db: Session, questiontag: schemas.QuestionTagForm):

    db_test = model.QuestionTagForm(
        questionid=questiontag.questionid, tagid=questiontag.tagid
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def get_questions(db: Session, page: int):

    limit = 10
    skip = page * 10 - 10

    return (
        db.query(model.Question)
        .order_by(model.Question.questionid.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_questionbyquestionid(db: Session, questionid: int):

    return (
        db.query(model.Question)
        .filter(model.AssignmentQuestion.questionid == questionid)
        .first()
    )


def get_questionpage(db: Session):

    return math.ceil(db.query(model.Question).count() / 10)


def create_assignment(db: Session, assignment: schemas.AssignmentForm):

    db_test = model.Assignment(
        assignmentname=assignment.assignmentname,
        assignmentdescription=assignment.assignmentdescription,
        maxpossiblescore=assignment.maxpossiblescore,
        visibleat=assignment.visibleat.replace("T", " ").replace(":00", ""),
        avaliableat=assignment.avaliableat.replace("T", " ").replace(":00", ""),
        disableat=assignment.disableat.replace("T", " ").replace(":00", ""),
        invisibleat=assignment.invisibleat.replace("T", " ").replace(":00", ""),
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def create_exam(db: Session, exam: schemas.ExamForm):

    db_test = model.Exam(
        examname=exam.examname,
        examdescription=exam.examdescription,
        maxpossiblescore=exam.maxpossiblescore,
        visibleat=datetime.datetime.strptime(
            exam.visibleat.replace("T", " "), "%Y-%m-%d %H:%M"
        ),
        avaliableat=datetime.datetime.strptime(
            exam.avaliableat.replace("T", " "), "%Y-%m-%d %H:%M"
        ),
        disableat=datetime.datetime.strptime(
            exam.disableat.replace("T", " "), "%Y-%m-%d %H:%M"
        ),
        invisibleat=datetime.datetime.strptime(
            exam.invisibleat.replace("T", " "), "%Y-%m-%d %H:%M"
        ),
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def create_assignmentquestion(
    db: Session, assigmentquestion: schemas.AssignmentQuestionForm, assignmentid: int
):
    for questionrealid in assigmentquestion.questionid:
        db_test = model.AssignmentQuestion(
            assignmentid=assignmentid, questionid=questionrealid
        )
        db.add(db_test)
        db.commit()
        db.refresh(db_test)
    return db_test


def get_allquestions(db: Session):
    return db.query(model.Question).all()


def get_assignmentpage(db: Session):

    return math.ceil(db.query(model.Assignment).count() / 10)


def get_assignments(db: Session, page: int):

    limit = 10
    skip = page * 10 - 10
    assignment = (
        db.query(model.Assignment)
        .order_by(model.Assignment.assignmentid.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    print(assignment)
    return assignment


def get_assignments_assignmentid(db: Session, page: int):

    limit = 10
    skip = page * 10 - 10

    return (
        db.query(model.Assignment.assignmentid)
        .order_by(model.Assignment.assignmentid.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_onequestion(db: Session, questionid: int):
    db.query(model.AssignmentQuestion).filter(
        model.AssignmentQuestion.questionid == questionid
    ).delete()
    db.query(model.Test).filter(model.Test.question_id == questionid).delete()
    db.query(model.Question).filter(model.Question.questionid == questionid).delete()
    # update({"testcases": ("ppo")})
    db.commit()

    return 0


def update_question(db: Session, questiontest: schemas.QuestionTestForm):
    questionid = questiontest.questionid
    db.query(model.Question).filter(model.Question.questionid == questionid).update(
        {"questiondescription": (questiontest.questiondescription)}
    )
    db.query(model.Question).filter(model.Question.questionid == questionid).update(
        {"questiontopic": (questiontest.questiontopic)}
    )
    db.query(model.Question).filter(model.Question.questionid == questionid).update(
        {"questiondifficulty": (questiontest.questiondifficulty)}
    )
    db.query(model.Question).filter(model.Question.questionid == questionid).update(
        {"questioninit": (questiontest.questioninit)}
    )
    db.query(model.Test).filter(model.Test.question_id == questionid).update(
        {"exampletestcases": (questiontest.exampletestcases)}
    )
    db.query(model.Test).filter(model.Test.question_id == questionid).update(
        {"testcases": (questiontest.testcases)}
    )
    db.query(model.Test).filter(model.Test.question_id == questionid).update(
        {"testsolution": (questiontest.testsolution)}
    )

    db.commit()
    return 0


def delete_multiplequestion(db: Session, questionid: schemas.ArrayQuestionid):

    for x in questionid.questionid:
        db.query(model.AssignmentQuestion).filter(
            model.AssignmentQuestion.questionid == x
        ).delete()
        db.query(model.Test).filter(model.Test.question_id == x).delete()
        db.query(model.Question).filter(model.Question.questionid == x).delete()

    db.commit()
    return 0


def delete_oneassignment(db: Session, assignmentid: schemas.Assignmentid):
    db.query(model.AssignmentQuestion).filter(
        model.AssignmentQuestion.assignmentid == assignmentid
    ).delete()
    db.query(model.Assignment).filter(
        model.Assignment.assignmentid == assignmentid
    ).delete()
    db.commit()

    return 0


def delete_multipleassignment(db: Session, assignmentid: schemas.ArrayAssignmentid):

    for x in assignmentid.assignmentid:
        db.query(model.AssignmentQuestion).filter(
            model.AssignmentQuestion.assignmentid == x
        ).delete()
        db.query(model.Assignment).filter(model.Assignment.assignmentid == x).delete()

    db.commit()
    return 0


def getquestionbyassignmentid(db: Session, assignmentid: schemas.Assignmentid):
    #  db.query(model.Question,model.Test).join(model.AssignmentQuestion).filter(model.AssignmentQuestion.assignmentid ==  assignmentid.assignmentid).all()

    return (
        db.query(model.Question)
        .join(model.AssignmentQuestion)
        .filter(model.AssignmentQuestion.assignmentid == assignmentid.assignmentid)
        .all()
    )


def update_assignment(db: Session, assignmentquestion: schemas.Assignmentwithnoquesid):

    assignmentquestion.visibleat = assignmentquestion.visibleat.replace(
        "T", " "
    ).replace(":00", "")
    assignmentquestion.avaliableat = assignmentquestion.avaliableat.replace(
        "T", " "
    ).replace(":00", "")
    assignmentquestion.disableat = assignmentquestion.disableat.replace(
        "T", " "
    ).replace(":00", "")
    assignmentquestion.invisibleat = assignmentquestion.invisibleat.replace(
        "T", " "
    ).replace(":00", "")

    db.query(model.Assignment).filter(
        model.Assignment.assignmentid == assignmentquestion.assignmentid
    ).update({"visibleat": (assignmentquestion.visibleat)})
    db.query(model.Assignment).filter(
        model.Assignment.assignmentid == assignmentquestion.assignmentid
    ).update({"avaliableat": (assignmentquestion.avaliableat)})
    db.query(model.Assignment).filter(
        model.Assignment.assignmentid == assignmentquestion.assignmentid
    ).update({"disableat": (assignmentquestion.disableat)})
    db.query(model.Assignment).filter(
        model.Assignment.assignmentid == assignmentquestion.assignmentid
    ).update({"invisibleat": (assignmentquestion.invisibleat)})
    db.query(model.Assignment).filter(
        model.Assignment.assignmentid == assignmentquestion.assignmentid
    ).update({"assignmentname": (assignmentquestion.assignmentname)})
    db.query(model.Assignment).filter(
        model.Assignment.assignmentid == assignmentquestion.assignmentid
    ).update({"assignmentdescription": (assignmentquestion.assignmentdescription)})
    db.query(model.Assignment).filter(
        model.Assignment.assignmentid == assignmentquestion.assignmentid
    ).update({"maxpossiblescore": (assignmentquestion.maxpossiblescore)})
    db.commit()
    return 0


def update_assignmentquestion(
    db: Session, assignmentquestion: schemas.UpdateAssignmentQuestion
):

    db.query(model.AssignmentQuestion).filter(
        model.AssignmentQuestion.assignmentid == assignmentquestion.assignmentid
    ).delete()
    for x in assignmentquestion.questionid:
        db_test = model.AssignmentQuestion(
            assignmentid=assignmentquestion.assignmentid, questionid=x
        )
        db.add(db_test)
        db.commit()

    db.commit()
    return 0


def get_questionbyassignmentid(db: Session, assignmentid: int):

    return (
        db.query(model.Question, model.Test)
        .join(model.AssignmentQuestion)
        .join(model.Test)
        .filter(model.AssignmentQuestion.assignmentid == assignmentid)
        .all()
    )
