@echo off
echo Starting Crypto Futures Signals Bot...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Backend setup
echo Setting up backend...
cd /d "%SCRIPT_DIR%backend"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1

REM Start backend in new window
echo Starting backend server...
start "Backend Server" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && python main.py"

REM Frontend setup
echo Setting up frontend...
cd /d "%SCRIPT_DIR%frontend"

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
)

REM Start frontend
echo Starting frontend server...
call npm run dev

pause

