@echo off
echo ================================================
echo   Crypto Futures Signals Bot - Debug Mode
echo ================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo Current directory: %CD%
echo.

REM Check Python
echo [1/6] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed!
    pause
    exit /b 1
)
echo OK!
echo.

REM Check Node.js
echo [2/6] Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    pause
    exit /b 1
)
echo OK!
echo.

REM Backend setup
echo [3/6] Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies (this may take a few minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)
echo Backend dependencies installed!
echo.

REM Start backend
echo [4/6] Starting backend server...
echo Opening new window for backend...
start "Crypto Bot - Backend Server" cmd /k "cd /d %SCRIPT_DIR%backend && venv\Scripts\activate.bat && python main.py"
echo Backend starting in new window...
echo.

cd ..

REM Frontend setup
echo [5/6] Setting up frontend...
cd frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies (this may take a few minutes)...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install Node.js dependencies!
        pause
        exit /b 1
    )
)
echo Frontend dependencies installed!
echo.

REM Start frontend
echo [6/6] Starting frontend server...
echo.
echo ================================================
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo ================================================
echo.
echo Press Ctrl+C to stop the frontend server
echo.
call npm run dev

pause

