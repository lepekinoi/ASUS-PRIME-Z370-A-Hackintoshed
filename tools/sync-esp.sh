#!/usr/bin/env bash
# usage: ./tools/sync-esp.sh disk0s1   (identifiant via: diskutil list)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DISK="${1:?usage: sync-esp.sh diskXsY}"

git -C "$REPO" pull --ff-only
sudo diskutil mount "$DISK"
MNT="$(diskutil info "$DISK" | awk -F': *' '/Mount Point/{print $2}')"
[ -d "$MNT/EFI" ] || { echo "Pas d'EFI sur $MNT"; exit 1; }

BK="$HOME/EFI-backups/EFI-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BK" && rsync -rt "$MNT/EFI/" "$BK/"
echo "Backup : $BK"

sudo rsync -rt --delete --exclude '.DS_Store' "$REPO/EFI/" "$MNT/EFI/"
sync && sudo diskutil unmount "$DISK"
echo "ESP synchronisee."
