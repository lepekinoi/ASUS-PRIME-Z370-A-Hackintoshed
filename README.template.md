# 🍏 ASUS PRIME Z370-A Hackintosh (OpenCore)

A fully working OpenCore build for the **ASUS PRIME Z370-A** paired with an **Intel i7-9700**, **Gigabyte Vega 64**, and **ALC1220S audio**. No Wi-Fi/Bluetooth card. 🚀

## 📦 Current EFI Versions (Auto-Updated)
- **OpenCore:** {{OC_VERSION}}
- **Lilu:** {{LILU_VERSION}}
- **WhateverGreen:** {{WEG_VERSION}}
- **AppleALC:** {{ALC_VERSION}}

---

## 💻 Hardware Configuration

| Component | Model | Status/Notes |
|---|---|---|
| **Motherboard** | ASUS PRIME Z370-A | Working perfectly |
| **CPU** | Intel Core i7-9700 (Coffee Lake) | Native Power Management |
| **GPU** | Gigabyte RX Vega 64 8GB | Native support (OOB) |
| **Audio** | Realtek ALC1220S | `layout-id=7` |
| **Storage** | WD Black SN850X NVMe | Fully compatible |
| **Wi-Fi / Bluetooth** | None | No wireless card installed; this EFI ships no Wi-Fi/BT kexts |

## 🎭 SMBIOS: `MacPro7,1`

This EFI uses **`MacPro7,1`** with `PlatformInfo → Automatic = YES` (only the `Generic` section is filled). It is a dGPU-only model: the iGPU **must be disabled** in the BIOS, and the Vega 64 gets full acceleration plus native DRM (Apple TV+, Netflix in Safari, Prime Video).

- `MacPro7,1` is not in the Coffee Lake support list, so OTA updates are kept working with **RestrictEvents.kext** + the `revpatch=sbvmm` boot-arg. Do not remove either.
- The CPU shows as **Intel Xeon** in "About This Mac" — expected, no performance impact.
- The committed `config.plist` only contains placeholder serials (`XXXX…`, zero UUID/ROM). Generate your own with GenSMBIOS and keep them out of any public repo (see `tools/inject_platforminfo.py`).

---

## ⚙️ BIOS Settings (Crucial for Coffee Lake)

> Start by loading **Optimized Defaults** (`F5`) before applying the settings below.

### Quick Reference Table

| Action | Setting | BIOS Path |
|---|---|---|
| 🔴 Disable | Fast Boot | Boot |
| 🔴 Disable | Secure Boot | Boot → Secure Boot |
| 🔴 Disable | CSM | Boot → CSM |
| 🔴 Disable | **CFG Lock** (MSR 0xE2) | Advanced → CPU Power Management |
| 🔴 Disable | VT-d | Advanced → System Agent (SA) Config |
| 🔴 Disable | Intel SGX | Advanced → CPU Configuration |
| 🔴 Disable | Intel Platform Trust (PTT/TPM) | Advanced → PCH-FW Configuration |
| 🔴 Disable | Serial / COM Port | Advanced → Onboard Devices |
| 🔴 Disable | **iGPU (Intel UHD 630)** ⚠️ | Advanced → SA Config → Graphics Config |
| 🟢 Enable | VT-x | Advanced → CPU Configuration |
| 🟢 Enable | Hyper-Threading | Advanced → CPU Configuration |
| 🟢 Enable | Execute Disable Bit | Advanced → CPU Configuration |
| 🟢 Enable | **Above 4G Decoding** | Advanced → System Agent (SA) Config |
| 🟢 Enable | XHCI / EHCI Hand-off | Advanced → USB Configuration |
| 🔵 Set | SATA Mode → **AHCI** | Advanced → PCH Storage Configuration |
| 🔵 Set | DVMT Pre-Allocated → **64 MB** | Advanced → SA Config → Graphics Config |
| 🔵 Set | OS Type → **Windows 8.1/10 UEFI Mode** | Boot → Secure Boot |

### ❌ Disable — Details

