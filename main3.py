from calendar import c
import json
from fastapi.param_functions import Body
import httpx
from datetime import datetime, timedelta
from typing import List
from typing import Optional

from pydantic.networks import HttpUrl
from db import codingcrud, schemas, database, model, classroomcrud, authenticatecrud
from sqlalchemy.orm import Session, defaultload
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from collections import defaultdict
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status


model.Base.metadata.create_all(bind=database.engine)
app = FastAPI()
allstudent = {}
allteacher = {}
html1 = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("wss://api.pdm-dev.me/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

html2 = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`wss://api.pdm-dev.me/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):

        self.active_connections: dict = defaultdict(dict)

    async def connect(self, websocket: WebSocket, courseid: int):
        await websocket.accept()
        if (
            self.active_connections[courseid] == {}
            or len(self.active_connections[courseid]) == 0
        ):
            self.active_connections[courseid] = []
        self.active_connections[courseid].append(websocket)

    def disconnect(self, websocket: WebSocket, courseid: int):
        self.active_connections[courseid].remove(websocket)

    async def send_personal_message(self, json, websocket: WebSocket):
        await websocket.send_json(json, "text")

    async def broadcast(self, json, courseid: int):
        for connection in self.active_connections[courseid]:
            await connection.send_json(json, "text")


manager = ConnectionManager()


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Optional[str] = Cookie(None),
    token: Optional[str] = Query(None),
):
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.websocket("/ws/{courseid}/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: int,
    role: str,
    courseid: int,
    db: Session = Depends(get_db),
):

    await manager.connect(websocket, courseid)

    teacher = ""
    student = ""

    if role == "Teacher":

        teacher = authenticatecrud.get_teacher_by_id(db, client_id)
        if courseid not in allteacher.keys():
            allteacher[courseid] = []

        # if client_id not in allteacher[courseid]:

        # await manager.broadcast(
        #     {"message": f"{role} {teacher.firstname}  join chat", "id": 3},
        #     courseid,
        # )

        allteacher[courseid].append(client_id)

        listteacher = []
        for teacher in allteacher[courseid]:

            oneteacher = authenticatecrud.get_teacher_by_id(db, teacher)
            listteacher.append(jsonable_encoder(oneteacher))
        await manager.broadcast({"message": listteacher, "id": 1}, courseid)
        if allstudent == {}:
            await manager.broadcast({"message": [], "id": 2}, courseid)
        else:
            if courseid in allstudent.keys():
                liststudent = []
                for student in allstudent[courseid]:

                    onestudent = authenticatecrud.get_student_by_id(db, student)
                    liststudent.append(jsonable_encoder(onestudent))

                await manager.broadcast(
                    {"message": liststudent, "id": 2},
                    courseid,
                )
            else:
                await manager.broadcast({"message": [], "id": 2}, courseid)

    else:
        if allteacher == {}:
            await manager.broadcast({"message": [], "id": 1}, courseid)
        else:
            listteacher = []
            if courseid in allteacher.keys():
                for teacher in allteacher[courseid]:

                    oneteacher = authenticatecrud.get_teacher_by_id(db, teacher)
                    listteacher.append(jsonable_encoder(oneteacher))
                await manager.broadcast(
                    {"message": listteacher, "id": 1},
                    courseid,
                )
            else:
                await manager.broadcast({"message": [], "id": 1}, courseid)

        student = authenticatecrud.get_student_by_id(db, client_id)
        if courseid not in allstudent.keys():
            allstudent[courseid] = []

        allstudent[courseid].append(client_id)
        liststudent = []
        if courseid in allstudent.keys():
            for student in allstudent[courseid]:

                onestudent = authenticatecrud.get_student_by_id(db, student)
                liststudent.append(jsonable_encoder(onestudent))
        await manager.broadcast({"message": liststudent, "id": 2}, courseid)

    try:
        while True:
            data = await websocket.receive_text()
            if role == "Teacher":
                teacher = authenticatecrud.get_teacher_by_id(db, client_id)
                await manager.broadcast(
                    {
                        "message": f"{role} {teacher.firstname} \n says: {data} ",
                        "id": 5,
                    },
                    courseid,
                )
            else:
                student = authenticatecrud.get_student_by_id(db, client_id)
                await manager.broadcast(
                    {
                        "message": f"{role} {student.firstname} \n says: {data} ",
                        "id": 6,
                    },
                    courseid,
                )

            # await manager.send_personal_message(f"You wrote: {data}", websocket)

    except WebSocketDisconnect:

        manager.disconnect(websocket, courseid)

        if role == "Teacher":
            listteacher = []

            allteacher[courseid].remove(client_id)
            for teacher in allteacher[courseid]:

                oneteacher = authenticatecrud.get_teacher_by_id(db, teacher)
                listteacher.append(jsonable_encoder(oneteacher))
            await manager.broadcast({"message": listteacher, "id": 100}, courseid)

        else:
            allstudent[courseid].remove(client_id)
            for student in allstudent[courseid]:
                liststudent = []

                onestudent = authenticatecrud.get_student_by_id(db, student)
                liststudent.append(jsonable_encoder(onestudent))
            await manager.broadcast({"message": liststudent, "id": 200}, courseid)

        #     student = authenticatecrud.get_student_by_id(db, client_id)
        #     await manager.broadcast(
        #         {"message": f"Student {student.firstname} left the chat", "id": 8},
        #         courseid,
        #     )
        # await manager.broadcast(
        #     {"message": f"Student in This room : {liststudent}", "id": 2},
        #     courseid,
        # )


@app.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    item_id: str,
    q: Optional[int] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(
            f"Session cookie or query token value is: {cookie_or_token}"
        )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")


@app.get("/")
async def get():
    return HTMLResponse(html2)


# @app.get("/")
# async def get():
#     return HTMLResponse(html1)


# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(us_code=400, detail="Email already registered")
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
def create_questionwithtest(
    questiontest: schemas.QuestionTestForm, db: Session = Depends(get_db)
):
    question = schemas.QuestionForm(
        questioninit=questiontest.questioninit,
        questiontopic=questiontest.questiontopic,
        questiondescription=questiontest.questiondescription,
        questiondifficulty=questiontest.questiondifficulty,
    )
    test = schemas.TestForm(
        testsolution=questiontest.testsolution,
        testcases=questiontest.testcases,
        exampletestcases=questiontest.exampletestcases,
        testframework=questiontest.testframework,
        testlanquage=questiontest.testlanquage,
    )

    questiona = codingcrud.create_question(db=db, question=question)
    testa = codingcrud.create_question_test(
        db=db, test=test, question_id=questiona.questionid
    )

    return {"question": questiona, "asd": "asd"}


@app.get("/showtenquestions/{number}", response_model=List[schemas.QuestionResponse])
def read_showtenquestion(number: int, db: Session = Depends(get_db)):
    questions = codingcrud.get_questions(db, number)
    return questions


@app.get("/questionpage/")
def read_questionpage(db: Session = Depends(get_db)):
    questionpage = codingcrud.get_questionpage(db)
    return questionpage


@app.post("/showtenquestionspost/", response_model=List[schemas.QuestionResponse])
def read_showtenquestionpost(page: schemas.page, db: Session = Depends(get_db)):
    questions = codingcrud.get_questions(db, page=page.page)
    return questions


# @app.post("/createxam/",response_model=schemas.ExamForm)
# def create_exam(exam:schemas.ExamForm, db: Session = Depends(get_db)):
#     crud.create_exam(db=db,exam=exam)


#     return exam


@app.post("/createassignmentquestion/")
def create_assignmentquestion(
    assignmentquestion: schemas.AssignmentQuestionForm, db: Session = Depends(get_db)
):
    createdassignment = codingcrud.create_assignment(
        db=db, assignment=assignmentquestion
    )

    return codingcrud.create_assignmentquestion(
        db=db,
        assigmentquestion=assignmentquestion,
        assignmentid=createdassignment.assignmentid,
    )


@app.get("/showallquestions/", response_model=List[schemas.QuestionResponse])
def read_showallquestion(db: Session = Depends(get_db)):
    questions = codingcrud.get_allquestions(db)
    return questions


@app.get("/assignmentpage/")
def read_assignmentpage(db: Session = Depends(get_db)):
    assignmentpage = codingcrud.get_assignmentpage(db)
    return assignmentpage


@app.get("/showtenassignment/{page}")
def read_showtenassignment(page: int, db: Session = Depends(get_db)):
    assignments = codingcrud.get_assignments(db, page=page)

    return assignments


@app.post("/showtenassignmentpost/")
def read_showtenquestionpost(page: schemas.page, db: Session = Depends(get_db)):
    assignments = codingcrud.get_assignments(db, page=page.page)
    return assignments


@app.post("/deleteonequestion/")
def delete_onequestion(questionid: schemas.Questionid, db: Session = Depends(get_db)):

    return codingcrud.delete_onequestion(db, questionid=questionid.questionid)


@app.post("/updatequestion/")
def update_question(
    questiontest: schemas.QuestionTestForm, db: Session = Depends(get_db)
):

    return codingcrud.update_question(db, questiontest=questiontest)


@app.post("/multipledeletequestion/")
def delete_multiplequestion(
    questionid: schemas.ArrayQuestionid, db: Session = Depends(get_db)
):

    return codingcrud.delete_multiplequestion(db, questionid=questionid)


@app.post("/deleteoneassignment/")
def delete_onequestion(
    assignmentid: schemas.Assignmentid, db: Session = Depends(get_db)
):

    return codingcrud.delete_oneassignment(db, assignmentid=assignmentid.assignmentid)


@app.post("/multipledeleteassignment/")
def delete_multipleassignment(
    assignmentid: schemas.ArrayAssignmentid, db: Session = Depends(get_db)
):

    return codingcrud.delete_multipleassignment(db, assignmentid=assignmentid)


@app.post("/findquestionbyassignmentid/")
def getquestionbyassignmentid(
    assignmentid: schemas.Assignmentid, db: Session = Depends(get_db)
):

    return codingcrud.getquestionbyassignmentid(db, assignmentid=assignmentid)


@app.post("/updateassignment/")
def update_question(
    assignmentquestion: schemas.Assignmentwithnoquesid, db: Session = Depends(get_db)
):

    return codingcrud.update_assignment(db, assignmentquestion=assignmentquestion)


@app.post("/updateassignmentquestion/")
def update_assignmentquestion(
    assignmentquestion: schemas.UpdateAssignmentQuestion, db: Session = Depends(get_db)
):

    return codingcrud.update_assignmentquestion(
        db, assignmentquestion=assignmentquestion
    )


@app.get(
    "/getquestionbyquestionid/{questionid}", response_model=schemas.QuestionResponse
)
def read_showtenassignment(questionid: int, db: Session = Depends(get_db)):
    question = codingcrud.get_questionbyquestionid(db, questionid=questionid)

    return question


@app.get("/getquestionbyassignmentid/{assignmentid}")
def read_showtenassignment(assignmentid: int, db: Session = Depends(get_db)):

    return codingcrud.get_questionbyassignmentid(db, assignmentid=assignmentid)


@app.post("/gogo")
def read_showtenassignment(
    code: schemas.code, context: schemas.context, db: Session = Depends(get_db)
):

    code = schemas.code(version="3.9.2", language="python", value=code.value)
    context = schemas.context(test=context.test, scoring="any_pass", mode="submit")
    encoded_code = jsonable_encoder(code)
    encoded_context = jsonable_encoder(context)
    r = httpx.post(
        "https://xc.pdm-dev.me/api/codes",
        json={"code": encoded_code, "context": encoded_context},
    )
    return r.text


# classroom part


@app.post("/createteacher")
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):

    return classroomcrud.create_teacher(db, teacher=teacher)


@app.post("/createcourseteacher")
def create_course_teacher(
    course: schemas.CourseTeacherCreate, db: Session = Depends(get_db)
):
    # teacherid need to change for use token to find teacherid
    course2 = classroomcrud.create_course(db, course=course)

    return classroomcrud.create_course_teacher(
        db, courseid=course2.courseid, teacherid=course.teacherid
    )


@app.get("/{teacherid}/getallcourseteacher")
def get_all_course_teacher(teacherid: int, db: Session = Depends(get_db)):

    # teacherid need to change for use token to find teacherid

    return classroomcrud.get_all_course_teacher(db, teacherid)


@app.get("/{studentid}/getallcoursestudent")
def get_all_course_student(studentid: int, db: Session = Depends(get_db)):

    # teacherid need to change for use token to find teacherid

    return classroomcrud.get_all_course_student(db, studentid)


@app.post("/createstudent")
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):

    return classroomcrud.create_student(db, student=student)


# @app.get("/getstudentincourse")
# def create_teacher( db: Session = Depends(get_db)):

#     return


# @app.get("/getteacher")
# def create_teacher(teacher:schemas.TeacherCreate, db: Session = Depends(get_db)):

#     return


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# authenpart

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


@app.post("/createtokenteacher")
def login_for_access_token_teacher(
    user: schemas.UserCreate, db: Session = Depends(get_db)
):

    teacher = authenticatecrud.authenticate_teacher(db, user.username, user.password)
    if not teacher:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "teacher": teacher,
        "accesstoken": access_token,
        "user": authenticatecrud.get_teacher_by_username(db, user.username),
    }


@app.post("/createtokenstudent")
def login_for_access_token_student(
    user: schemas.UserCreate, db: Session = Depends(get_db)
):

    student = authenticatecrud.authenticate_student(db, user.username, user.password)
    if not student:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "student": student,
        "accesstoken": access_token,
        "user": authenticatecrud.get_student_by_username(db, user.username),
    }


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authen_teacher(token: schemas.Token, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    teacher = authenticatecrud.get_teacher_by_username(db, username)
    if teacher is None:
        raise credentials_exception
    return teacher


def authen_student(token: schemas.Token, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    student = authenticatecrud.get_student_by_username(db, username)
    if student is None:
        raise credentials_exception
    return student


@app.post("/getteacherbytoken")
def authen_teacher2(token: schemas.Token, db: Session = Depends(get_db)):

    teacher = authen_teacher(token, db)

    return teacher


@app.post("/getstudentbytoken")
def authen_student2(token: schemas.Token, db: Session = Depends(get_db)):

    student = authen_student(token, db)

    return student


@app.post("/testroute")
def test_route(bl: int = None, ads: int = Body(None), db: Session = Depends(get_db)):

    return bl


@app.post("/studentassignment")
def write_studentassignment(
    assignmentid: int = Body(...),
    totalscore: int = Body(...),
    studentid: int = Body(...),
    totalcorrect: int = Body(...),
    totalnotcorrect: int = Body(...),
    db: Session = Depends(get_db),
):

    return classroomcrud.create_student_assignment(
        db,
        assignmentid,
        totalscore,
        studentid,
        totalcorrect,
        totalnotcorrect,
    )


@app.get("/{studentid}/studentassignment")
def get_studentassignment(
    studentid: int,
    db: Session = Depends(get_db),
):

    return classroomcrud.read_student_assignment(db, studentid)


@app.get("/{studentid}/studentassignmentquestion")
def read_studentassignment_question(
    studentid: int,
    studentassignmentid: int,
    db: Session = Depends(get_db),
):

    return classroomcrud.read_student_assignment_question_by_id_studentassignmentid(
        db, studentid, studentassignmentid
    )


@app.get("/{studentid}/attempt/")
def get_studentassignment(
    studentid: int,
    assignmentid: int,
    db: Session = Depends(get_db),
):

    return classroomcrud.count_attempt(db, studentid, assignmentid)


@app.post("/studentassignmentquestion")
def write_studentassignmentquestion(
    questionnumber: int = Body(...),
    studentscore: int = Body(...),
    testresult: str = Body(...),
    studentanswer: str = Body(...),
    totalcorrect: int = Body(...),
    totalnotcorrect: int = Body(...),
    studentassignmentid: int = Body(...),
    db: Session = Depends(get_db),
):
    classroomcrud.create_student_assignmentquestion(
        db,
        studentassignmentid,
        questionnumber,
        studentscore,
        testresult,
        studentanswer,
        totalcorrect,
        totalnotcorrect,
    )

    return 0


@app.put("/studentassignment")
def update_studentassignment(
    studentassignmentid: int = Body(...),
    totalscore: int = Body(...),
    totalcorrect: int = Body(...),
    totalnotcorrect: int = Body(...),
    db: Session = Depends(get_db),
):
    classroomcrud.update_student_assignment(
        db, studentassignmentid, totalscore, totalcorrect, totalnotcorrect
    )

    return 0


@app.get("/{courseid}/studentnotinthiscourse")
def read_studentnotinthiscourse(
    courseid: int,
    db: Session = Depends(get_db),
):

  allstu= classroomcrud.read_students_notin_this_course(db, courseid)
  studentincourse=classroomcrud.read_all_student_in_course(db,courseid)
  result=[]
  for stu in allstu:
      if(stu not in studentincourse): 
          result.append(stu)
  
  return result


@app.get("/{courseid}/course")
def read_course(
    courseid: int,
    db: Session = Depends(get_db),
):

    return classroomcrud.read_course(db, courseid)


@app.post("/studentenrollcourse")
def write_student_enroll_course(
    studentid: int = Body(...),
    courseid: int = Body(...),
    db: Session = Depends(get_db),
):

    return classroomcrud.create_student_enroll_course(db, studentid, courseid)


@app.post("/create_course_assignment")
def write_course_assignment(
    assignmentid: int = Body(...),
    courseid: int = Body(...),
    db: Session = Depends(get_db),
):

    return classroomcrud.create_course_assignment(db, assignmentid, courseid)


@app.get("/{courseid}/read_course_assignment")
def read_course_assignment(
    courseid: int,
    db: Session = Depends(get_db),
):

    return classroomcrud.read_course_assignment(db, courseid)


@app.get("/{courseid}/read_course_assignment_status")
def read_course_assignment_status(
    page: int,
    courseid: int,
    db: Session = Depends(get_db),
):

    assignment = codingcrud.get_assignments_assignmentid(db, page)

    result = []

    for ass in jsonable_encoder(assignment):

        if (
            classroomcrud.read_course_assignment_status(
                db, ass["assignmentid"], courseid
            )
            is not None
        ):
            result.append(True)
        else:
            result.append(False)

    return result


@app.post("/toggle_course_assignment")
def read_course_assignment(
    courseid: int = Body(...),
    assignmentid: int = Body(...),
    db: Session = Depends(get_db),
):

    if classroomcrud.read_course_assignment_by_id(db, courseid, assignmentid) is None:
        return classroomcrud.create_course_assignment(db, assignmentid, courseid)

    else:
        return classroomcrud.toggle_course_assignment(db, courseid, assignmentid)


@app.post("/write_assignment_record")
def write_assignment_record(
    assignmentid: int = Body(...),
    studentscore: int = Body(...),
    db: Session = Depends(get_db),
):
    record = classroomcrud.read_student_assignment_record_by_assignmentid(
        db, assignmentid
    )

    if record is None:
        max = studentscore
        min = studentscore
        allscore = studentscore
        attempt = 1

        return classroomcrud.create_studentassignmentrecord(
            db, assignmentid, max, min, allscore, attempt
        )
    else:
        if studentscore >= record.max:
            max = studentscore
        else:
            max = record.max
        if studentscore <= record.min:
            min = studentscore
        else:
            min = record.min

        allscore = record.allscore + studentscore
        attempt = record.attempt + 1

        classroomcrud.update_student_assignment_record(
            db, assignmentid, max, min, allscore, attempt
        )

        return record.studentassignmentrecordid


#  assignmentid = Column(
#         Integer, ForeignKey("assignment.assignmentid"), primary_key=True
#     )
#     max = Column(Integer, index=True, nullable=False)
#     min = Column(Integer, index=True, nullable=False)
#     allscore = Column(Integer, index=True, nullable=False)
#     attempt = Column(Integer, index=True, nullable=False)
#     firstdonetime = Column(DateTime, index=True, nullable=False)
#     lastdonetime = Column(DateTime, index=True, nullable=False)


@app.get("/read_all_student_assignment_record")
def read_all_student_assignment_record(db: Session = Depends(get_db)):

    return classroomcrud.read_all_student_assignment_record(db)


@app.get("/{courseid}/read_student_in_course")
def read_all_student_in_course(courseid: int, db: Session = Depends(get_db)):

    return classroomcrud.read_all_student_in_course(db, courseid)


@app.get("/read_record_student")
def read_all_student_in_course(assignmentid: int, db: Session = Depends(get_db)):

    result = []
    studentid = classroomcrud.read_record_student(db, assignmentid)

    for a in studentid:
        if a not in result:

            result.append(a.studentid)
    my_list = list(set(result))

    student = []

    for i in my_list:
        std = classroomcrud.read_student(db, i)

        student.append(std)

    return student
