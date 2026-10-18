@echo off
setlocal
pushd "%~dp0"

if exist "File_Organizer.exe" (
    "File_Organizer.exe" %*
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo File_Organizer.exe was not found and Python is not installed.
        echo Run Build_File_Organizer.bat or install Python 3.10 or newer.
        set "RUN_EXIT=1"
    ) else (
        python file_organizer.py %*
        set "RUN_EXIT=%ERRORLEVEL%"
    )
)

if not defined RUN_EXIT set "RUN_EXIT=%ERRORLEVEL%"
popd
if not "%RUN_EXIT%"=="0" pause
exit /b %RUN_EXIT%
