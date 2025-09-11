from sqlalchemy import Column, Integer, String, ForeignKey, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os
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
