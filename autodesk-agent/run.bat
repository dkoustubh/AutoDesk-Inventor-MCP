@echo off
echo ===================================================
echo   Starting ATS Autodesk Agent & Copilot
echo ===================================================
cd /d %~dp0
set ATS_SERVER_URL=ws://192.168.11.94:8005
set COPILOT_UI_URL=http://192.168.11.94:5173
set ATS_WORKSTATION_IP=192.168.11.150

echo Launching ATS Copilot Web Interface...
start "" "%COPILOT_UI_URL%"

echo Connecting Native Windows CAD Agent...
powershell -ExecutionPolicy Bypass -File "%~dp0agent.ps1" -ServerUrl "%ATS_SERVER_URL%" -WorkstationIp "%ATS_WORKSTATION_IP%"
pause
