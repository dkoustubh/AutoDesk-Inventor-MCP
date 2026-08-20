# Snap InventorAI Chat directly to the right side of Autodesk Inventor
param(
    [string]$Url = "http://192.168.11.94:5173"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$width = 420
$height = $screen.Height
$left = $screen.Width - $width
$top = 0

Write-Host "Opening InventorAI Chat docked to Autodesk Inventor screen..." -ForegroundColor Cyan

# Launch edge or chrome app mode snapped to the right sidebar
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"

if (Test-Path $edgePath) {
    Start-Process $edgePath -ArgumentList "--app=$Url", "--window-position=$left,$top", "--window-size=$width,$height"
} elseif (Test-Path $chromePath) {
    Start-Process $chromePath -ArgumentList "--app=$Url", "--window-position=$left,$top", "--window-size=$width,$height"
} else {
    Start-Process $Url
}
