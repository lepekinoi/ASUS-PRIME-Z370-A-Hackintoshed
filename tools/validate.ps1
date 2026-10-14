#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
$root = Resolve-Path "$PSScriptRoot\.."
$cfg  = Join-Path $root 'EFI\OC\config.plist'
$ocv  = Join-Path $PSScriptRoot 'bin\ocvalidate.exe'

if (-not (Test-Path $ocv)) { throw "ocvalidate.exe absent : $ocv (OpenCorePkg-<ver>-RELEASE\Utilities\ocvalidate\)" }

Write-Host "== ocvalidate ==" -ForegroundColor Cyan
& $ocv $cfg
if ($LASTEXITCODE -ne 0) { throw "ocvalidate KO (code $LASTEXITCODE)" }

Write-Host "== AWAC/PMC ==" -ForegroundColor Cyan
$py = @'
import plistlib, sys
p = plistlib.load(open(sys.argv[1], "rb"))
on = [a["Path"] for a in p["ACPI"]["Add"] if a.get("Enabled") and a["Path"] in ("SSDT-AWAC.aml","SSDT-PMC.aml")]
print("Actifs:", on or "aucun")
sys.exit(1 if len(on) > 1 else 0)
'@
$py | python - $cfg
if ($LASTEXITCODE -ne 0) { throw "SSDT-AWAC et SSDT-PMC actives simultanement" }

Write-Host "== PlatformInfo (fuite de serial) ==" -ForegroundColor Cyan
$raw = Get-Content $cfg -Raw
foreach ($k in 'SystemSerialNumber','MLB','SystemUUID') {
  if ($raw -match "<key>$k</key>\s*<string>([^<]+)</string>") {
    $v = $Matches[1]
    if ($v -notmatch '^(0+|X+|[-0]+|placeholder)$') { Write-Warning "$k renseigne ($($v.Substring(0,[Math]::Min(4,$v.Length)))...) : ne pas committer en public" }
  }
}
Write-Host "OK" -ForegroundColor Green
