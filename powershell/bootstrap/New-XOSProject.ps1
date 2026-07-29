#Requires -Version 5.1
<#
.SYNOPSIS
Creates a new XOS project with Expo + React Native conventions.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Name,
    [string]$Path = ".",
    [string]$Template = "blank-typescript"
)

$projectDir = Join-Path $Path $Name
if (Test-Path $projectDir) {
    Write-Host "[FAIL] Project '$Name' already exists at $projectDir" -ForegroundColor Red
    exit 1
}

Write-Host "Creating XOS project: $Name" -ForegroundColor Cyan

& npx create-expo-app@latest $Name --template $Template -- --cwd $Path
Set-Location $projectDir

pnpm add expo-router expo-haptics react-native-reanimated react-native-gesture-handler @shopify/flash-list nativewind tailwindcss zustand @tanstack/react-query react-hook-form @hookform/resolvers zod react-native-mmkv
pnpm add -D @types/react typescript eslint

$dirs = @("app","components","stores","shared/validation","features","tests/unit","tests/e2e")
$dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

Write-Host "[OK] XOS project '$Name' created at $projectDir" -ForegroundColor Green
