@echo off
pushd %~dp0
powershell -ExecutionPolicy Bypass -File start.ps1
pause
