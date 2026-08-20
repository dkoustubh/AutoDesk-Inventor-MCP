# Autodesk Inventor 1-Click Add-In Installer
param(
    [string]$ServerUrl = "http://192.168.11.94:5173"
)

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " Installing InventorAI Chat Add-In for Inventor" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

$addinFileName = "Autodesk.InventorAIChat.Inventor.addin"
$srcAddinPath = Join-Path $PSScriptRoot $addinFileName

if (-not (Test-Path $srcAddinPath)) {
    $srcAddinPath = Join-Path $PSScriptRoot "Autodesk.InventorAIChat.Inventor.addin"
}

# Target AddIn directories for Inventor
$appDataAddins = @(
    "$env:APPDATA\Autodesk\Inventor 2026\Addins",
    "$env:APPDATA\Autodesk\Inventor 2025\Addins",
    "$env:APPDATA\Autodesk\Inventor 2024\Addins",
    "$env:APPDATA\Autodesk\ApplicationPlugins\InventorAIChat",
    "$env:ALLUSERSPROFILE\Autodesk\Inventor 2026\Addins",
    "$env:ALLUSERSPROFILE\Autodesk\Inventor 2025\Addins"
)

$installedCount = 0

foreach ($dir in $appDataAddins) {
    try {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        $destFile = Join-Path $dir $addinFileName
        Copy-Item -Path $srcAddinPath -Destination $destFile -Force
        Write-Host "[✓] Installed AddIn manifest to: $dir" -ForegroundColor Green
        $installedCount++
    } catch {
        Write-Host "[!] Notice for $dir: $($_.Exception.Message)" -ForegroundColor Gray
    }
}

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host " Add-In Registered Successfully ($installedCount locations)!" -ForegroundColor Green
Write-Host " When you launch Autodesk Inventor, 'InventorAI Chat'" -ForegroundColor Yellow
Write-Host " will dock on the right side of your CAD window!" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan
