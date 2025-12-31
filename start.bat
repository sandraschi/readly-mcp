@echo off
pushd %~dp0
call d:\Dev\venv\Scripts\activate.bat || echo Warning: Could not activate venv
python -m src.readly_mcp
pause
