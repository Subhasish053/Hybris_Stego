@echo off
setlocal

set "ROOT=%~dp0"
set "VENV_PY=%ROOT%.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo Virtual environment Python not found at:
    echo %VENV_PY%
    exit /b 1
)

"%VENV_PY%" -m streamlit run "%ROOT%app.py"
