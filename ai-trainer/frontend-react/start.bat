@echo off
echo ========================================
echo AI Gym Trainer - Starting Frontend
echo ========================================
echo.

REM Add Node.js to PATH for this session
set "PATH=%PATH%;C:\Program Files\nodejs\"

echo Starting development server on http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause
