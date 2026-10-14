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

Write-Host "== PlatformInfo (placeholders uniquement) ==" -ForegroundColor Cyan
python "$PSScriptRoot\inject_platforminfo.py" check
if ($LASTEXITCODE -ne 0) { throw "Valeur PlatformInfo reelle dans le depot : interdit (repo public). Lancer : python tools/inject_platforminfo.py sanitize" }
Write-Host "OK" -ForegroundColor Green
