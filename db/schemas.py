from typing import List, Optional
import array as arr
from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True










class TestForm(BaseModel):
    
    
    testsolution:str
    testcases:str
    exampletestcases:str
    testlanquage:str
    testframework:str

    class Config:
        orm_mode = True



















class QuestionForm(BaseModel):
   
    questiontopic: str
    questiondescription: str
    questiondifficulty: str
    questioninit:str
    class Config:
        orm_mode = True

class QuestionResponse(QuestionForm):
    questionid:int   
    questiontopic: str
    questiondescription: str
    questiondifficulty: str
    questioninit:str
    tests: List[TestForm] = []

    class Config:
        orm_mode = True




class TagForm(BaseModel):
    
    
    tagid:int
    tagname:str

    class Config:
        orm_mode = True


class QuestionTagForm(BaseModel):
    
    
    questionid:int
    tagid:int
    class Config:
        orm_mode = True

class QuestionTagResponse(QuestionTagForm):
    
    
    question:QuestionForm
    tag:TagForm
    class Config:
        orm_mode = True
   
class QuestionTestForm(BaseModel):
    
    questionid:int
    questiontopic: str
    questiondescription: str
    questiondifficulty: str 
    testsolution:str
    testcases:str
    questioninit:str
    exampletestcases:str
    testlanquage:str
    testframework:str
    
class page(BaseModel):
    page:int

class ExamForm(BaseModel):
    
    

    examname: str
    examdescription: str 
  
    maxpossiblescore:int
    visibleat:str
    avaliableat:str
    disableat:str
    invisibleat:str
    class Config:
        orm_mode = True 

class AssignmentForm(BaseModel):
    
    

    assignmentname: str
    assignmentdescription: str 
    maxpossiblescore:int
    visibleat:str
    avaliableat:str
    disableat:str
    invisibleat:str   
    assignmentid:int
    class Config:
        orm_mode = True       

class AssignmentQuestionForm(BaseModel):
    
    
    assignmentname: str
    assignmentdescription: str 
    maxpossiblescore:int
    visibleat:str
    avaliableat:str
    disableat:str
    invisibleat:str
    questionid:List[int]
    
    class Config:
        orm_mode = True        

class Questionid(BaseModel):
   questionid:int


class TeacherCreate(BaseModel):
    fistname:str
    lastname:str
    password:str
    username:str



class CourseCreate(BaseModel):
    coursename:str
    coursedescription:str
    courseobjective:str
   