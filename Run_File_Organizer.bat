@echo off
setlocal
pushd "%~dp0"

if exist "File_Organizer.exe" goto run_executable

where python >nul 2>nul
if errorlevel 1 goto python_missing

python file_organizer.py %*
set "RUN_EXIT=%ERRORLEVEL%"
goto finish

:run_executable
"File_Organizer.exe" %*
set "RUN_EXIT=%ERRORLEVEL%"
goto finish

:python_missing
echo File_Organizer.exe was not found and Python is not installed.
echo Run Build_File_Organizer.bat or install Python 3.10 or newer.
set "RUN_EXIT=1"

:finish
popd
if not "%RUN_EXIT%"=="0" pause
exit /b %RUN_EXIT%
