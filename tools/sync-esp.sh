#!/usr/bin/env bash
# usage: ./tools/sync-esp.sh [--debug-boot] disk0s1   (identifiant via: diskutil list)
# Meme chaine que deploy-usb.ps1 : validation, injection PlatformInfo dans un staging
# hors depot, overlay debug optionnel, ocvalidate du config injecte, backup, copie.
set -euo pipefail
TOOLS="$(cd "$(dirname "$0")" && pwd)"

DEBUG_BOOT=0
if [ "${1:-}" = "--debug-boot" ]; then DEBUG_BOOT=1; shift; fi
DISK="${1:?usage: sync-esp.sh [--debug-boot] diskXsY}"

# 1. Le depot doit etre valide et sans valeur PlatformInfo reelle
"$TOOLS/validate.sh"

# 2. Injection des vraies valeurs (tools/bin/platforminfo.local.json) dans un staging hors depot
STAGING="$(mktemp -d "${TMPDIR:-/tmp}/oc-staging-XXXXXX")"
trap 'rm -rf "$STAGING"' EXIT
echo "== Injection PlatformInfo -> $STAGING =="
python3 -I "$TOOLS/inject_platforminfo.py" inject "$STAGING"

# 2b. Option --debug-boot : verbose + logs OpenCore, applique au staging uniquement
if [ "$DEBUG_BOOT" = 1 ]; then
  echo "== Overlay debug (verbose + logs) =="
  python3 -I "$TOOLS/debug_overlay.py" "$STAGING/EFI/OC/config.plist"
fi

echo "== ocvalidate (config injecte) =="
"$TOOLS/bin/ocvalidate" "$STAGING/EFI/OC/config.plist"

# 3. Sauvegarde de l'EFI existante puis deploiement depuis le staging
sudo diskutil mount "$DISK"
MNT="$(diskutil info "$DISK" | awk -F': *' '/Mount Point/{print $2}')"
[ -d "$MNT/EFI" ] || { echo "Pas d'EFI sur $MNT"; exit 1; }

BK="$HOME/EFI-backups/EFI-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BK" && rsync -rt "$MNT/EFI/" "$BK/"
echo "Backup : $BK"

sudo rsync -rt --delete --exclude '.DS_Store' --exclude '._*' "$STAGING/EFI/" "$MNT/EFI/"
sync && sudo diskutil unmount "$DISK"
echo "ESP synchronisee."
