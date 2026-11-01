#!/usr/bin/env python3
"""Applique le branding local (tools/bin/branding/, gitignore) a un staging, jamais au depot.

  branding_overlay.py <staging>

  tools/bin/branding/EFI/         copie par-dessus <staging>/EFI (theme OpenCanopy, icones)
  tools/bin/branding/config.json  cles du config.plist a forcer, "Section/Sous-section/Cle": valeur
                                  ex. {"Misc/Boot/PickerVariant": "Vendor\\\\Theme"}

Sans tools/bin/branding/ : rien a faire. Une cle absente du config.plist est refusee (faute de frappe),
un PickerVariant force doit exister dans Resources/Image du staging.
"""
import json
import plistlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANDING = Path(__file__).resolve().parent / "bin" / "branding"
CONFIG_REL = Path("EFI") / "OC" / "config.plist"


def main(argv):
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    staging = Path(argv[0]).resolve()
    if staging == ROOT or ROOT in staging.parents:
        raise SystemExit(f"Refus : {staging} est dans le depot. Le branding ne s'applique qu'a un staging.")
    cfg = staging / CONFIG_REL
    if not cfg.is_file():
        raise SystemExit(f"config.plist absent : {cfg}")
    if not BRANDING.is_dir():
        print(f"Pas de branding local ({BRANDING}), EFI du depot inchangee")
        return 0

    overlay = BRANDING / "EFI"
    if overlay.is_dir():
        shutil.copytree(overlay, staging / "EFI", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".DS_Store", "._*"))
        print(f"Fichiers : {sum(1 for f in overlay.rglob('*') if f.is_file())} copies depuis {overlay}")

    overrides = BRANDING / "config.json"
    if not overrides.is_file():
        return 0
    with open(overrides, encoding="utf-8") as f:
        keys = json.load(f)
    with open(cfg, "rb") as f:
        plist = plistlib.load(f)

    for key, value in keys.items():
        if not isinstance(value, (str, int, bool)):
            raise SystemExit(f"{key} : seules les valeurs texte, entieres ou booleennes sont gerees")
        *parents, last = key.split("/")
        node = plist
        for part in parents:
            node = node.get(part) if isinstance(node, dict) else None
        if not isinstance(node, dict) or last not in node:
            raise SystemExit(f"Cle absente du config.plist : {key}")
        if type(node[last]) is not type(value):
            raise SystemExit(f"{key} : type {type(value).__name__} au lieu de {type(node[last]).__name__}")
        node[last] = value
        print(f"{key} = {value}")

    variant = plist["Misc"]["Boot"]["PickerVariant"]
    if variant not in ("Auto", "Default"):
        theme = staging / "EFI" / "OC" / "Resources" / "Image" / Path(*variant.split("\\"))
        if not (theme / "HardDrive.icns").is_file() or not (theme / "ExtHardDrive.icns").is_file():
            raise SystemExit(f"Theme {variant} incomplet ou absent : {theme}")

    with open(cfg, "wb") as f:
        plistlib.dump(plist, f, sort_keys=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
