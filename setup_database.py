"""
Database Setup and Sample Data Script
Run this script to initialize the database with sample data
"""

from sqlalchemy.orm import sessionmaker
from models import engine, Teacher, Student, Mark
from auth import get_password_hash
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_sample_data():
    """Create sample teachers, students, and marks for testing"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_teacher = db.query(Teacher).first()
        if existing_teacher:
            logger.info("Sample data already exists. Skipping creation.")
            return
        
        # Create sample teachers
        teachers = [
            Teacher(
                username="teacher1",
                hashed_password=get_password_hash("password123"),
                name="Dr. Sarah Johnson"
            ),
            Teacher(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                name="Admin User"
            )
        ]
        
        for teacher in teachers:
            db.add(teacher)
        
        # Create sample students
        students = [
            Student(
                reg_no="REG001",
                umis_id="UMIS001",
                emis_id="EMIS001",
                name="John Doe",
                aadhar_number="123456789012",
                phone_number="9876543210",
                address="123 Main Street, City, State",
                admission_year=2022  # 3rd year student
            ),
            Student(
                reg_no="REG002",
                umis_id="UMIS002",
                emis_id="EMIS002",
                name="Jane Smith",
                aadhar_number="234567890123",
                phone_number="8765432109",
                address="456 Oak Avenue, City, State",
                admission_year=2023  # 2nd year student
            ),
            Student(
                reg_no="REG003",
                umis_id="UMIS003",
                emis_id="EMIS003",
                name="Mike Johnson",
                aadhar_number="345678901234",
                phone_number="7654321098",
                address="789 Pine Road, City, State",
                admission_year=2024  # 1st year student
            )
        ]
        
        for student in students:
            db.add(student)
        
        # Commit students first
        db.commit()
        
        # Sample subjects for each semester
        subjects_by_semester = {
            1: [
                ("CS101", "Introduction to Programming"),
                ("MA101", "Mathematics I"),
                ("PH101", "Physics I"),
                ("EN101", "English Communication"),
                ("CS102", "Computer Fundamentals"),
                ("MA102", "Discrete Mathematics"),
                ("CS103", "Data Structures")
            ],
            2: [
                ("CS201", "Object Oriented Programming"),
                ("MA201", "Mathematics II"),
                ("PH201", "Physics II"),
                ("CS202", "Database Systems"),
                ("CS203", "Computer Networks"),
                ("CS204", "Operating Systems"),
                ("CS205", "Software Engineering")
            ],
            3: [
                ("CS301", "Algorithms"),
                ("CS302", "Computer Graphics"),
                ("CS303", "Web Development"),
                ("CS304", "Mobile Computing"),
                ("CS305", "Machine Learning"),
                ("CS306", "Artificial Intelligence"),
                ("CS307", "Compiler Design")
            ]
        }
        
        # Create sample marks for each student
        for student in students:
            for semester, subjects in subjects_by_semester.items():
                for subject_code, subject_name in subjects:
                    # Generate some realistic marks
                    internal_1 = 35 + (hash(student.reg_no + subject_code + "1") % 16)  # 35-50
                    internal_2 = 30 + (hash(student.reg_no + subject_code + "2") % 21)  # 30-50
                    
                    mark = Mark(
                        student_id=student.reg_no,
                        semester=semester,
                        subject_code=subject_code,
                        subject_name=subject_name,
                        internal_1=internal_1,
                        internal_2=internal_2
                    )
                    db.add(mark)
        
        db.commit()
        logger.info("Sample data created successfully!")
        
        # Print login credentials
        print("\n" + "="*50)
        print("SAMPLE DATA CREATED SUCCESSFULLY!")
        print("="*50)
        print("\nLogin Credentials:")
        print("-" * 20)
        print("Username: teacher1")
        print("Password: password123")
        print("\nUsername: admin")
        print("Password: admin123")
        print("\nSample Student IDs:")
        print("-" * 20)
        for student in students:
            print(f"Name: {student.name}")
            print(f"  - Reg No: {student.reg_no}")
            print(f"  - UMIS ID: {student.umis_id}")
            print(f"  - EMIS ID: {student.emis_id}")
            print()
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
