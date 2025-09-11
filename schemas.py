from pydantic import BaseModel
from typing import List, Optional

class TeacherLogin(BaseModel):
    username: str
    password: str

class TeacherCreate(BaseModel):
    username: str
    password: str
    name: str

class StudentBase(BaseModel):
    reg_no: str
    umis_id: str
    emis_id: str
    name: str
    aadhar_number: str
    phone_number: str
    address: str

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    class Config:
        from_attributes = True

class MarkBase(BaseModel):
    semester: int
    subject_code: str
    subject_name: str
    internal_1: float
    internal_2: float

class MarkCreate(MarkBase):
    student_id: str

class Mark(MarkBase):
    id: int
    student_id: str
    best_of_two: float
    
    class Config:
        from_attributes = True

class StudentWithMarks(Student):
    marks: List[Mark] = []

class SemesterMarks(BaseModel):
    semester: int
    subjects: List[Mark]
    total_marks: float
    percentage: float
    cgpa_cutoff: float

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class TeacherInfo(BaseModel):
    id: int
    username: str
    name: str
