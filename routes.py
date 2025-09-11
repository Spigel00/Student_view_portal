from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import timedelta
from typing import Optional, List

from models import get_db, Student, Mark, Teacher
from schemas import TeacherLogin, TeacherCreate, TokenResponse, SemesterMarks, Mark as MarkSchema
from auth import authenticate_teacher, create_teacher, create_access_token, get_current_teacher, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Authentication Routes
@router.post("/api/login", response_model=TokenResponse)
async def login(login_data: TeacherLogin, db: Session = Depends(get_db)):
    teacher = authenticate_teacher(db, login_data.username, login_data.password)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": teacher.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/api/signup", response_model=TokenResponse)
async def signup(signup_data: TeacherCreate, db: Session = Depends(get_db)):
    teacher = create_teacher(db, signup_data.username, signup_data.password, signup_data.name)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": teacher.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Web Routes
@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/login")
async def web_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    teacher = authenticate_teacher(db, username, password)
    if not teacher:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": teacher.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.post("/signup")
async def web_signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    teacher = create_teacher(db, username, password, name)
    if not teacher:
        return templates.TemplateResponse(
            "signup.html", 
            {"request": request, "error": "Username already exists. Please choose a different username."}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": teacher.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # In a real app, you'd validate the token from cookies here
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

# Student API Routes
@router.get("/api/student/{identifier}")
async def get_student(
    identifier: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    # Search by reg_no, umis_id, or emis_id
    student = db.query(Student).filter(
        or_(
            Student.reg_no == identifier,
            Student.umis_id == identifier,
            Student.emis_id == identifier
        )
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student

@router.get("/api/student/{identifier}/marks")
async def get_student_marks(
    identifier: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    # First find the student
    student = db.query(Student).filter(
        or_(
            Student.reg_no == identifier,
            Student.umis_id == identifier,
            Student.emis_id == identifier
        )
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all marks for the student
    marks = db.query(Mark).filter(Mark.student_id == student.reg_no).all()
    
    # Group marks by semester and calculate totals
    semester_marks = {}
    for mark in marks:
        if mark.semester not in semester_marks:
            semester_marks[mark.semester] = []
        
        mark_data = MarkSchema(
            id=mark.id,
            semester=mark.semester,
            subject_code=mark.subject_code,
            subject_name=mark.subject_name,
            internal_1=mark.internal_1,
            internal_2=mark.internal_2,
            student_id=mark.student_id,
            best_of_two=mark.best_of_two
        )
        semester_marks[mark.semester].append(mark_data)
    
    # Calculate totals for each semester
    result = []
    for semester, subjects in semester_marks.items():
        total_marks = sum(subject.best_of_two for subject in subjects)
        max_marks = len(subjects) * 50  # Assuming max 50 marks per subject
        percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
        cgpa_cutoff = percentage / 9.5  # Simple CGPA calculation
        
        semester_data = SemesterMarks(
            semester=semester,
            subjects=subjects,
            total_marks=total_marks,
            percentage=percentage,
            cgpa_cutoff=cgpa_cutoff
        )
        result.append(semester_data)
    
    return sorted(result, key=lambda x: x.semester)

# Web Routes for Student Search
@router.get("/student/{identifier}", response_class=HTMLResponse)
async def student_details_page(
    request: Request,
    identifier: str,
    db: Session = Depends(get_db)
):
    try:
        # Find student
        student = db.query(Student).filter(
            or_(
                Student.reg_no == identifier,
                Student.umis_id == identifier,
                Student.emis_id == identifier
            )
        ).first()
        
        if not student:
            return templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "error": "Student not found"}
            )
        
        # Get marks
        marks = db.query(Mark).filter(Mark.student_id == student.reg_no).all()
        
        # Group by semester
        semester_marks = {}
        for mark in marks:
            if mark.semester not in semester_marks:
                semester_marks[mark.semester] = []
            semester_marks[mark.semester].append(mark)
        
        # Calculate semester totals
        semester_data = []
        for semester in sorted(semester_marks.keys()):
            subjects = semester_marks[semester]
            total_marks = sum(subject.best_of_two for subject in subjects)
            max_marks = len(subjects) * 50
            percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
            cgpa_cutoff = percentage / 9.5
            
            semester_data.append({
                'semester': semester,
                'subjects': subjects,
                'total_marks': total_marks,
                'percentage': round(percentage, 2),
                'cgpa_cutoff': round(cgpa_cutoff, 2)
            })
        
        return templates.TemplateResponse(
            "student_details.html",
            {
                "request": request,
                "student": student,
                "semester_data": semester_data
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "error": f"An error occurred: {str(e)}"}
        )

@router.post("/search")
async def search_student(
    request: Request,
    student_id: str = Form(...),
    db: Session = Depends(get_db)
):
    if not student_id.strip():
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "error": "Please enter a student ID"}
        )
    
    return RedirectResponse(
        url=f"/student/{student_id.strip()}",
        status_code=status.HTTP_302_FOUND
    )
