from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException
from db import crud,schemas,database,model

from sqlalchemy.orm import Session


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
  
  
    questiona =crud.create_question(db=db, question=question)
    testa=crud.create_question_test(db=db,test=test,question_id=questiona.questionid)
    
    return {'question':questiona,'asd':'asd'}


@app.get("/showtenquestions/{number}", response_model=List[schemas.QuestionResponse])
def read_showtenquestion(number:int, db: Session = Depends(get_db)):
    questions = crud.get_questions(db, number)
    return questions
    

@app.get("/questionpage/")
def read_questionpage(db: Session = Depends(get_db)):
    questionpage = crud.get_questionpage(db)
    return questionpage
    
@app.post("/showtenquestionspost/", response_model=List[schemas.QuestionResponse])
def read_showtenquestionpost(page:schemas.page, db: Session = Depends(get_db)):
    questions = crud.get_questions(db, page=page.page)
    return questions



# @app.post("/createxam/",response_model=schemas.ExamForm)
# def create_exam(exam:schemas.ExamForm, db: Session = Depends(get_db)):
#     crud.create_exam(db=db,exam=exam)



    
#     return exam     
   
@app.post("/createassignmentquestion/")
def create_assignmentquestion(assignmentquestion: schemas.AssignmentQuestionForm, db: Session = Depends(get_db)):
    createdassignment = crud.create_assignment(db=db,assignment=assignmentquestion)
    
    return crud.create_assignmentquestion(db=db, assigmentquestion=assignmentquestion, assignmentid=createdassignment.assignmentid)
    

@app.get("/showallquestions/", response_model=List[schemas.QuestionResponse])
def read_showallquestion( db: Session = Depends(get_db)):
    questions = crud.get_allquestions(db)
    return questions


@app.get("/assignmentpage/")
def read_assignmentpage(db: Session = Depends(get_db)):
    assignmentpage = crud.get_assignmentpage(db)
    return assignmentpage
    
@app.get("/showtenassignment/{page}")
def read_showtenassignment(page:int, db: Session = Depends(get_db)):
    assignments = crud.get_assignments(db, page=page)
    return assignments

@app.post("/showtenassignmentpost/", )
def read_showtenquestionpost(page:schemas.page, db: Session = Depends(get_db)):
    assignments = crud.get_assignments(db, page=page.page)
    return assignments 

@app.post("/deleteonequestion/")
def delete_onequestion(questionid:schemas.Questionid, db: Session = Depends(get_db)):
 
    return  crud.delete_onequestion(db,questionid=questionid.questionid)

@app.post("/updatequestion/")
def update_question(questiontest:schemas.QuestionTestForm, db: Session = Depends(get_db)):
 
    return  crud.update_question(db,questiontest=questiontest)

#endofrelease1 nextis api classroom

@app.post("/createteacher")
def create_teacher(teacher:schemas.TeacherCreate, db: Session = Depends(get_db)):
 
    return  classroomcrud.create_teacher(db,teacher=teacher)

@app.post("/createcourseteacher")
def create_course_teacher(course:schemas.CourseCreate,teacherid:int db: Session = Depends(get_db)):
      #teacherid need to change for use token to find teacherid
    course = classroomcrud.create_course(db,course=course)

    return   classroomcrud.create_course_teacher(courseid=course.courseid,teacherid=teacherid) 


# @app.post("/token")
# def login_for_access_token(user: userschemas.UserCreate):
      
#     user = authenticate_user(db, user.email, user.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#     data={"sub": user.email}, expires_delta=access_token_expires)
#     return {'accesstoken':access_token}  
   
# @app.post("/")
# async def get_current_user(token: str ):
#     credentials_exception = HTTPException(
#         status_code="status.HTTP_401_UNAUTHORIZED",
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
       

        
#     except JWTError:
#         raise credentials_exception
#     user = get_user(db, username)
#     if user is None:
#         raise credentials_exception
#     return user
