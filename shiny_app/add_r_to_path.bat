@echo off
REM Add R to Windows PATH permanently (requires admin rights)

echo ========================================
echo Add R to Windows PATH Permanently
echo ========================================
echo.
echo This will add R to your system PATH.
echo You need to run this as Administrator!
echo.
echo After running this, you can use R from any command prompt.
echo.

set "R_PATH=C:\Program Files\R\R-4.5.1\bin"

echo R will be added to PATH: %R_PATH%
echo.
pause

REM Add to system PATH (requires admin)
setx PATH "%PATH%;%R_PATH%" /M

if errorlevel 1 (
    echo.
    echo ERROR: Failed to add R to PATH.
    echo Make sure you run this script as Administrator!
    echo.
    echo Right-click on this file and select "Run as administrator"
    echo.
) else (
    echo.
    echo SUCCESS! R has been added to your system PATH.
    echo.
    echo Please close and reopen any command prompts for the change to take effect.
    echo.
)

pause
