@echo off
echo Starting CPU Scheduling Algorithms Visualizer...
echo.

REM Check if streamlit is installed
streamlit --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Streamlit is not installed.
    echo Please run install_requirements.bat first.
    pause
    exit /b 1
)

REM Start Streamlit app
echo Opening Streamlit app in your browser...
streamlit run streamlit_app.py

pause
