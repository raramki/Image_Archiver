@echo off
setlocal
pushd "%~dp0"

python -m PyInstaller --clean --onefile --console --name Image_Archiver image_archiver.py
if errorlevel 1 (
    echo Build failed. Install Python 3 and PyInstaller with: python -m pip install pyinstaller
    popd
    exit /b 1
)

copy /Y "dist\Image_Archiver.exe" "Image_Archiver.exe" >nul
if errorlevel 1 (
    echo Could not copy the executable to the package folder.
    popd
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$files = @('image_archiver.py','Image_Archiver.exe','Run_Image_Archiver.bat','Build_Image_Archiver.bat','README.md'); Compress-Archive -Path $files -DestinationPath 'Image_Archiver_Windows.zip' -Force"
if errorlevel 1 (
    echo The executable was built, but the ZIP could not be created.
    popd
    exit /b 1
)

echo Created Image_Archiver.exe and Image_Archiver_Windows.zip.
popd
exit /b 0
