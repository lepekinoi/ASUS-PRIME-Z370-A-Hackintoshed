#Requires -RunAsAdministrator
param(
  [Parameter(Mandatory)][ValidatePattern('^[A-Za-z]$')][string]$Drive,
  [switch]$AllowNonUsb
)
$ErrorActionPreference = 'Stop'
$repoEfi = Resolve-Path "$PSScriptRoot\..\EFI"

$vol  = Get-Volume -DriveLetter $Drive
$part = Get-Partition -DriveLetter $Drive
$disk = Get-Disk -Number $part.DiskNumber
if ($vol.FileSystem -notin 'FAT32','FAT')           { throw "$Drive`: n'est pas en FAT32 ($($vol.FileSystem))" }
if ($disk.IsBoot -or $disk.IsSystem)                { throw "$Drive`: est sur le disque systeme Windows, refus." }
if ($disk.BusType -ne 'USB' -and -not $AllowNonUsb) { throw "BusType=$($disk.BusType), pas USB. -AllowNonUsb pour forcer." }

& "$PSScriptRoot\validate.ps1"

$dst = "${Drive}:\EFI"
if (Test-Path $dst) {
  $bk = Join-Path $env:USERPROFILE ("EFI-backups\EFI-" + (Get-Date -Format yyyyMMdd-HHmmss))
  robocopy $dst $bk /E /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
  Write-Host "Backup : $bk"
}
robocopy $repoEfi $dst /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS
if ($LASTEXITCODE -ge 8) { throw "robocopy erreur $LASTEXITCODE" }
Write-Host "EFI deployee sur $dst" -ForegroundColor Green
