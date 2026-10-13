@echo off
setlocal
pushd "%~dp0"

if exist "Image_Archiver.exe" (
    "Image_Archiver.exe" %*
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Image_Archiver.exe was not found and Python is not installed.
        echo Run Build_Image_Archiver.bat or install Python 3.10 or newer.
        set "RUN_EXIT=1"
    ) else (
        python image_archiver.py %*
        set "RUN_EXIT=%ERRORLEVEL%"
    )
)

if not defined RUN_EXIT set "RUN_EXIT=%ERRORLEVEL%"
popd
if not "%RUN_EXIT%"=="0" pause
exit /b %RUN_EXIT%
