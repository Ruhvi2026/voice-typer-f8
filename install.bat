@echo off
title Bangla Voice Typer Setup
echo ========================================================
echo Installing dependencies for Bangla Voice Typer...
echo ========================================================
cd /d "%~dp0"
pip install -r requirements.txt
echo.
echo ========================================================
echo Dependencies installed successfully!
echo Run 'run.bat' or double-click 'start_silent.vbs' to start.
echo ========================================================
pause
