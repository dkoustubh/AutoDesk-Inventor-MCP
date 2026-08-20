@echo off
echo ===================================================
echo   Installing InventorAI Chat AddIn for Inventor
echo ===================================================
cd /d %~dp0
set ADDIN_FILE=Autodesk.InventorAIChat.Inventor.addin

rem Copy to Inventor 2026, 2025, 2024 Addins folders
if not exist "%APPDATA%\Autodesk\Inventor 2026\Addins" mkdir "%APPDATA%\Autodesk\Inventor 2026\Addins"
copy /y "%~dp0%ADDIN_FILE%" "%APPDATA%\Autodesk\Inventor 2026\Addins\%ADDIN_FILE%" >nul 2>nul

if not exist "%APPDATA%\Autodesk\Inventor 2025\Addins" mkdir "%APPDATA%\Autodesk\Inventor 2025\Addins"
copy /y "%~dp0%ADDIN_FILE%" "%APPDATA%\Autodesk\Inventor 2025\Addins\%ADDIN_FILE%" >nul 2>nul

if not exist "%APPDATA%\Autodesk\Inventor 2024\Addins" mkdir "%APPDATA%\Autodesk\Inventor 2024\Addins"
copy /y "%~dp0%ADDIN_FILE%" "%APPDATA%\Autodesk\Inventor 2024\Addins\%ADDIN_FILE%" >nul 2>nul

if not exist "%APPDATA%\Autodesk\ApplicationPlugins" mkdir "%APPDATA%\Autodesk\ApplicationPlugins"
copy /y "%~dp0%ADDIN_FILE%" "%APPDATA%\Autodesk\ApplicationPlugins\%ADDIN_FILE%" >nul 2>nul

if not exist "%ALLUSERSPROFILE%\Autodesk\Inventor 2026\Addins" mkdir "%ALLUSERSPROFILE%\Autodesk\Inventor 2026\Addins" >nul 2>nul
copy /y "%~dp0%ADDIN_FILE%" "%ALLUSERSPROFILE%\Autodesk\Inventor 2026\Addins\%ADDIN_FILE%" >nul 2>nul

echo.
echo ===================================================
echo   [SUCCESS] InventorAI Chat Add-In Installed!
echo   Open Autodesk Inventor to see the dockable panel.
echo ===================================================
pause
