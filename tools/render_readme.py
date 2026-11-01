#!/usr/bin/env python3
"""Genere README.md depuis README.template.md et l'etat reel de l'EFI.

  render_readme.py          ecrit README.md
  render_readme.py --check  echoue si README.md n'est pas a jour

Marqueurs remplaces : {{KEXT_TABLE}}, {{SSDT_TABLE}}, {{BOOT_ARGS}}, {{SMBIOS}}, {{USB_TABLE}}
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
    "VirtualSMC.kext": "SMC emulation",
    "IntelMausi.kext": "Intel I219-V Ethernet",
    "RestrictEvents.kext": "Keeps OTA updates working with MacPro7,1 (`revpatch=sbvmm`)",
    "AppleALC.kext": "Realtek ALC1220 onboard audio (`layout-id` 7)",
    "SimpleHDA.kext": "Restores Apple's AppleHDA on Tahoe so AppleALC works again",
    "NVMeFix.kext": "NVMe power management (APST) for the WD_BLACK SN850X",
    "USBToolBox.kext": "USB mapping driver",
    "UTBMap.kext": "USB port map for this build (3 controllers, see [USB map](#usb-map))",
    "SMCProcessor.kext": "CPU temperature sensors",
    "SMCSuperIO.kext": "Fan speed sensors",
}

SSDT_ROLES = {
    "SSDT-PLUG-DRTNIA.aml": "CPU power management (`plugin-type`)",
    "SSDT-EC-USBX-DESKTOP.aml": "Fake Embedded Controller + USB power",
    "SSDT-AWAC.aml": "Brings back the legacy RTC clock on Z370",
}

# Cles des personnalites UTBMap.kext -> controleur physique
USB_CONTROLLERS = {
    "XHC": "Intel Z370 (PCH)",
    "_SB.PCI0.RP05.PXSX": "ASMedia ASM2142 (onboard)",
    "_SB.PCI0.RP21.PXSX": "ASMedia ASM1242 (PCIe card)",
}

USB_CONNECTORS = {
    0: "USB 2 Type-A",
    3: "USB 3 Type-A",
    9: "USB-C (with switch)",
    10: "USB-C (without switch)",
    255: "Internal",
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


def usb_table():
    """Une ligne par prise physique : les ports HS/SS d'une meme prise partagent leur #comment."""
    info = OC / "Kexts" / "UTBMap.kext" / "Contents" / "Info.plist"
    with open(info, "rb") as f:
        personalities = plistlib.load(f)["IOKitPersonalities"]
    rows = ["| Port | Controller | Connector | USB 2 | USB 3 |", "|---|---|---|---|---|"]
    total = 0
    for key, pers in personalities.items():
        match = pers.get("IOPropertyMatch", {}).get("pcidebug")
        ctrl = USB_CONTROLLERS.get(key, key) + (f" `{match}`" if match else "")
        sockets = {}
        for name, p in pers["IOProviderMergeProperties"]["ports"].items():
            total += 1
            s = sockets.setdefault(p.get("#comment", name), {"type": p["UsbConnector"]})
            s["SS" if name.startswith("SS") else "HS"] = f"`{name}`"
        for label, s in sockets.items():
            rows.append(f"| {label} | {ctrl} | {USB_CONNECTORS.get(s['type'], s['type'])} "
                        f"| {s.get('HS', '')} | {s.get('SS', '')} |")
    return "\n".join(rows) + f"\n\n{total} ports mapped, at most 15 per controller."


def render():
    with open(OC / "config.plist", "rb") as f:
        cfg = plistlib.load(f)
    nv = cfg["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]
    values = {
        "{{KEXT_TABLE}}": kext_table(cfg),
        "{{SSDT_TABLE}}": ssdt_table(cfg),
        "{{BOOT_ARGS}}": nv["boot-args"],
        "{{SMBIOS}}": cfg["PlatformInfo"]["Generic"]["SystemProductName"],
        "{{USB_TABLE}}": usb_table(),
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
