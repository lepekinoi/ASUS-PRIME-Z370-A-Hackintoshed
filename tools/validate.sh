#!/usr/bin/env bash
# usage: ./tools/validate.sh [config.plist]   (equivalent macOS de validate.ps1)
set -euo pipefail
TOOLS="$(cd "$(dirname "$0")" && pwd)"
CFG="${1:-$TOOLS/../EFI/OC/config.plist}"
OCV="$TOOLS/bin/ocvalidate"

[ -x "$OCV" ] || { echo "ocvalidate absent : $OCV (OpenCorePkg-<ver>-RELEASE/Utilities/ocvalidate/)"; exit 1; }

echo "== ocvalidate =="
"$OCV" "$CFG" || { echo "ocvalidate KO"; exit 1; }

echo "== AWAC/PMC =="
python3 -I - "$CFG" <<'EOF' || { echo "SSDT-AWAC et SSDT-PMC actives simultanement"; exit 1; }
import plistlib, sys
p = plistlib.load(open(sys.argv[1], "rb"))
on = [a["Path"] for a in p["ACPI"]["Add"] if a.get("Enabled") and a["Path"] in ("SSDT-AWAC.aml","SSDT-PMC.aml")]
print("Actifs:", on or "aucun")
sys.exit(1 if len(on) > 1 else 0)
EOF

echo "== PlatformInfo (placeholders uniquement) =="
python3 -I "$TOOLS/inject_platforminfo.py" check \
  || { echo "Valeur PlatformInfo reelle dans le depot : interdit (repo public). Lancer : python3 tools/inject_platforminfo.py sanitize"; exit 1; }
echo "OK"
