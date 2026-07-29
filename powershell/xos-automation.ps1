#Requires -Version 5.1
<#
.SYNOPSIS
XOS Automation entrypoint. Use with: pwsh -File xos-automation.ps1 -Command <cmd>
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet("bootstrap","health","env-check","diagnose","reset")]
    [string]$Command,
    [string]$ProjectName = "my-xos-app"
)

$moduleDir = $PSScriptRoot
Import-Module (Join-Path $moduleDir "XOSEnvironment.psm1") -Force

switch ($Command) {
    "bootstrap" {
        Initialize-XOSProject -ProjectName $ProjectName
    }
    "health" {
        $ok = Invoke-XOSHealthCheck
        if (-not $ok) { exit 1 }
    }
    "env-check" {
        & (Join-Path $moduleDir "diagnostics/Test-XOSEnvironment.ps1")
    }
    "diagnose" {
        Write-Host "=== XOS Environment ===" -ForegroundColor Cyan
        Get-XOSEnvironment | Format-List
        Write-Host ""
        Write-Host "=== Health Check ===" -ForegroundColor Cyan
        Invoke-XOSHealthCheck
    }
    "reset" {
        Write-Host "[WARN] This will delete node_modules and reinstall. Continue? (y/n)" -ForegroundColor Yellow
        $confirm = Read-Host
        if ($confirm -ne "y") { exit 0 }
        Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
        Remove-Item pnpm-lock.yaml -ErrorAction SilentlyContinue
        pnpm install
        Write-Host "[OK] Workspace reset complete." -ForegroundColor Green
    }
}
