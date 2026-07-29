#Requires -Version 5.1
<#
.SYNOPSIS
Validates the XOS development environment.
#>
[CmdletBinding()]
param([switch]$VerboseOutput)

$allOk = $true

function Test-Tool {
    param([string]$Name, [string]$Command, [string]$InstallHint, [string]$MinVersion)
    Write-Host -NoNewline "  $Name ... "
    try {
        $out = Invoke-Expression $Command 2>$null
        if ($LASTEXITCODE -eq 0 -and $out) {
            $ver = ($out -split '\n')[0] -replace '[^0-9.]', ''
            if ($MinVersion -and [version]$ver -lt [version]$MinVersion) {
                Write-Host "[OLD] $ver (need >= $MinVersion)" -ForegroundColor Yellow
                $script:allOk = $false
            } else {
                Write-Host "[OK] $ver" -ForegroundColor Green
            }
        } else {
            Write-Host "[MISSING]" -ForegroundColor Red
            if ($InstallHint) { Write-Host "       Install: $InstallHint" -ForegroundColor Gray }
            $script:allOk = $false
        }
    } catch {
        Write-Host "[MISSING]" -ForegroundColor Red
        if ($InstallHint) { Write-Host "       Install: $InstallHint" -ForegroundColor Gray }
        $script:allOk = $false
    }
}

Write-Host "XOS Environment Check" -ForegroundColor Cyan
Write-Host "====================="
Write-Host ""

Write-Host "Required tools:" -ForegroundColor White
Test-Tool -Name "Node.js" -Command "node --version" -InstallHint "https://nodejs.org" -MinVersion "18"
Test-Tool -Name "pnpm" -Command "pnpm --version" -InstallHint "npm i -g pnpm" -MinVersion "8"
Test-Tool -Name "Python" -Command "python3 --version" -InstallHint "https://python.org" -MinVersion "3.10"
Test-Tool -Name "Git" -Command "git --version" -InstallHint "https://git-scm.com" -MinVersion "2.40"
Test-Tool -Name "Expo CLI" -Command "npx expo --version" -InstallHint "npm i -g expo-cli"

Write-Host ""
Write-Host "Optional tools:" -ForegroundColor White
Test-Tool -Name "EAS CLI" -Command "npx eas --version" -InstallHint "npm i -g eas-cli"
Test-Tool -Name "Bun" -Command "bun --version" -InstallHint "https://bun.sh"
Test-Tool -Name "Docker" -Command "docker --version" -InstallHint "https://docker.com"

Write-Host ""
if ($allOk) {
    Write-Host "[OK] Environment ready." -ForegroundColor Green
} else {
    Write-Host "[FAIL] Some tools are missing or outdated. Install them and re-run." -ForegroundColor Red
}
exit $(if ($allOk) { 0 } else { 1 })
