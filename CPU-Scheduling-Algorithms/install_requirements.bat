@echo off
echo Installing required Python packages for CPU Scheduling Visualizer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install pip packages
echo Installing packages from requirements.txt...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✅ Installation completed successfully!
    echo.
    echo To run the Streamlit app, use:
    echo streamlit run streamlit_app.py
    echo.
) else (
    echo.
    echo ❌ Installation failed. Please check the error messages above.
    echo.
)

pause
