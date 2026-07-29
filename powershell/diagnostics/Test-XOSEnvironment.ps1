<#
.SYNOPSIS
  XOS Environment Diagnostics — validate the local machine for Expo development.
#>

Write-Host "==> XOS Environment Diagnostics" -ForegroundColor Cyan

$checks = @()

# Node
$nodeVersion = try { & node --version 2>$null } catch { $null }
$checks += [PSCustomObject]@{ Tool="Node.js"; Installed=[bool]$nodeVersion; Version=$nodeVersion; Status=if($nodeVersion){ "OK" }else{ "FAIL" } }

# pnpm
$pnpmVersion = try { & pnpm --version 2>$null } catch { $null }
$checks += [PSCustomObject]@{ Tool="pnpm"; Installed=[bool]$pnpmVersion; Version=$pnpmVersion; Status=if($pnpmVersion){ "OK" }else{ "FAIL" } }

# npx
$npxOk = [bool](Get-Command npx -ErrorAction SilentlyContinue)
$checks += [PSCustomObject]@{ Tool="npx"; Installed=$npxOk; Version="-"; Status=if($npxOk){ "OK" }else{ "FAIL" } }

# Expo CLI
$expoVersion = try { & npx expo --version 2>$null } catch { $null }
$checks += [PSCustomObject]@{ Tool="Expo CLI"; Installed=[bool]$expoVersion; Version=$expoVersion; Status=if($expoVersion){ "OK" }else{ "WARN" } }

# Java / Android SDK
$javaHome = $env:JAVA_HOME
$androidHome = $env:ANDROID_HOME
$checks += [PSCustomObject]@{ Tool="JAVA_HOME"; Installed=[bool]$javaHome; Version=$javaHome; Status=if($javaHome){ "OK" }else{ "WARN" } }
$checks += [PSCustomObject]@{ Tool="ANDROID_HOME"; Installed=[bool]$androidHome; Version=$androidHome; Status=if($androidHome){ "OK" }else{ "WARN" } }

# Xcode (macOS only)
if ($IsMacOS) {
  $xcodeVersion = try { & xcodebuild -version 2>$null | Select-Object -First 1 } catch { $null }
  $checks += [PSCustomObject]@{ Tool="Xcode"; Installed=[bool]$xcodeVersion; Version=$xcodeVersion; Status=if($xcodeVersion){ "OK" }else{ "FAIL" } }
}

# Git
$gitVersion = try { & git --version 2>$null } catch { $null }
$checks += [PSCustomObject]@{ Tool="Git"; Installed=[bool]$gitVersion; Version=$gitVersion; Status=if($gitVersion){ "OK" }else{ "FAIL" } }

# Python
$pyVersion = try { & python3 --version 2>$null } catch { $null }
$checks += [PSCustomObject]@{ Tool="Python"; Installed=[bool]$pyVersion; Version=$pyVersion; Status=if($pyVersion){ "OK" }else{ "WARN" } }

$checks | Format-Table -AutoSize

$failCount = ($checks | Where-Object { $_.Status -eq "FAIL" }).Count
$warnCount = ($checks | Where-Object { $_.Status -eq "WARN" }).Count

Write-Host "`nSummary: $($checks.Count) checks — $failCount failures, $warnCount warnings" -ForegroundColor $(if($failCount -gt 0){"Red"}else{"Green"})
