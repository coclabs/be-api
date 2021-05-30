import json
import httpx

from typing import List

from db import codingcrud,schemas,database,model
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

model.Base.metadata.create_all(bind=database.engine)
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)


# @app.get("/users/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items

    
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)







# @app.post("/questions/{question_id}/tests/", response_model=schemas.TestForm)
# def create_test_for_question(
#     question_id: int, test: schemas.TestForm, db: Session = Depends(get_db)
# ):
#     return crud.create_question_test(db=db, test=test, question_id=question_id)



# @app.post("/createquestion/",response_model=schemas.QuestionResponse)
# def create_question(question: schemas.QuestionForm, db: Session = Depends(get_db)):

#     return crud.create_question(db=db, question=question)

# @app.get("/test/{question_id}", response_model=List[schemas.TestForm])
# def read_test_in_question(question_id:int, db: Session = Depends(get_db)):
#     test = crud.get_tests(db, question_id=question_id)
#     return test

    
# @app.post("/createtag/",response_model=schemas.TagForm)
# def create_tag(tag: schemas.TagForm, db: Session = Depends(get_db)):

#     return crud.create_tag(db=db, tag=tag)

# @app.post("/createquestiontag/",response_model=schemas.QuestionTagResponse)
# def create_tag(questiontag: schemas.QuestionTagForm, db: Session = Depends(get_db)):

#     return crud.create_questiontag(db=db, questiontag=questiontag)


@app.post("/createquestionwithtest/")
def create_questionwithtest(questiontest:schemas.QuestionTestForm,db: Session = Depends(get_db)):
    question=schemas.QuestionForm(questioninit=questiontest.questioninit,questiontopic=questiontest.questiontopic,questiondescription=questiontest.questiondescription,questiondifficulty=questiontest.questiondifficulty)
    test=schemas.TestForm(testsolution=questiontest.testsolution,testcases=questiontest.testcases,exampletestcases=questiontest.exampletestcases,testframework=questiontest.testframework,testlanquage=questiontest.testlanquage)
  
  
    questiona =codingcrud.create_question(db=db, question=question)
    testa=codingcrud.create_question_test(db=db,test=test,question_id=questiona.questionid)
    
    return {'question':questiona,'asd':'asd'}


@app.get("/showtenquestions/{number}", response_model=List[schemas.QuestionResponse])
def read_showtenquestion(number:int, db: Session = Depends(get_db)):
    questions = codingcrud.get_questions(db, number)
    return questions
    

@app.get("/questionpage/")
def read_questionpage(db: Session = Depends(get_db)):
    questionpage = codingcrud.get_questionpage(db)
    return questionpage
    
@app.post("/showtenquestionspost/", response_model=List[schemas.QuestionResponse])
def read_showtenquestionpost(page:schemas.page, db: Session = Depends(get_db)):
    questions = codingcrud.get_questions(db, page=page.page)
    return questions



# @app.post("/createxam/",response_model=schemas.ExamForm)
# def create_exam(exam:schemas.ExamForm, db: Session = Depends(get_db)):
#     crud.create_exam(db=db,exam=exam)



    
#     return exam     
   
@app.post("/createassignmentquestion/")
def create_assignmentquestion(assignmentquestion: schemas.AssignmentQuestionForm, db: Session = Depends(get_db)):
    createdassignment = codingcrud.create_assignment(db=db,assignment=assignmentquestion)
     
    return codingcrud.create_assignmentquestion(db=db, assigmentquestion=assignmentquestion, assignmentid=createdassignment.assignmentid)
    

@app.get("/showallquestions/", response_model=List[schemas.QuestionResponse])
def read_showallquestion( db: Session = Depends(get_db)):
    questions = codingcrud.get_allquestions(db)
    return questions


@app.get("/assignmentpage/")
def read_assignmentpage(db: Session = Depends(get_db)):
    assignmentpage = codingcrud.get_assignmentpage(db)
    return assignmentpage
    
@app.get("/showtenassignment/{page}")
def read_showtenassignment(page:int, db: Session = Depends(get_db)):
    assignments = codingcrud.get_assignments(db, page=page)
    
    return assignments

@app.post("/showtenassignmentpost/")
def read_showtenquestionpost(page:schemas.page, db: Session = Depends(get_db)):
    assignments = codingcrud.get_assignments(db, page=page.page)
    return assignments 

@app.post("/deleteonequestion/")
def delete_onequestion(questionid:schemas.Questionid, db: Session = Depends(get_db)):
 
    return  codingcrud.delete_onequestion(db,questionid=questionid.questionid)

@app.post("/updatequestion/")
def update_question(questiontest:schemas.QuestionTestForm, db: Session = Depends(get_db)):
 
    return  codingcrud.update_question(db,questiontest=questiontest)

@app.post("/multipledeletequestion/")
def delete_multiplequestion(questionid:schemas.ArrayQuestionid, db: Session = Depends(get_db)):
 
    return  codingcrud.delete_multiplequestion(db,questionid=questionid)

@app.post("/deleteoneassignment/")
def delete_onequestion(assignmentid:schemas.Assignmentid, db: Session = Depends(get_db)):
 
    return  codingcrud.delete_oneassignment(db,assignmentid=assignmentid.assignmentid)


@app.post("/multipledeleteassignment/")
def delete_multipleassignment(assignmentid:schemas.ArrayAssignmentid, db: Session = Depends(get_db)):
 
    return  codingcrud.delete_multipleassignment(db,assignmentid=assignmentid)


@app.post("/findquestionbyassignmentid/")
def getquestionbyassignmentid(assignmentid:schemas.Assignmentid, db: Session = Depends(get_db)):
    
 
    
    return   codingcrud.getquestionbyassignmentid(db,assignmentid=assignmentid)


@app.post("/updateassignment/")
def update_question(assignmentquestion: schemas.Assignmentwithnoquesid,db: Session = Depends(get_db)):
 
    return  codingcrud.update_assignment(db,assignmentquestion=assignmentquestion)

@app.post("/updateassignmentquestion/")
def update_assignmentquestion(assignmentquestion: schemas.UpdateAssignmentQuestion,db: Session = Depends(get_db)):
 
    return  codingcrud.update_assignmentquestion(db,assignmentquestion=assignmentquestion)

@app.get("/getquestionbyquestionid/{questionid}",response_model=schemas.QuestionResponse)
def read_showtenassignment(questionid:int, db: Session = Depends(get_db)):
    question = codingcrud.get_questionbyquestionid(db,questionid=questionid)
    
    return question


@app.get("/getquestionbyassignmentid/{assignmentid}")
def read_showtenassignment(assignmentid:int, db: Session = Depends(get_db)):
    
    return codingcrud.get_questionbyassignmentid(db,assignmentid=assignmentid)
    
@app.post("/gogo")
def read_showtenassignment(code: schemas.code,context:schemas.context ,db: Session = Depends(get_db)):

    
    code=schemas.code(version="3.9.2",language="python",value=code.value)
    context=schemas.context(test=context.test,scoring="any_pass",mode="submit")
    encoded_code = jsonable_encoder(code)
    encoded_context = jsonable_encoder(context)
    r = httpx.post('https://xc.pdm-dev.me/api/codes', json={'code': encoded_code,'context':encoded_context})
    return r.text
    
