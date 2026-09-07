@echo off
setlocal
set TARGET=%1
if "%TARGET%"=="" set TARGET=build\reviewed

if not exist "%TARGET%" (
    echo Target directory %TARGET% does not exist.
    echo Usage: view.cmd [build_directory]
    exit /b 1
)

echo Generating/updating viewer for %TARGET%...
"%~dp0.venv\Scripts\python.exe" "%~dp0tools\viewer.py" "%TARGET%"

echo Opening visual model and technical drawings in default browser...
start "" "%~dp0%TARGET%\viewer.html"
