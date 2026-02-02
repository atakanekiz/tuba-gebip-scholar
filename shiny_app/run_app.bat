@echo off
REM Add R to PATH and run the Shiny app
REM This script temporarily adds R to PATH for this session

echo ========================================
echo TUBA GEBIP Shiny Dashboard Launcher
echo ========================================
echo.

REM Set R path
set "R_HOME=C:\Program Files\R\R-4.5.1"
set "PATH=%R_HOME%\bin;%PATH%"

echo R_HOME set to: %R_HOME%
echo.

REM Check if R is accessible
echo Checking R installation...
R --version
if errorlevel 1 (
    echo.
    echo ERROR: R not found!
    echo Please check that R is installed at: %R_HOME%
    echo.
    pause
    exit /b 1
)

echo.
echo R found successfully!
echo.
echo ========================================
echo Installing required packages...
echo ========================================
echo.

REM Install packages
Rscript install_packages.R
if errorlevel 1 (
    echo.
    echo WARNING: Package installation had issues.
    echo You may need to install packages manually.
    echo.
    pause
)

echo.
echo ========================================
echo Launching Shiny app...
echo ========================================
echo.
echo The app will open in your default browser.
echo Press Ctrl+C to stop the server.
echo.

REM Run the app
cd ..
Rscript launch_shiny.R

pause
