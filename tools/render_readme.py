#!/usr/bin/env python3
"""Genere README.md depuis README.template.md et l'etat reel de l'EFI.

  render_readme.py          ecrit README.md
  render_readme.py --check  echoue si README.md n'est pas a jour

Marqueurs remplaces : {{KEXT_TABLE}}, {{SSDT_TABLE}}, {{BOOT_ARGS}}, {{SMBIOS}}
"""
import plistlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OC = ROOT / "EFI" / "OC"
TEMPLATE = ROOT / "README.template.md"
README = ROOT / "README.md"

KEXT_ROLES = {
    "Lilu.kext": "Patching engine, required by every plugin below",
    "AppleALC.kext": "ALC1220S layout `7`, no effect on Tahoe without AppleHDA",
    "VirtualSMC.kext": "SMC emulation",
    "IntelMausi.kext": "Intel I219-V Ethernet",
    "WhateverGreen.kext": "GPU patches, not needed for the Vega 64 on Tahoe",
    "RestrictEvents.kext": "Keeps OTA updates working with MacPro7,1 (`revpatch=sbvmm`)",
    "NVMeFix.kext": "NVMe power management, optional (this build runs on SATA)",
    "USBToolBox.kext": "USB mapping driver",
    "UTBMap.kext": "USB port map for this board",
    "SMCProcessor.kext": "CPU temperature sensors",
    "SMCSuperIO.kext": "Fan speed sensors",
}

SSDT_ROLES = {
    "SSDT-PLUG-DRTNIA.aml": "CPU power management (`plugin-type`)",
    "SSDT-EC-USBX-DESKTOP.aml": "Fake Embedded Controller + USB power",
    "SSDT-AWAC.aml": "Brings back the legacy RTC clock on Z370",
    "SSDT-PMC.aml": "Alternative to SSDT-AWAC, mutually exclusive",
}


def state(enabled):
    return "✅ Enabled" if enabled else "⚪ Disabled"


def kext_table(cfg):
    rows = ["| Kext | Version | State | Role |", "|---|---|---|---|"]
    for k in cfg["Kernel"]["Add"]:
        name = k["BundlePath"]
        info = OC / "Kexts" / name / "Contents" / "Info.plist"
        with open(info, "rb") as f:
            ver = plistlib.load(f).get("CFBundleVersion", "?")
        rows.append(f"| `{name}` | `{ver}` | {state(k['Enabled'])} | {KEXT_ROLES.get(name, '')} |")
    return "\n".join(rows)


def ssdt_table(cfg):
    rows = ["| SSDT | State | Role |", "|---|---|---|"]
    for a in cfg["ACPI"]["Add"]:
        name = a["Path"]
        rows.append(f"| `{name}` | {state(a['Enabled'])} | {SSDT_ROLES.get(name, '')} |")
    return "\n".join(rows)


def render():
    with open(OC / "config.plist", "rb") as f:
        cfg = plistlib.load(f)
    nv = cfg["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]
    values = {
        "{{KEXT_TABLE}}": kext_table(cfg),
        "{{SSDT_TABLE}}": ssdt_table(cfg),
        "{{BOOT_ARGS}}": nv["boot-args"],
        "{{SMBIOS}}": cfg["PlatformInfo"]["Generic"]["SystemProductName"],
    }
    out = TEMPLATE.read_text(encoding="utf-8")
    for k, v in values.items():
        out = out.replace(k, v)
    return out


def main(argv):
    out = render()
    if argv == ["--check"]:
        if not README.is_file() or README.read_text(encoding="utf-8") != out:
            print("README.md pas a jour : lancer python3 tools/render_readme.py", file=sys.stderr)
            return 1
        print("README.md a jour")
        return 0
    if argv:
        print(__doc__, file=sys.stderr)
        return 2
    README.write_text(out, encoding="utf-8")
    print(f"{README} genere")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
