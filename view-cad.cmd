@echo off
setlocal

set "OPENSCAD_EXE=C:\Program Files\OpenSCAD\openscad.exe"
if not exist "%OPENSCAD_EXE%" (
    echo OpenSCAD not found at "%OPENSCAD_EXE%".
    echo Install OpenSCAD or update OPENSCAD_EXE in view-cad.cmd.
    exit /b 1
)

if "%~1"=="" (
    set "TARGET=%~dp0build\reviewed\model.scad"
) else (
    set "TARGET=%~f1"
)

if not exist "%TARGET%" (
    echo Target 3D model "%TARGET%" not found.
    exit /b 1
)

echo Launching OpenSCAD 3D GUI for "%TARGET%"...
start "" "%OPENSCAD_EXE%" "%TARGET%"
