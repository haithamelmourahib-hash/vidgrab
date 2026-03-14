@echo off
title VidGrab - Windows Build
color 0A
echo.
echo  ============================================
echo   VidGrab - Windows Build Script
echo  ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo  Download: https://www.python.org/downloads/
    echo  IMPORTANT: Check "Add Python to PATH" during install!
    pause & exit /b 1
)
echo  [OK] Python found

echo.
echo  [1/4] Installing dependencies...
pip install flask flask-cors yt-dlp pyinstaller --quiet
echo  [OK] Done

echo.
echo  [2/4] Checking FFmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo  [!] FFmpeg not found.
    echo  1. Download: https://github.com/BtbN/FFmpeg-Builds/releases
    echo  2. Download ffmpeg-master-latest-win64-gpl.zip
    echo  3. Extract and rename folder to "ffmpeg"
    echo  4. Move it to C:\ffmpeg
    echo  5. Add C:\ffmpeg\bin to system PATH
    echo  6. Re-run this script
    pause & exit /b 1
)
echo  [OK] FFmpeg found

echo.
echo  [3/4] Building VidGrab.exe...
pyinstaller --onefile --noconsole --name VidGrab --add-data "static;static" --hidden-import flask --hidden-import flask_cors --hidden-import yt_dlp main.py

if errorlevel 1 ( echo  [ERROR] Build failed. & pause & exit /b 1 )

echo.
echo  ============================================
echo   [DONE] VidGrab.exe is ready in /dist
echo   Send that file to Haitham!
echo  ============================================
pause
