<#
.SYNOPSIS
  Bootstrap a new Expo project with all XOS-mandated dependencies.
.DESCRIPTION
  Creates an Expo (SDK 52+) project, installs NativeWind, Reanimated,
  Gesture Handler, React Query, Zustand, RHF + Zod, MMKV, FlashList, Skia,
  and configures pnpm.  Validates the environment before creating anything.
#>

param(
  [string]$ProjectName = "xos-app",
  [string]$RootPath   = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$projectDir = Join-Path $RootPath $ProjectName

Write-Host "==> XOS Bootstrap: $ProjectName" -ForegroundColor Cyan

# ── Environment validation ──────────────────────────────────────────
$required = @("node", "pnpm", "npx")
foreach ($cmd in $required) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing required tool: $cmd"
  }
}
Write-Host "  ✓ Required tools present: $($required -join ', ')" -ForegroundColor Green

# ── Create Expo project via create-expo-app ─────────────────────────
Write-Host "  Creating Expo project ..." -ForegroundColor Gray
& npx create-expo-app@latest $ProjectName --template blank-typescript 2>&1 | Out-Null
Set-Location $projectDir

# ── Install core packages ──────────────────────────────────────────
Write-Host "  Installing XOS dependencies ..." -ForegroundColor Gray

pnpm add nativewind@4 tailwindcss@4 react-native-reanimated react-native-gesture-handler `
  @tanstack/react-query zustand react-hook-form zod react-native-mmkv `
  @shopify/flash-list @shopify/react-native-skia @react-navigation/native `
  @react-navigation/native-stack expo-router expo-haptics

pnpm add -D @types/react-native

# ── Configure NativeWind ───────────────────────────────────────────
$metroConfigPath = Join-Path $projectDir "metro.config.js"
if (Test-Path $metroConfigPath) {
  Write-Host "  Configuring NativeWind in metro.config.js ..." -ForegroundColor Gray
  $metroContent = @"
const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);
module.exports = withNativeWind(config, { input: "./global.css" });
"@
  Set-Content -Path $metroConfigPath -Value $metroContent
}

# Create global.css for NativeWind
Set-Content -Path (Join-Path $projectDir "global.css") -Value @"
@tailwind base;
@tailwind components;
@tailwind utilities;
"@

Write-Host "  ✓ Bootstrap complete: $projectDir" -ForegroundColor Green
