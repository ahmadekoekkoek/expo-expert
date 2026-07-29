#!/usr/bin/env pwsh
<#
.SYNOPSIS
    XOS PowerShell Automation — host environment management for React Native + Expo.
.DESCRIPTION
    Manages the local development environment:
    - Bootstrap Expo projects with correct dependencies
    - Configure Android SDK, iOS certificates
    - Validate environment health
    - Run diagnostics and auto-repair
    - Build and deploy automation
.PARAMETER Command
    The operation to perform: bootstrap, validate, doctor, build, clean, deploy, health
#>

param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("bootstrap", "validate", "doctor", "build", "clean", "deploy", "health", "repair")]
    [string]$Command,

    [Parameter()]
    [string]$ProjectPath = ".",

    [Parameter()]
    [string]$Platform = "all"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─── Configuration ───────────────────────────────────────────

$Script:RequiredTools = @(
    @{ Name = "node";      MinVersion = "20.0.0";  CheckCmd = { node --version } },
    @{ Name = "npm";       MinVersion = "10.0.0";  CheckCmd = { npm --version } },
    @{ Name = "pnpm";      MinVersion = "8.0.0";   CheckCmd = { pnpm --version } },
    @{ Name = "npx";       MinVersion = "10.0.0";  CheckCmd = { npx --version } },
    @{ Name = "git";       MinVersion = "2.30.0";  CheckCmd = { git --version } },
    @{ Name = "python";    MinVersion = "3.13.0";  CheckCmd = { python3 --version } },
    @{ Name = "java";      MinVersion = "17.0.0";  CheckCmd = { java -version 2>&1 } },
    @{ Name = "watchman";  MinVersion = "4.9.0";   CheckCmd = { watchman --version } }
)

$Script:RequiredNpmPackages = @(
    "expo-cli", "eas-cli"
)

$Script:RecommendedVSCodeExtensions = @(
    "expo.vscode-expo-tools",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "msjsdiag.vscode-react-native"
)

# ─── Utility Functions ───────────────────────────────────────

function Write-XOSHeader {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   XOS — Experience Engineering OS            ║" -ForegroundColor Cyan
    Write-Host "║   PowerShell Automation Runtime               ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-XOSSuccess([string]$Message) {
    Write-Host "  ✅ $Message" -ForegroundColor Green
}

function Write-XOSWarning([string]$Message) {
    Write-Host "  ⚠️  $Message" -ForegroundColor Yellow
}

function Write-XOSError([string]$Message) {
    Write-Host "  ❌ $Message" -ForegroundColor Red
}

function Write-XOSInfo([string]$Message) {
    Write-Host "  ℹ️  $Message" -ForegroundColor Gray
}

# ─── Health Check ────────────────────────────────────────────

function Invoke-HealthCheck {
    Write-Host "🔍 Running environment health check..." -ForegroundColor Cyan
    Write-Host ""

    $allOk = $true

    foreach ($tool in $Script:RequiredTools) {
        try {
            $output = & $tool.CheckCmd 2>&1 | Out-String
            $version = [regex]::Match($output, '(\d+\.\d+\.\d+)').Value

            if (-not $version) {
                Write-XOSWarning "$($tool.Name): found but could not parse version"
                $allOk = $false
                continue
            }

            $minVersion = [System.Version]::Parse($tool.MinVersion)
            $currentVersion = [System.Version]::Parse($version)

            if ($currentVersion -ge $minVersion) {
                Write-XOSSuccess "$($tool.Name) v$version"
            } else {
                Write-XOSWarning "$($tool.Name) v$version (minimum: $($tool.MinVersion))"
                $allOk = $false
            }
        } catch {
            Write-XOSError "$($tool.Name): not found or not executable"
            $allOk = $false
        }
    }

    # Check Android SDK
    if ($env:ANDROID_HOME) {
        Write-XOSSuccess "ANDROID_HOME = $env:ANDROID_HOME"
    } else {
        Write-XOSWarning "ANDROID_HOME not set"
        $allOk = $false
    }

    # Check Xcode (macOS only)
    if ($IsMacOS) {
        try {
            $xcodeVersion = xcodebuild -version 2>&1 | Select-Object -First 1
            Write-XOSSuccess "Xcode: $xcodeVersion"
        } catch {
            Write-XOSWarning "Xcode not found"
        }
    }

    Write-Host ""
    if ($allOk) {
        Write-Host "✅ Environment is healthy." -ForegroundColor Green
    } else {
        Write-Host "⚠️  Environment has issues. Run 'repair' for guidance." -ForegroundColor Yellow
    }

    return $allOk
}

