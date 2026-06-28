@echo off
REM Build the portable MDfier.exe (Windows)
setlocal

echo [1/2] Installing dependencies...
python -m pip install -r requirements.txt || goto :error

echo [2/2] Building portable executable...
python -m PyInstaller --noconfirm build.spec || goto :error

echo.
echo Build complete: dist\MDfier.exe
goto :eof

:error
echo.
echo Build failed. See the output above for details.
exit /b 1
