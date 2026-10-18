@echo off
setlocal
pushd "%~dp0"

python -m PyInstaller --clean --noconfirm --onefile --console --name File_Organizer file_organizer.py
if errorlevel 1 (
    echo Build failed. Install Python 3 and PyInstaller with: python -m pip install pyinstaller
    popd
    exit /b 1
)

copy /Y "dist\File_Organizer.exe" "File_Organizer.exe" >nul
if errorlevel 1 (
    echo Could not copy the executable to the package folder.
    popd
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$files = @('file_organizer.py','File_Organizer.exe','Run_File_Organizer.bat','Build_File_Organizer.bat','Create_Desktop_Shortcut.bat','Create_Desktop_Shortcut.ps1','README.md'); Compress-Archive -Path $files -DestinationPath 'File_Organizer_Windows.zip' -Force"
if errorlevel 1 (
    echo The executable was built, but the ZIP could not be created.
    popd
    exit /b 1
)

echo Created File_Organizer.exe and File_Organizer_Windows.zip.
echo Run Create_Desktop_Shortcut.bat to add a desktop shortcut.
popd
exit /b 0
