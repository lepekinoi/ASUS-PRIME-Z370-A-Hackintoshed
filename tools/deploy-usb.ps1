#Requires -RunAsAdministrator
param(
  [Parameter(Mandatory)][ValidatePattern('^[A-Za-z]$')][string]$Drive,
  [switch]$AllowNonUsb
)
$ErrorActionPreference = 'Stop'
$ocv = Join-Path $PSScriptRoot 'bin\ocvalidate.exe'

$vol  = Get-Volume -DriveLetter $Drive
$part = Get-Partition -DriveLetter $Drive
$disk = Get-Disk -Number $part.DiskNumber
if ($vol.FileSystem -notin 'FAT32','FAT')           { throw "$Drive`: n'est pas en FAT32 ($($vol.FileSystem))" }
if ($disk.IsBoot -or $disk.IsSystem)                { throw "$Drive`: est sur le disque systeme Windows, refus." }
if ($disk.BusType -ne 'USB' -and -not $AllowNonUsb) { throw "BusType=$($disk.BusType), pas USB. -AllowNonUsb pour forcer." }

# 1. Le depot doit etre valide et sans valeur PlatformInfo reelle
& "$PSScriptRoot\validate.ps1"

# 2. Injection des vraies valeurs (tools/bin/platforminfo.local.json) dans un staging hors depot
$staging = Join-Path $env:TEMP ("oc-staging-" + (Get-Date -Format yyyyMMdd-HHmmss))
try {
  Write-Host "== Injection PlatformInfo -> $staging ==" -ForegroundColor Cyan
  python "$PSScriptRoot\inject_platforminfo.py" inject $staging
  if ($LASTEXITCODE -ne 0) { throw "Injection PlatformInfo KO (code $LASTEXITCODE)" }

  Write-Host "== ocvalidate (config injecte) ==" -ForegroundColor Cyan
  & $ocv (Join-Path $staging 'EFI\OC\config.plist')
  if ($LASTEXITCODE -ne 0) { throw "ocvalidate KO sur le config injecte (code $LASTEXITCODE)" }

  # 3. Sauvegarde de l'EFI existante puis deploiement depuis le staging
  $dst = "${Drive}:\EFI"
  if (Test-Path $dst) {
    $bk = Join-Path $env:USERPROFILE ("EFI-backups\EFI-" + (Get-Date -Format yyyyMMdd-HHmmss))
    robocopy $dst $bk /E /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
    Write-Host "Backup : $bk"
  }
  robocopy (Join-Path $staging 'EFI') $dst /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS
  if ($LASTEXITCODE -ge 8) { throw "robocopy erreur $LASTEXITCODE" }
  Write-Host "EFI deployee sur $dst" -ForegroundColor Green
}
finally {
  if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
}
