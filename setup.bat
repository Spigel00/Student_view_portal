@echo off
echo ====================================================
echo Student View Portal - Quick Setup Script
echo ====================================================
echo.

echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher and try again
    pause
    exit /b 1
)
echo ✓ Python is installed
echo.

echo Step 2: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created
echo.

echo Step 3: Activating virtual environment...
call venv\Scripts\activate
echo ✓ Virtual environment activated
echo.

echo Step 4: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo Step 5: Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo ✓ Environment file created from template
    echo NOTE: You can modify .env file if needed
) else (
    echo ✓ Environment file already exists
)
echo.

echo Step 6: Initializing database...
python setup_database.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo ✓ Database initialized with sample data
echo.

echo ====================================================
echo SETUP COMPLETE!
echo ====================================================
echo.
echo Login Credentials:
echo   Username: teacher1  ^| Password: password123
echo   Username: admin     ^| Password: admin123
echo.
echo To start the application:
echo   python main.py
echo.
echo The app will be available at: http://localhost:8000
echo.
pause