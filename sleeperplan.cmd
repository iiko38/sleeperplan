@echo off
if exist %~dp0.venv\Scripts\sleeperplan.exe (
    %~dp0.venv\Scripts\sleeperplan.exe %*
) else (
    py -m sleeperplan %*
)
