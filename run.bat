@echo off
REM Launch MDfier from source (Windows)
setlocal
cd /d "%~dp0"

REM Prefer the project venv; fall back to system Python.
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" app.py
) else (
    echo Virtual environment not found. Creating it and installing dependencies...
    python -m venv .venv || goto :error
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
    start "" ".venv\Scripts\pythonw.exe" app.py
)
goto :eof

:error
echo.
echo Failed to start. Make sure Python is installed and on PATH.
pause
exit /b 1
