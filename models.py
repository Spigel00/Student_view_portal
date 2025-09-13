from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database configuration - using SQLite for easier setup
USE_SQLITE = os.getenv("USE_SQLITE", "True").lower() == "true"

if USE_SQLITE:
    DATABASE_URL = "sqlite:///./student_portal.db"
else:
    # MySQL configuration (optional)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "student_portal")
    DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)

class Student(Base):
    __tablename__ = "students"
    
    reg_no = Column(String(20), primary_key=True, index=True)
    umis_id = Column(String(20), unique=True, index=True, nullable=False)
    emis_id = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    aadhar_number = Column(String(12), unique=True, nullable=False)
    phone_number = Column(String(15), nullable=False)
    address = Column(String(255), nullable=False)
    admission_year = Column(Integer, nullable=False)  # Year of admission (e.g., 2023)
    
    # Relationship with marks
    marks = relationship("Mark", back_populates="student")

class Mark(Base):
    __tablename__ = "marks"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), ForeignKey("students.reg_no"), nullable=False)
    semester = Column(Integer, nullable=False)  # 1-6
    subject_code = Column(String(10), nullable=False)
    subject_name = Column(String(100), nullable=False)
    internal_1 = Column(Float, nullable=False, default=0)
    internal_2 = Column(Float, nullable=False, default=0)
    
    # Computed field - best of two internals
    @property
    def best_of_two(self):
        return max(self.internal_1, self.internal_2)
    
    # Relationship with student
    student = relationship("Student", back_populates="marks")

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Utility functions for semester calculation
def calculate_current_semester(admission_year: int, current_date: datetime = None) -> int:
    """
    Calculate the current semester based on admission year and current date.
    
    Args:
        admission_year: Year of admission (e.g., 2023)
        current_date: Current date (defaults to now)
    
    Returns:
        Current semester (1-6), or 6 if graduated
    """
    if current_date is None:
        current_date = datetime.now()
    
    current_year = current_date.year
    current_month = current_date.month
    
    # Calculate years since admission
    years_since_admission = current_year - admission_year
    
    # Determine semester within the academic year
    # Assuming: Jan-Jun = Even semester, Jul-Dec = Odd semester
    if current_month >= 7:  # July to December (Odd semester)
        semester_in_year = 1
    else:  # January to June (Even semester)
        semester_in_year = 2
        if current_month <= 6 and years_since_admission > 0:
            years_since_admission -= 1
    
    # Calculate total semester
    total_semester = (years_since_admission * 2) + semester_in_year
    
    # Cap at 6 semesters (3 years)
    return min(total_semester, 6)

def get_graduation_year(admission_year: int) -> int:
    """Get graduation year based on admission year (3-year course)"""
    return admission_year + 3

def is_student_graduated(admission_year: int, current_date: datetime = None) -> bool:
    """Check if student has graduated"""
    if current_date is None:
        current_date = datetime.now()
    
    graduation_year = get_graduation_year(admission_year)
    return current_date.year >= graduation_year

def get_academic_year_info(admission_year: int, current_date: datetime = None) -> dict:
    """
    Get comprehensive academic year information for a student.
    
    Returns:
        Dictionary with academic info including current semester, graduation year, etc.
    """
    if current_date is None:
        current_date = datetime.now()
    
    current_semester = calculate_current_semester(admission_year, current_date)
    graduation_year = get_graduation_year(admission_year)
    is_graduated = is_student_graduated(admission_year, current_date)
    
    return {
        'admission_year': admission_year,
        'graduation_year': graduation_year,
        'current_semester': current_semester,
        'is_graduated': is_graduated,
        'total_semesters': 6,
        'available_semesters': list(range(1, current_semester + 1))
    }
