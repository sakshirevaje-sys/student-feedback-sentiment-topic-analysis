@echo off
cd /d "%~dp0"
echo Installing required libraries (first run may take a few minutes)...
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo Installation failed. Please check your internet connection and Python installation.
  pause
  exit /b 1
)
echo Starting Student Feedback Analyzer...
py -m streamlit run app.py
pause
