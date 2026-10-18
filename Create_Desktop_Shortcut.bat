@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Create_Desktop_Shortcut.ps1"
if errorlevel 1 pause
