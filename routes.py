from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import timedelta
from typing import Optional, List

from models import get_db, Student, Mark, Teacher
from schemas import TeacherLogin, TeacherCreate, TokenResponse, SemesterMarks, Mark as MarkSchema, StudentCreateWithMarks, Student as StudentSchema, MarkCreate
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

# New Student Management Routes
@router.get("/enter-student", response_class=HTMLResponse)
async def enter_student_page(request: Request):
    return templates.TemplateResponse("enter_student.html", {"request": request})

@router.get("/view-student", response_class=HTMLResponse)
async def view_student_page(request: Request):
    return templates.TemplateResponse("view_student.html", {"request": request})

@router.post("/enter-student")
async def create_student_web(request: Request, db: Session = Depends(get_db)):
    # Get form data
    form = await request.form()
    
    try:
        # Extract basic student info
        student_data = {
            'reg_no': form.get('reg_no'),
            'umis_id': form.get('umis_id'),
            'emis_id': form.get('emis_id'),
            'name': form.get('name'),
            'aadhar_number': form.get('aadhar_number'),
            'phone_number': form.get('phone_number'),
            'address': form.get('address'),
            'admission_year': form.get('admission_year')
        }
        
        # Validate admission year
        try:
            admission_year = int(student_data['admission_year'])
            if admission_year < 2020 or admission_year > 2030:
                return templates.TemplateResponse(
                    "enter_student.html",
                    {"request": request, "error": "Admission year must be between 2020 and 2030"}
                )
        except (ValueError, TypeError):
            return templates.TemplateResponse(
                "enter_student.html",
                {"request": request, "error": "Valid admission year is required"}
            )
        
        # Check if student already exists
        existing_student = db.query(Student).filter(
            or_(
                Student.reg_no == student_data['reg_no'],
                Student.umis_id == student_data['umis_id'],
                Student.emis_id == student_data['emis_id']
            )
        ).first()
        
        if existing_student:
            return templates.TemplateResponse(
                "enter_student.html",
                {"request": request, "error": "Student with this Registration Number, UMIS ID, or EMIS ID already exists"}
            )
        
        # Create new student
        new_student = Student(**student_data)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        
        # Get available semesters for this student
        from models import get_academic_year_info
        academic_info = get_academic_year_info(admission_year)
        available_semesters = academic_info['available_semesters']
        
        # Extract and save marks only for available semesters
        marks_saved = 0
        for semester in available_semesters:
            for subject in range(1, 8):
                subject_code = form.get(f'semester_{semester}_subject_{subject}_code')
                subject_name = form.get(f'semester_{semester}_subject_{subject}_name')
                internal1 = form.get(f'semester_{semester}_subject_{subject}_internal1')
                internal2 = form.get(f'semester_{semester}_subject_{subject}_internal2')
                
                # Only save if all fields are provided and not empty
                if all([subject_code, subject_name, internal1, internal2]) and \
                   all([str(x).strip() for x in [subject_code, subject_name, internal1, internal2]]):
                    try:
                        mark = Mark(
                            student_id=new_student.reg_no,
                            semester=semester,
                            subject_code=subject_code.strip(),
                            subject_name=subject_name.strip(),
                            internal_1=float(internal1),
                            internal_2=float(internal2)
                        )
                        db.add(mark)
                        marks_saved += 1
                    except ValueError:
                        continue  # Skip invalid marks
        
        db.commit()
        
        success_msg = f"Student {new_student.name} created successfully"
        if marks_saved > 0:
            success_msg += f" with {marks_saved} subject marks"
        
        return templates.TemplateResponse(
            "enter_student.html",
            {"request": request, "success": success_msg}
        )
        
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "enter_student.html",
            {"request": request, "error": f"Error creating student: {str(e)}"}
        )

@router.post("/view-student/search")
async def search_student_web(
    request: Request,
    student_id: str = Form(...),
    db: Session = Depends(get_db)
):
    if not student_id.strip():
        return templates.TemplateResponse(
            "view_student.html",
            {"request": request, "error": "Please enter a student ID"}
        )
    
    return RedirectResponse(
        url=f"/student/{student_id.strip()}",
        status_code=status.HTTP_302_FOUND
    )

# Student API Routes
@router.post("/api/student", response_model=StudentSchema)
async def create_student(
    student_data: StudentCreateWithMarks,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    # Check if student with any of the IDs already exists
    existing_student = db.query(Student).filter(
        or_(
            Student.reg_no == student_data.reg_no,
            Student.umis_id == student_data.umis_id,
            Student.emis_id == student_data.emis_id
        )
    ).first()
    
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this Registration Number, UMIS ID, or EMIS ID already exists"
        )
    
    # Create new student
    new_student = Student(
        reg_no=student_data.reg_no,
        umis_id=student_data.umis_id,
        emis_id=student_data.emis_id,
        name=student_data.name,
        aadhar_number=student_data.aadhar_number,
        phone_number=student_data.phone_number,
        address=student_data.address
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    # Add marks if provided
    if student_data.marks:
        for mark_data in student_data.marks:
            new_mark = Mark(
                student_id=new_student.reg_no,
                semester=mark_data.semester,
                subject_code=mark_data.subject_code,
                subject_name=mark_data.subject_name,
                internal_1=mark_data.internal_1,
                internal_2=mark_data.internal_2
            )
            db.add(new_mark)
        
        db.commit()
    
    return new_student

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

@router.put("/api/student/{identifier}/marks")
async def update_student_marks(
    identifier: str,
    marks_data: List[MarkCreate],
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
    
    # Check if student can have marks for the requested semesters
    from models import get_academic_year_info
    academic_info = get_academic_year_info(student.admission_year)
    
    # Validate that marks are only being added for available semesters
    for mark_data in marks_data:
        if mark_data.semester not in academic_info['available_semesters']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add marks for semester {mark_data.semester}. Student is currently in semester {academic_info['current_semester']}"
            )
    
    # Delete existing marks for the semesters being updated
    semesters_to_update = list(set([mark.semester for mark in marks_data]))
    db.query(Mark).filter(
        Mark.student_id == student.reg_no,
        Mark.semester.in_(semesters_to_update)
    ).delete(synchronize_session=False)
    
    # Add new marks
    for mark_data in marks_data:
        new_mark = Mark(
            student_id=student.reg_no,
            semester=mark_data.semester,
            subject_code=mark_data.subject_code,
            subject_name=mark_data.subject_name,
            internal_1=mark_data.internal_1,
            internal_2=mark_data.internal_2
        )
        db.add(new_mark)
    
    db.commit()
    
    return {"message": f"Updated marks for {len(marks_data)} subjects across {len(semesters_to_update)} semesters"}

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
        
        # Get academic information
        from models import get_academic_year_info
        academic_info = get_academic_year_info(student.admission_year)
        
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
                "semester_data": semester_data,
                "academic_info": academic_info
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
