#Requires -Version 5.1
using namespace System.Management.Automation

<#
.SYNOPSIS
PowerShell XOS Environment Module
Manages local dev environment: bootstrap, health checks, diagnostics.
#>

$Script:ModuleRoot = $PSScriptRoot

function Get-XOSEnvironment {
    <#
    .SYNOPSIS
    Returns the current XOS environment status.
    #>
    [CmdletBinding()]
    param()

    $info = @{
        OS             = if ($IsWindows) { "Windows" } elseif ($IsMacOS) { "macOS" } else { "Linux" }
        Node           = $null
        Bun            = $null
        PNPM           = $null
        Python         = $null
        Expo           = $null
        EAS            = $null
        Java           = $null
        AndroidSDK     = $null
        Xcode          = $null
        Git            = $null
        Docker         = $null
    }

    try { $info.Node = (node --version 2>$null) -replace 'v', '' } catch {}
    try { $info.Bun = (bun --version 2>$null) } catch {}
    try { $info.PNPM = (pnpm --version 2>$null) } catch {}
    try { $info.Python = (python3 --version 2>$null) -replace 'Python ', '' } catch {}
    try { $info.Expo = (npx expo --version 2>$null) } catch {}
    try { $info.Git = (git --version 2>$null) -replace 'git version ', '' } catch {}
    try { $info.Docker = (docker --version 2>$null) -replace 'Docker version ', '' } catch {}

    if ($IsMacOS) {
        try { $info.Xcode = (xcodebuild -version 2>$null | Select-Object -First 1) -replace 'Xcode ', '' } catch {}
    }

    if ($env:ANDROID_HOME) { $info.AndroidSDK = $env:ANDROID_HOME }
    elseif ($env:ANDROID_SDK_ROOT) { $info.AndroidSDK = $env:ANDROID_SDK_ROOT }

    return [PSCustomObject]$info
}

function Test-XOSPrerequisites {
    <#
    .SYNOPSIS
    Validates that all required tools for Expo + React Native development are installed.
    #>
    [CmdletBinding()]
    param(
        [switch]$iOS,
        [switch]$Android
    )

    $env = Get-XOSEnvironment
    $missing = @()
    $warnings = @()

    if (-not $env.Node) { $missing += "Node.js (>= 18)" }
    if (-not $env.PNPM) { $missing += "pnpm (npm i -g pnpm)" }
    if (-not $env.Expo) { $missing += "Expo CLI (npm i -g expo-cli)" }
    if (-not $env.Git) { $missing += "Git" }

    if ($Android -or (-not $iOS -and -not $IsMacOS)) {
        if (-not $env.AndroidSDK) { $missing += "Android SDK (set ANDROID_HOME)" }
        if (-not $env.Java) { $warnings += "Java/JDK 17+ recommended for Android builds" }
    }

    if ($iOS -or $IsMacOS) {
        if (-not $env.Xcode) { $missing += "Xcode (macOS only)" }
    }

    if ($missing.Count -gt 0) {
        Write-Host "[FAIL] Missing prerequisites:" -ForegroundColor Red
        $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        return $false
    }

    if ($warnings.Count -gt 0) {
        Write-Host "[WARN] Warnings:" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }

    Write-Host "[OK] All prerequisites met" -ForegroundColor Green
    return $true
}

function Invoke-XOSHealthCheck {
    <#
    .SYNOPSIS
    Runs a comprehensive health check on the XOS project environment.
    #>
    [CmdletBinding()]
    param(
        [string]$ProjectPath = "."
    )

    $checks = @{}

    $pkgJson = Join-Path $ProjectPath "package.json"
    if (Test-Path $pkgJson) {
        $checks.PackageJSON = "[OK] Found"
    } else {
        $checks.PackageJSON = "[FAIL] Missing - run 'xos bootstrap' first"
    }

    $nm = Join-Path $ProjectPath "node_modules"
    if (Test-Path $nm) {
        $checks.NodeModules = "[OK] Installed"
    } else {
        $checks.NodeModules = "[WARN] Missing - run 'pnpm install'"
    }

    $tsconfig = Join-Path $ProjectPath "tsconfig.json"
    if (Test-Path $tsconfig) {
        $checks.TypeScript = "[OK] Configured"
    } else {
        $checks.TypeScript = "[WARN] Missing"
    }

    $tailwind = Join-Path $ProjectPath "tailwind.config.js"
    if (Test-Path $tailwind) {
        $checks.NativeWind = "[OK] Configured"
    } else {
        $checks.NativeWind = "[WARN] Missing"
    }

    $eas = Join-Path $ProjectPath "eas.json"
    if (Test-Path $eas) {
        $checks.EASBuild = "[OK] Configured"
    } else {
        $checks.EASBuild = "[WARN] Missing - run 'eas build:configure'"
    }

    Write-Host "XOS Health Check - $ProjectPath" -ForegroundColor Cyan
    Write-Host ""
    foreach ($key in $checks.Keys | Sort-Object) {
        $color = if ($checks[$key] -match "^\[OK\]") { "Green" } else { "Yellow" }
        Write-Host "  $key : $($checks[$key])" -ForegroundColor $color
    }

    $healthy = ($checks.Values | Where-Object { $_ -match "^\[FAIL\]" }).Count -eq 0
    return $healthy
}

function Initialize-XOSProject {
    <#
    .SYNOPSIS
    Bootstraps a new Expo project with XOS conventions.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ProjectName,

        [string]$Template = "blank-typescript"
    )

    Write-Host "Bootstrapping XOS project: $ProjectName" -ForegroundColor Cyan

    npx create-expo-app@latest $ProjectName --template $Template
    Set-Location $ProjectName

    pnpm add expo-router expo-haptics react-native-reanimated react-native-gesture-handler @shopify/flash-list nativewind tailwindcss zustand @tanstack/react-query react-hook-form @hookform/resolvers zod react-native-mmkv

    pnpm add -D @types/react typescript eslint

    $dirs = @("app", "components", "stores", "shared/validation", "features", "tests/unit", "tests/e2e")
    $dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

    @"
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <QueryClientProvider client={queryClient}>
        <StatusBar style="auto" />
        <Stack screenOptions={{ headerShown: false }} />
      </QueryClientProvider>
    </GestureHandlerRootView>
  );
}
"@ | Out-File -FilePath "app/_layout.tsx" -Encoding UTF8

    Write-Host "[OK] XOS project '$ProjectName' bootstrapped successfully!" -ForegroundColor Green
    Write-Host "   cd $ProjectName && npx expo start" -ForegroundColor Gray
}



function Test-XOSEnvironment {
    <#
    .SYNOPSIS
    Validates all required and optional tools for XOS + Expo development.
    #>
    [CmdletBinding()]
    param([switch]$VerboseOutput)

    $allOk = $true

    function Test-Tool {
        param([string]$Name, [string]$Command, [string]$InstallHint, [string]$MinVersion)
        Write-Host -NoNewline "  $Name ... "
        try {
            $parts = $Command -split " "
            $exe = $parts[0]
            $rest = $parts[1..$($parts.Length - 1)]
            $out = & $exe @rest 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0 -and $out.Trim()) {
                $ver = ($out -split "`n")[0] -replace "[^0-9.]", ""
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
    Test-Tool -Name "Python" -Command "python --version" -InstallHint "https://python.org" -MinVersion "3.10"
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
    return $allOk
}

Export-ModuleMember -Function Get-XOSEnvironment, Test-XOSPrerequisites, Invoke-XOSHealthCheck, Initialize-XOSProject, Test-XOSEnvironment
