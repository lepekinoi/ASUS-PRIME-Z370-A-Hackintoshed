#!/usr/bin/env python3
"""Gestion des valeurs PlatformInfo reelles, hors du depot public.

Les vraies valeurs vivent dans tools/bin/platforminfo.local.json (gitignore).
Le config.plist du depot ne contient que des placeholders.

  inject <staging>  copie EFI/ dans <staging>/EFI et y injecte les vraies valeurs
  check             echoue si une valeur reelle est presente dans le depot
  sanitize          remplace les valeurs du depot par des placeholders
  export            ecrit les valeurs actuelles du depot dans le JSON (sans les afficher)
"""
import json
import plistlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EFI_DIR = ROOT / "EFI"
CONFIG_REL = Path("OC") / "config.plist"
SECRETS = Path(__file__).resolve().parent / "bin" / "platforminfo.local.json"

KEYS = [
    "PlatformInfo/Generic/SystemSerialNumber",
    "PlatformInfo/Generic/MLB",
    "PlatformInfo/Generic/SystemUUID",
    "PlatformInfo/Generic/ROM",
    "PlatformInfo/SMBIOS/SystemSerialNumber",
    "PlatformInfo/SMBIOS/BoardSerialNumber",
    "PlatformInfo/SMBIOS/ChassisSerialNumber",
    "PlatformInfo/SMBIOS/SystemUUID",
    "PlatformInfo/DataHub/SystemSerialNumber",
    "PlatformInfo/DataHub/SystemUUID",
    "PlatformInfo/PlatformNVRAM/SystemSerialNumber",
    "PlatformInfo/PlatformNVRAM/MLB",
    "PlatformInfo/PlatformNVRAM/SystemUUID",
    "PlatformInfo/PlatformNVRAM/ROM",
]

PLACEHOLDERS = {
    "SystemSerialNumber": "X" * 12,
    "BoardSerialNumber": "X" * 12,
    "ChassisSerialNumber": "X" * 12,
    "MLB": "X" * 17,
    "SystemUUID": "00000000-0000-0000-0000-000000000000",
    "ROM": bytes(6),
}


def leaf(key):
    return key.rsplit("/", 1)[1]


def get(plist, key):
    node = plist
    for part in key.split("/"):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(key)
        node = node[part]
    return node


def put(plist, key, value):
    *parents, last = key.split("/")
    node = plist
    for part in parents:
        node = node[part]
    node[last] = value


def is_placeholder(key, value):
    ph = PLACEHOLDERS[leaf(key)]
    if isinstance(ph, bytes):
        return value == ph
    return value == ph or not value or set(value) <= set("X0-")


def to_json(key, value):
    return value.hex().upper() if leaf(key) == "ROM" else value


def from_json(key, value):
    if leaf(key) == "ROM":
        raw = bytes.fromhex(value)
        if len(raw) != 6:
            raise ValueError(f"{key}: ROM doit faire 6 octets")
        return raw
    if not isinstance(value, str):
        raise ValueError(f"{key}: chaine attendue")
    return value


def load(path):
    with open(path, "rb") as f:
        return plistlib.load(f)


def dump(plist, path):
    with open(path, "wb") as f:
        plistlib.dump(plist, f, sort_keys=False)


def cmd_check(config):
    plist = load(config)
    bad = [k for k in KEYS if not is_placeholder(k, get(plist, k))]
    if bad:
        print("Valeurs PlatformInfo reelles dans le depot :", file=sys.stderr)
        for k in bad:
            print(f"  {k}", file=sys.stderr)
        return 1
    print(f"PlatformInfo : {len(KEYS)} cles en placeholder")
    return 0


def cmd_sanitize(config):
    plist = load(config)
    for k in KEYS:
        get(plist, k)
        put(plist, k, PLACEHOLDERS[leaf(k)])
    dump(plist, config)
    print(f"{config} : {len(KEYS)} cles remplacees par des placeholders")
    return 0


def cmd_export(config):
    plist = load(config)
    data = {k: to_json(k, get(plist, k)) for k in KEYS}
    SECRETS.parent.mkdir(parents=True, exist_ok=True)
    with open(SECRETS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"{SECRETS} : {len(data)} cles ecrites")
    return 0


def cmd_inject(config, staging):
    if not SECRETS.is_file():
        raise SystemExit(f"JSON absent : {SECRETS}")
    with open(SECRETS, encoding="utf-8") as f:
        secrets = json.load(f)
    missing = [k for k in KEYS if k not in secrets]
    if missing:
        raise SystemExit("Cles manquantes dans le JSON : " + ", ".join(missing))
    values = {k: from_json(k, secrets[k]) for k in KEYS}
    still = [k for k, v in values.items() if is_placeholder(k, v)]
    if still:
        raise SystemExit("Valeurs placeholder dans le JSON : " + ", ".join(still))

    staging = Path(staging).resolve()
    if staging == ROOT or ROOT in staging.parents:
        raise SystemExit(f"Le staging doit etre hors du depot : {staging}")
    dst_efi = staging / "EFI"
    if dst_efi.exists():
        shutil.rmtree(dst_efi)
    shutil.copytree(EFI_DIR, dst_efi)

    out = dst_efi / CONFIG_REL
    plist = load(out)
    for k, v in values.items():
        get(plist, k)
        put(plist, k, v)
    dump(plist, out)

    plist = load(out)
    leftover = [k for k in KEYS if is_placeholder(k, get(plist, k))]
    if leftover:
        raise SystemExit("Placeholders restants apres injection : " + ", ".join(leftover))
    print(f"EFI injectee dans {dst_efi} ({len(KEYS)} cles)")
    return 0


def main(argv):
    config = EFI_DIR / CONFIG_REL
    if len(argv) == 1 and argv[0] in ("check", "sanitize", "export"):
        return {"check": cmd_check, "sanitize": cmd_sanitize, "export": cmd_export}[argv[0]](config)
    if len(argv) == 2 and argv[0] == "inject":
        return cmd_inject(config, argv[1])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