# ─── Bootstrap ───────────────────────────────────────────────

function Invoke-Bootstrap {
    param([string]$Path)

    Write-Host "🚀 Bootstrapping Expo project at $Path..." -ForegroundColor Cyan
    Write-Host ""

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }

    Push-Location $Path

    try {
        Write-XOSInfo "Creating Expo project with TypeScript..."
        npx create-expo-app@latest . --template blank-typescript -- --no-install

        Write-XOSInfo "Installing core dependencies..."
        pnpm install

        Write-XOSInfo "Installing XOS required packages..."
        pnpm add expo-router react-native-reanimated react-native-gesture-handler `
            react-native-safe-area-context react-native-screens `
            expo-haptics expo-status-bar @react-navigation/native `
            zustand @tanstack/react-query react-hook-form zod nativewind `
            tailwindcss @shopify/flash-list

        Write-XOSInfo "Installing dev dependencies..."
        pnpm add -D @types/react typescript eslint prettier `
            jest @testing-library/react-native detox

        Write-XOSInfo "Installing global tools..."
        foreach ($pkg in $Script:RequiredNpmPackages) {
            npm install -g $pkg 2>&1 | Out-Null
            Write-XOSSuccess "Global: $pkg"
        }

        Write-Host ""
        Write-Host "✅ Project bootstrapped successfully." -ForegroundColor Green
        Write-Host "   Next steps:"
        Write-Host "   1. cd $Path"
        Write-Host "   2. npx expo start"
    } finally {
        Pop-Location
    }
}

# ─── Expo Doctor ─────────────────────────────────────────────

function Invoke-ExpoDoctor {
    Write-Host "🩺 Running Expo doctor..." -ForegroundColor Cyan
    Write-Host ""

    try {
        npx expo-doctor 2>&1
        Write-Host ""
        Write-Host "✅ Expo doctor completed." -ForegroundColor Green
    } catch {
        Write-XOSError "Expo doctor found issues."
        Write-Host "   Run 'repair' for automatic fixes."
    }
}

# ─── Build ───────────────────────────────────────────────────

function Invoke-Build {
    param([string]$Platform, [string]$Path)

    Write-Host "🔨 Building for $Platform..." -ForegroundColor Cyan
    Write-Host ""

    Push-Location $Path
    try {
        if ($Platform -eq "android" -or $Platform -eq "all") {
            Write-XOSInfo "Building Android APK..."
            npx eas build --platform android --profile preview --local
        }
        if ($Platform -eq "ios" -or $Platform -eq "all") {
            Write-XOSInfo "Building iOS..."
            npx eas build --platform ios --profile preview --local
        }
        Write-Host ""
        Write-Host "✅ Build completed." -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

# ─── Clean ───────────────────────────────────────────────────

function Invoke-Clean {
    param([string]$Path)

    Write-Host "🧹 Cleaning project at $Path..." -ForegroundColor Cyan
    Write-Host ""

    Push-Location $Path
    try {
        $dirsToClean = @("node_modules", ".expo", "dist", "android/app/build", "ios/build", "ios/Pods")

        foreach ($dir in $dirsToClean) {
            if (Test-Path $dir) {
                Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
                Write-XOSSuccess "Removed: $dir"
            }
        }

        Write-XOSInfo "Clearing Metro bundler cache..."
        npx expo start --clear 2>&1 | Out-Null

        Write-XOSInfo "Reinstalling dependencies..."
        pnpm install

        Write-Host ""
        Write-Host "✅ Clean completed. Dependencies reinstalled." -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

# ─── Repair ──────────────────────────────────────────────────

function Invoke-Repair {
    Write-Host "🔧 Running auto-repair..." -ForegroundColor Cyan
    Write-Host ""

    $fixes = @()

    # Check Node.js
    try { $nodeV = node --version } catch {
        $fixes += "Install Node.js 20+: https://nodejs.org"
    }

    # Check ANDROID_HOME
    if (-not $env:ANDROID_HOME) {
        $fixes += "Set ANDROID_HOME environment variable to Android SDK location"
        Write-XOSWarning "ANDROID_HOME not set."
        Write-Host "   Set it via: export ANDROID_HOME=~/Android/Sdk" -ForegroundColor Gray
        if ($IsMacOS -or $IsLinux) {
            Write-Host "   Add to ~/.zshrc: export ANDROID_HOME=\$HOME/Android/Sdk" -ForegroundColor Gray
            Write-Host "   Add to ~/.zshrc: export PATH=\$PATH:\$ANDROID_HOME/emulator:\$ANDROID_HOME/platform-tools" -ForegroundColor Gray
        }
    }

    # Check Watchman
    try { watchman version 2>&1 | Out-Null } catch {
        if ($IsMacOS) {
            $fixes += "Install Watchman: brew install watchman"
        } elseif ($IsLinux) {
            $fixes += "Install Watchman: https://facebook.github.io/watchman/docs/install"
        }
    }

    # Clear Metro cache
    if (Test-Path "$env:TEMP/metro-cache") {
        Remove-Item -Recurse -Force "$env:TEMP/metro-cache" -ErrorAction SilentlyContinue
        Write-XOSSuccess "Cleared Metro cache"
    }
    if (Test-Path "$env:TEMP/haste-map-metro-*") {
        Remove-Item -Force "$env:TEMP/haste-map-metro-*" -ErrorAction SilentlyContinue
        Write-XOSSuccess "Cleared Haste map cache"
    }

    # Reset Watchman
    try {
        watchman watch-del-all 2>&1 | Out-Null
        Write-XOSSuccess "Reset Watchman watches"
    } catch {}

    Write-Host ""
    if ($fixes.Count -gt 0) {
        Write-Host "⚠️  Manual fixes needed:" -ForegroundColor Yellow
        foreach ($fix in $fixes) {
            Write-Host "   • $fix" -ForegroundColor Gray
        }
    } else {
        Write-Host "✅ No issues requiring manual repair." -ForegroundColor Green
    }
}

# ─── Deploy ──────────────────────────────────────────────────

function Invoke-Deploy {
    param([string]$Platform, [string]$Path)

    Write-Host "🚀 Deploying to $Platform..." -ForegroundColor Cyan
    Write-Host ""

    Push-Location $Path
    try {
        if ($Platform -eq "all") {
            Write-XOSInfo "Submitting to both stores via EAS..."
            npx eas submit --platform all
        } elseif ($Platform -eq "android") {
            Write-XOSInfo "Submitting to Google Play..."
            npx eas submit --platform android
        } elseif ($Platform -eq "ios") {
            Write-XOSInfo "Submitting to App Store..."
            npx eas submit --platform ios
        }
        Write-Host ""
        Write-Host "✅ Deploy initiated." -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

# ─── Main Dispatch ───────────────────────────────────────────

Write-XOSHeader

switch ($Command) {
    "bootstrap" { Invoke-Bootstrap -Path $ProjectPath }
    "validate"  { $null = Invoke-HealthCheck }
    "doctor"    { Invoke-ExpoDoctor }
    "build"     { Invoke-Build -Platform $Platform -Path $ProjectPath }
    "clean"     { Invoke-Clean -Path $ProjectPath }
    "deploy"    { Invoke-Deploy -Platform $Platform -Path $ProjectPath }
    "health"    { $null = Invoke-HealthCheck }
    "repair"    { Invoke-Repair }
}
