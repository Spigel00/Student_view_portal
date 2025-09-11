# Student Details Web Application

A comprehensive web application for teachers to view student details and academic performance, built with Python FastAPI, MySQL, HTML, and CSS.

## Features

### 🔐 Authentication System
- Secure teacher login and registration
- New teacher account creation (sign-up)
- JWT-based authentication
- Session management with cookies
- Password hashing with bcrypt

### 👥 Student Management
- Search students by Registration Number, UMIS ID, or EMIS ID
- View detailed student information (contact details, address)
- Unique identification system with multiple ID types

### 📊 Academic Performance Tracking
- Semester-wise marks display (1-6 semesters)
- Internal assessment tracking (Internal 1, Internal 2, Best of Two)
- 7 subjects per semester support
- Automatic calculation of:
  - Total marks per semester
  - Percentage calculation
  - CGPA cutoff computation
- Overall academic performance summary

### 🎨 User Interface
- Clean, teacher-friendly web interface
- Responsive design for desktop and mobile
- Modern CSS styling with gradients and animations
- Intuitive navigation and search functionality

## Tech Stack

- **Backend**: Python FastAPI
- **Database**: SQLite (default) / MySQL (optional) with SQLAlchemy ORM
- **Frontend**: HTML, CSS, Jinja2 templates
- **Authentication**: JWT with python-jose
- **Password Security**: bcrypt via passlib
- **Styling**: Custom CSS with responsive design

## Project Structure

```
student_view_portal/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic schemas for API
├── routes.py            # API routes and web handlers
├── auth.py             # Authentication utilities
├── setup_database.py   # Database initialization script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── templates/         # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   └── student_details.html
└── static/           # Static files (CSS, JS, images)
    └── css/
        └── style.css

```

## Installation and Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- Git (optional)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
The application uses SQLite by default for easy setup. For production, you can switch to MySQL.

**Default Configuration (.env file):**
```env
# Database Configuration
USE_SQLITE=True
# MySQL settings (optional - set USE_SQLITE=False to use MySQL)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=student_portal

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
```

**For MySQL Setup:**
1. Create a MySQL database named `student_portal`
2. Set `USE_SQLITE=False` in `.env`
3. Update MySQL credentials in the `.env` file

### 3. Initialize Database
Run the setup script to create tables and sample data:
```bash
python setup_database.py
```

### 4. Start the Application
```bash
python main.py
```

The application will be available at: `http://localhost:8000`

## Usage

### Login Options

**Option 1: Use Demo Credentials**
- **Username**: `teacher1` | **Password**: `password123`
- **Username**: `admin` | **Password**: `admin123`

**Option 2: Create New Account**
1. Click "Sign up here" on the login page
2. Fill in your full name, desired username, and password
3. Click "Sign Up" to create your account
4. You'll be automatically logged in after successful registration

### Sample Student Data
The setup script creates sample students you can search for:
- **John Doe**: REG001, UMIS001, EMIS001
- **Jane Smith**: REG002, UMIS002, EMIS002  
- **Mike Johnson**: REG003, UMIS003, EMIS003

### Searching for Students
1. Login with teacher credentials
2. Use the search box on the dashboard
3. Enter any of the following for a student:
   - Registration Number (e.g., REG001)
   - UMIS ID (e.g., UMIS001)
   - EMIS ID (e.g., EMIS001)

## API Endpoints

### Authentication
- `POST /api/login` - Teacher login (returns JWT token)
- `POST /api/signup` - Teacher registration (returns JWT token)
- `POST /login` - Web form login
- `POST /signup` - Web form registration
- `GET /logout` - Logout and clear session

### Student Data
- `GET /api/student/{identifier}` - Get student by reg_no/umis_id/emis_id
- `GET /api/student/{identifier}/marks` - Get student marks with calculations

### Web Pages  
- `GET /` - Login page
- `GET /signup` - Registration page
- `GET /dashboard` - Main dashboard with search
- `GET /student/{identifier}` - Student details page with marks

## Database Schema

### Teachers Table
- `id` (Primary Key)
- `username` (Unique)
- `hashed_password`
- `name`

### Students Table
- `reg_no` (Primary Key)
- `umis_id` (Unique)
- `emis_id` (Unique)  
- `name`
- `aadhar_number`
- `phone_number`
- `address`

### Marks Table
- `id` (Primary Key)
- `student_id` (Foreign Key → students.reg_no)
- `semester` (1-6)
- `subject_code`
- `subject_name`
- `internal_1` (Marks out of 50)
- `internal_2` (Marks out of 50)
- Computed: `best_of_two` (Maximum of internal_1 and internal_2)

## Features in Detail

### Academic Performance Calculations
- **Best of Two**: Automatically selects higher marks between Internal 1 and Internal 2
- **Total Marks**: Sum of best_of_two for all subjects in a semester
- **Percentage**: (Total Marks / Max Possible Marks) × 100
- **CGPA Cutoff**: Percentage ÷ 9.5 (standard conversion)
- **Overall Performance**: Average across all completed semesters

### Security Features
- Password hashing with bcrypt
- JWT token authentication
- HTTP-only cookies for web sessions
- Protected API endpoints
- SQL injection prevention with SQLAlchemy ORM

### Responsive Design
- Mobile-friendly interface
- Flexible grid layouts
- Touch-friendly buttons and forms
- Optimized for various screen sizes

## Development

### Adding New Features
The codebase is modular and easy to extend:

- **Models**: Add new database tables in `models.py`
- **API**: Add new endpoints in `routes.py`  
- **Frontend**: Create new templates in `templates/`
- **Styling**: Modify `static/css/style.css`

### Environment Variables
Key configuration options in `.env`:
- `DEBUG=True` - Enable debug mode
- `SECRET_KEY` - JWT signing key (change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES=30` - Token validity duration

## Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to a strong, random value
- [ ] Set `DEBUG=False`
- [ ] Use environment variables for sensitive data
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure proper database permissions
- [ ] Set up regular database backups

### Deployment Options
- **Traditional**: Gunicorn + Nginx on Linux server
- **Docker**: Containerize with Docker Compose
- **Cloud**: Deploy to AWS, Google Cloud, or Azure
- **Platform**: Use Heroku, Railway, or similar platforms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
1. Check the existing documentation
2. Review the code comments
3. Create an issue with detailed information
4. Provide steps to reproduce any bugs

---

Built with ❤️ using FastAPI, MySQL, and modern web technologies.
