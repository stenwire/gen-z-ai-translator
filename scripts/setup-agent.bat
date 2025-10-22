@REM @echo off
@REM REM Navigate to the agent directory
@REM cd /d "%~dp0\..\agent" || exit /b 1

@REM REM Create virtual environment if it doesn't exist
@REM if not exist ".venv" (
@REM     uv venv .venv
@REM )

@REM REM Activate the virtual environment
@REM call .venv\Scripts\activate.bat

@REM REM Install requirements using uv
@REM uv pip install -r requirements.txt

@echo off
setlocal enabledelayedexpansion
echo 🚀 Setting up agent environment...

REM Navigate to the agent directory
cd /d "%~dp0\..\agent" || exit /b 1

REM Try to find uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚙️ 'uv' not found. Installing via pip...
    python -m pip install uv
)

REM Create virtual environment
where uv >nul 2>nul
if %errorlevel% equ 0 (
    echo 📦 Using uv to create venv...
    uv venv .venv
) else (
    echo 📦 Using python -m venv to create venv...
    python -m venv .venv
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
where uv >nul 2>nul
if %errorlevel% equ 0 (
    uv pip install -r requirements.txt
) else (
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

echo ✅ Agent environment setup complete!
endlocal
