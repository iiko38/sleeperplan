@echo off
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=build\reviewed\model.scad"

if not exist "%TARGET%" (
    echo Target 3D model %TARGET% not found.
    exit /b 1
)

echo Launching OpenSCAD 3D GUI for %TARGET%...
start "" "C:\Program Files\OpenSCAD\openscad.exe" "%~dp0%TARGET%"
