@echo off
REM Navigate to the agent directory
cd /d "%~dp0\..\agent" || exit /b 1

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    uv venv .venv
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Install requirements using uv
uv pip install -r requirements.txt