- **Fast Boot** — Can prevent OpenCore bootloader from loading correctly.
- **Secure Boot** — Incompatible with OpenCore; must be off.
- **CSM (Compatibility Support Module)** — Must be OFF for pure UEFI mode; active CSM causes `gIO` errors at OpenCore boot.
- **CFG Lock (MSR 0xE2)** ⚠️ **CRITICAL** — macOS cannot boot with this locked. If not visible in BIOS, enable `AppleCpuPmCfgLock` + `AppleXcpmCfgLock` in `config.plist → Kernel → Quirks`.
- **VT-d** — Can disrupt macOS IOMMU. It is disabled in BIOS here, so `DisableIoMapper` stays `NO`; set it to `YES` only if you keep VT-d enabled.
- **Intel SGX** — Unused, may cause instability.
- **Intel Platform Trust (PTT/TPM)** — Not needed under macOS.
- **Serial / COM Port** — Can conflict with ACPI SSDTs.
- **iGPU (Intel UHD 630)** ⚠️ **REQUIRED with MacPro7,1** — The `MacPro7,1` SMBIOS has no iGPU in the Apple model. Leaving it enabled will cause kernel panics. The Vega 64 handles all rendering.

### ✅ Enable — Details

- **VT-x** — Required for OpenCore Kernel Quirks and macOS virtualization.
- **Hyper-Threading** — Used natively by the macOS scheduler; improves multi-core performance.
- **Execute Disable Bit** — Required for macOS memory security.
- **Above 4G Decoding** — Mandatory for the RX Vega 64 (large GPU BAR).
- **XHCI / EHCI Hand-off** — Essential for native macOS USB controller management without kernel panics.

### 🔵 Set Values

- **SATA Mode: AHCI** — RAID mode is not recognized by macOS.
- **DVMT Pre-Allocated: 64 MB** — Minimum recommended (leave at 64 MB even with iGPU disabled).
- **OS Type: Windows 8.1/10 UEFI Mode** — Required for UEFI Secure Boot screen to remain compatible.

---

## 🧩 OpenCore Kernel Quirks (config.plist)

Values below are the ones actually set in this repository's `config.plist`.

| Quirk | Value | Notes |
|---|---|---|
| `AppleCpuPmCfgLock` | `NO` | Legacy (non-XCPM) path, not used on Coffee Lake; CFG Lock is unlocked in BIOS |
| `AppleXcpmCfgLock` | `YES` | Kept on purpose as a safety net for XCPM if MSR 0xE2 ever ends up locked |
| `DisableIoMapper` | `NO` | VT-d is disabled in BIOS, so the IOMMU workaround is not needed |
| `XhciPortLimit` | `NO` | Only for macOS ≤ 11 (Big Sur); USB ports are mapped with USBToolBox (`UTBMap.kext`) |
| `ResizeAppleGpuBars` (Booter) | `0` | Required with Above 4G Decoding enabled |
| `ProvideCurrentCpuInfo` | `YES` | Coffee Lake CPU power management |

---

## 🗂️ Required SSDTs (Coffee Lake Desktop)

State below matches `ACPI → Add` in this repository's `config.plist`.

| SSDT | State | Role |
|---|---|---|
| `SSDT-PLUG-DRTNIA` | ✅ Enabled | CPU Power Management (P-States & C-States) |
| `SSDT-EC-USBX-DESKTOP` | ✅ Enabled | Embedded Controller + USB power |
| `SSDT-AWAC` | ✅ Enabled | RTC clock fix for Z370 (replaces AWAC with RTC) |
| `SSDT-PMC` | ❌ Disabled | Alternative to `SSDT-AWAC` for the Z370 PMC; the two are mutually exclusive. Untested here, enable only if `SSDT-AWAC` fails |

---

---

## ⚡ ASPM — PCIe Power Management (Advanced → Platform Misc Configuration)

> These settings cover the **Platform Misc Configuration** and **PCH / SA PCI Express** sections of the ASUS Z370-A BIOS. ASPM (Active State Power Management) reduces power consumption on idle PCIe links.

### Recommended Settings for Hackintosh Desktop (MacPro7,1 + Vega 64)

