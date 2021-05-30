from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from sqlalchemy import BigInteger,DateTime
from .database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)

#     items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")







class Test(Base):
    __tablename__ = "tests"
    testid = Column(Integer, primary_key=True, index=True)
    testsolution = Column(String, index=True,nullable=False)
    testcases= Column(String, index=True,nullable=False)
    exampletestcases= Column(String, index=True,nullable=False)
    testlanquage= Column(String, index=True,nullable=False)
    testframework= Column(String, index=True,nullable=False)
    question_id = Column(Integer,ForeignKey("question.questionid"),nullable=False)
    question = relationship("Question", back_populates="tests")



class Question(Base):
    __tablename__ = "question"
    questionid = Column(Integer, primary_key=True, index=True)
    questiontopic = Column(String, index=True,nullable=False)
    questiondescription = Column(String, index=True,nullable=False)
    questiondifficulty = Column(String, index=True,nullable=False)
    questioninit = Column(String, index=True,nullable=False)
    tests = relationship("Test", back_populates="question",)
    tag = relationship("QuestionTagForm", back_populates="question")
    assignment = relationship("AssignmentQuestion", back_populates="question")
class Tag(Base):
    __tablename__ = "tag"
    tagid = Column(Integer, primary_key=True, index=True)
    tagname = Column(String, index=True,nullable=False)
    question = relationship("QuestionTagForm", back_populates="tag")
    





class QuestionTagForm(Base):
    __tablename__ = 'questiontag'
    questionid = Column(Integer, ForeignKey('question.questionid'), primary_key=True)
    tagid = Column(Integer, ForeignKey('tag.tagid'), primary_key=True)

    question = relationship("Question", back_populates="tag")
    tag = relationship("Tag", back_populates="question")



class Assignment(Base):
    __tablename__ = 'assignment'
    assignmentid = Column(Integer, primary_key=True, index=True)
    assignmentname = Column(String, index=True,nullable=False)
    assignmentdescription = Column(String, index=True,nullable=False)
    maxpossiblescore = Column(Integer, index=True,nullable=False)
    visibleat = Column(DateTime, index=True,nullable=False)
    avaliableat = Column(DateTime, index=True,nullable=False)
    disableat = Column(DateTime, index=True,nullable=False)
    invisibleat = Column(DateTime, index=True,nullable=False) 
    question = relationship("AssignmentQuestion", back_populates="assignment")           
    
class Exam(Base):
    __tablename__ = 'exam'
    examid = Column(Integer, primary_key=True, index=True)
    examname = Column(String, index=True,nullable=False)
    examdescription = Column(String, index=True,nullable=False)
    maxpossiblescore = Column(Integer, index=True,nullable=False)
    visibleat = Column(DateTime, index=True,nullable=False)
    avaliableat = Column(DateTime, index=True,nullable=False)
    disableat = Column(DateTime, index=True,nullable=False)
    invisibleat = Column(DateTime, index=True,nullable=False)            
    
       
class AssignmentQuestion(Base):
    __tablename__ = 'assigmentquestion'

    questionid = Column(Integer, ForeignKey('question.questionid'), primary_key=True)
    assignmentid = Column(Integer, ForeignKey('assignment.assignmentid'), primary_key=True)
   
    assignment = relationship("Assignment", back_populates="question")
    question = relationship("Question", back_populates="assignment")

# class ExamQuestionForm(Base):
#     __tablename__ = 'examquestion'
#     questionid = Column(Integer, ForeignKey('question.questionid'), primary_key=True)
#     tagid = Column(Integer, ForeignKey('tag.tagid'), primary_key=True)

#     question = relationship("Question", back_populates="tag")
#     tag = relationship("Tag", back_populates="question")
       