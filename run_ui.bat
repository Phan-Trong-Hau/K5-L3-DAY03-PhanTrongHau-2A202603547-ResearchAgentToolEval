@echo off
setlocal
cd /d "%~dp0starter_v0"
if errorlevel 1 exit /b 1

if exist ".venv\Scripts\python.exe" goto check_dependencies

where py >nul 2>&1
if errorlevel 1 goto use_python
py -3 -m venv .venv
if errorlevel 1 exit /b 1
goto install_dependencies

:use_python
where python >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required. Install Python and enable Add Python to PATH.
    exit /b 1
)
python -m venv .venv
if errorlevel 1 exit /b 1
goto install_dependencies

:check_dependencies
".venv\Scripts\python.exe" -c "import streamlit, openai, requests, yaml, pypdf" >nul 2>&1
if not errorlevel 1 goto start_ui

:install_dependencies
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

:start_ui
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false %*
exit /b %errorlevel%