| Setting | Value | Priority | Reason |
|---|---|---|---|
| **PCI Express Native Power Management** | `Disabled` | 🔴 Important | Let BIOS manage ASPM — macOS has no full native control on Z370. Enabling can cause kernel panics or wake failures. |
| **Native ASPM** | `Disabled` | 🔴 Important | Only useful under Windows Vista+. Under macOS, BIOS-managed ASPM is more stable. |
| **DMI Link ASPM Control** (PCH PCIe) | `Disabled` | 🔴 Important | The DMI link (CPU to PCH) is critical — any interruption can cause freezes or black screens. |
| **ASPM** (PCH PCI Express) | `Disabled` | 🟠 Recommended | Disable globally for stability. Can be re-enabled per-device via DeviceProperties if needed. |
| **L1 Substates** (PCH PCI Express) | `Disabled` | 🟠 Recommended | L1 sub-states (L1.1 / L1.2) can cause latency spikes or spurious wake events on Hackintosh. |
| **ASPM Control** (SA PCIe) | `Disabled` | 🟠 Recommended | System Agent ASPM is irrelevant with iGPU disabled (MacPro7,1) and a potential source of conflicts. |
| **PEG ASPM** (SA PCIe) | `Disabled` | 🔴 Important | PEG slot = PCIe x16 for the Vega 64. Enabling ASPM on this link can cause GPU stutters or black screen on wake. |

### ASPM Power States Reference

| State | Description |
|---|---|
| `L0` | Active — all PCIe transactions running, no power savings |
| `L0s` | Light standby — fast entry/exit, minimal savings |
| `L1` | Deep standby — significant savings, higher wake latency |
| `L1.1 / L1.2` | L1 sub-states — maximum savings, incompatible with some Hackintosh hardware |

### Optional: Per-Device ASPM via DeviceProperties (NVMe Temperature)

If your NVMe SSD (WD SN850X) runs hot at idle, you can enable ASPM **only for that device** via `config.plist` DeviceProperties — without touching global BIOS settings:

```xml
<!-- Replace PciRoot path with your NVMe path (check with Hackintool -> PCIe tab) -->
<key>PciRoot(0x0)/Pci(0x1D,0x0)/Pci(0x0,0x0)</key>
<dict>
    <key>pci-aspm-default</key>
    <data>02010000</data>
</dict>
```

> Use **Hackintool -> PCIe tab** to get the exact PciRoot path of your NVMe and verify its current ASPM state with:
> `ioreg -l -p IODeviceTree | grep pci-aspm-default`

## 🛠️ OpenCore Installation & Update Guide

### 1. Updating OpenCore and Kexts
To update your EFI without breaking your system, follow the [Dortania Update Guide](https://dortania.github.io/OpenCore-Post-Install/universal/update.html).
1. Download the latest `OpenCorePkg` release.
2. Replace `BOOTx64.efi`, `OpenCore.efi`, and `OpenRuntime.efi`.
3. Update your Kexts in the `EFI/OC/Kexts` folder.
4. Run a **Clean Snapshot** (`Cmd/Ctrl + Shift + R`) in ProperTree.

### 2. Creating the Bootable USB
1. Format a USB drive as **Mac OS Extended (Journaled)** with a **GUID Partition Map**.
2. Run the `createinstallmedia` command for your desired macOS version.
3. Mount the USB's `EFI` partition and copy this repository's `EFI` folder into it.

### 3. First Boot & Install
1. Boot from the USB and select **Install macOS** in the OpenCore picker.
2. Format your NVMe as **APFS** (GUID Partition Map).
3. Install macOS. The system will reboot multiple times; always boot from the macOS Installer partition until complete.

### 4. Post-Install Checklist
- [ ] Load Optimized Defaults (`F5`), then apply all BIOS settings above
- [ ] Verify UEFI mode is active (no Legacy/CSM)
- [ ] iGPU confirmed disabled in Graphics Configuration
- [ ] CFG Lock disabled (or quirks enabled in config.plist)
- [ ] Above 4G Decoding enabled
- [ ] SATA in AHCI mode
- [ ] XHCI/EHCI Hand-off enabled
- [ ] Secure Boot + CSM disabled
- [ ] SMBIOS `MacPro7,1` serials generated with GenSMBIOS (unique values per machine, never committed)
- [ ] Audio Layout-id = `7` (ALC1220S)

---

## 📚 Credits
- [Dortania OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/)
- [Acidanthera](https://github.com/acidanthera) for OpenCore and Kexts.
