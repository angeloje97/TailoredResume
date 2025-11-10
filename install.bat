@echo off
echo ========================================
echo Resume Tailor - Installing Dependencies
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run the app with: python Source\Main.py
echo.
pause
