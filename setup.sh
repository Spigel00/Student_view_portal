#!/bin/bash

echo "===================================================="
echo "Student View Portal - Quick Setup Script"
echo "===================================================="
echo

echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.7 or higher and try again"
    exit 1
fi

$PYTHON_CMD --version
echo "✓ Python is installed"
echo

echo "Step 2: Creating virtual environment..."
$PYTHON_CMD -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created"
echo

echo "Step 3: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

echo "Step 4: Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"
echo

echo "Step 5: Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Environment file created from template"
    echo "NOTE: You can modify .env file if needed"
else
    echo "✓ Environment file already exists"
fi
echo

echo "Step 6: Initializing database..."
python setup_database.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to initialize database"
    exit 1
fi
echo "✓ Database initialized with sample data"
echo

echo "===================================================="
echo "SETUP COMPLETE!"
echo "===================================================="
echo
echo "Login Credentials:"
echo "  Username: teacher1  | Password: password123"
echo "  Username: admin     | Password: admin123"
echo
echo "To start the application:"
echo "  python main.py"
echo
echo "The app will be available at: http://localhost:8000"
echo