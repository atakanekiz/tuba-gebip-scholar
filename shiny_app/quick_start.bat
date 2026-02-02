@echo off
REM Quick launcher - assumes packages are already installed

set "R_HOME=C:\Program Files\R\R-4.5.1"
set "PATH=%R_HOME%\bin;%PATH%"

echo Starting Shiny app...
echo Press Ctrl+C to stop the server.
echo.

Rscript -e "shiny::runApp(launch.browser=TRUE)"
