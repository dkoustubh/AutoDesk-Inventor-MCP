@echo off
echo ===================================================
echo   Building ATS Autodesk Agent for Windows (.NET 8)
echo ===================================================
cd /d %~dp0
dotnet build src/ATS.AutodeskAgent.csproj -c Release
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed. Make sure .NET 8 SDK is installed.
    pause
    exit /b %ERRORLEVEL%
)
echo [SUCCESS] Build completed successfully.
pause
