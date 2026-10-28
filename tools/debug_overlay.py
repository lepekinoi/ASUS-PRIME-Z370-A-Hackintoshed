#!/usr/bin/env python3
"""Ajoute les reglages de debug a un config.plist de staging, jamais a celui du depot.

  debug_overlay.py <config.plist>

  boot-args  : ajoute -v (verbose) et debug=0x100 (pas de reboot sur panique), sans doublon
  Misc/Debug : Target=67 (log OpenCore en fichier a la racine de l'ESP + a l'ecran),
               AppleDebug, ApplePanic (panique sauvee en panic-*.txt), DisableWatchDog
"""
import plistlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NVRAM_GUID = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
BOOT_ARGS = ["-v", "debug=0x100"]
DEBUG = {"Target": 67, "AppleDebug": True, "ApplePanic": True, "DisableWatchDog": True}


def main(argv):
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    cfg = Path(argv[0]).resolve()
    if cfg == ROOT or ROOT in cfg.parents:
        raise SystemExit(f"Refus : {cfg} est dans le depot. L'overlay ne s'applique qu'a un staging ou a la cle.")
    if not cfg.is_file():
        raise SystemExit(f"config.plist absent : {cfg}")

    with open(cfg, "rb") as f:
        plist = plistlib.load(f)

    nv = plist["NVRAM"]["Add"][NVRAM_GUID]
    args = nv.get("boot-args", "").split()
    args += [a for a in BOOT_ARGS if a not in args]
    nv["boot-args"] = " ".join(args)

    dbg = plist["Misc"]["Debug"]
    for k, v in DEBUG.items():
        dbg[k] = v

    with open(cfg, "wb") as f:
        plistlib.dump(plist, f, sort_keys=False)

    print(f"boot-args  : {nv['boot-args']}")
    print("Misc/Debug : " + ", ".join(f"{k}={dbg[k]}" for k in DEBUG))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
