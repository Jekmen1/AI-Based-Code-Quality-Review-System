from fastapi import FastAPI, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

SQLALCHEMY_DATABASE_URL = 'sqlite:///./Students.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Students(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    point = Column(Integer)

Base.metadata.create_all(bind=engine)

class StudentBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    point: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    point: Optional[int] = None

class Student(StudentBase):
    id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/students/", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Students(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=List[Student])
def get_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Students).offset(skip).limit(limit).all()

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Students).filter(Students.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Students).filter(Students.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if student_update.email is not None:
        student.email = student_update.email
    if student_update.first_name is not None:
        student.first_name = student_update.first_name
    if student_update.last_name is not None:
        student.last_name = student_update.last_name
    if student_update.point is not None:
        student.point = student_update.point
    db.commit()
    db.refresh(student)
    return student

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Students).filter(Students.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"detail": "Student deleted successfully"}


