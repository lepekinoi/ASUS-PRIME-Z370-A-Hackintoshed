# 🍏 ASUS PRIME Z370-A Hackintosh (OpenCore)

A fully working OpenCore build for the **ASUS PRIME Z370-A** paired with an **Intel i7-9700**, **Gigabyte Vega 64**, **ALC1220S audio**, and full Bluetooth support. 🚀

## 📦 Current EFI Versions (Auto-Updated)
- **OpenCore:** 1.0.7
- **Lilu:** 1.7.2
- **WhateverGreen:** 1.7.0
- **AppleALC:** 1.9.7

***

## 💻 Hardware Configuration

| Component | Model | Status/Notes |
|---|---|---|
| **Motherboard** | ASUS PRIME Z370-A | Working perfectly |
| **CPU** | Intel Core i7-9700 (Coffee Lake) | Native Power Management |
| **GPU** | Gigabyte RX Vega 64 8GB | Native support (OOB) |
| **Audio** | Realtek ALC1220S | `layout-id=7` |
| **Storage** | WD Black SN850X NVMe | Fully compatible |
| **Bluetooth** | Intel / Broadcom | Fully working (requires `-ibtcompatbeta` boot-arg on Tahoe) |

## 🎭 SMBIOS Selection

- 🖥️ **`iMacPro1,1` (Recommended):** Best for a dGPU-only build (Vega 64). Ensure the iGPU is **disabled** in the BIOS. Enables native DRM (Apple TV+, Netflix in Safari, Prime Video).
- 🖥️ **`iMac19,1`:** Use this if you need to keep the iGPU enabled for compute tasks.

> ⚠️ With `iMacPro1,1`, the CPU will appear as **Intel Xeon** in "About This Mac" — this is expected and does not affect performance.

***

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
- **VT-d** — Can disrupt macOS IOMMU. Alternative: set `DisableIoMapper=YES` in `config.plist → Kernel → Quirks`.
- **Intel SGX** — Unused, may cause instability.
- **Intel Platform Trust (PTT/TPM)** — Not needed under macOS.
- **Serial / COM Port** — Can conflict with ACPI SSDTs.
- **iGPU (Intel UHD 630)** ⚠️ **REQUIRED with iMacPro1,1** — The `iMacPro1,1` SMBIOS has no iGPU in the Apple model. Leaving it enabled will cause kernel panics. The Vega 64 handles all rendering.

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

***

## 🧩 OpenCore Kernel Quirks (config.plist)

| Quirk | Value | Notes |
|---|---|---|
| `AppleCpuPmCfgLock` | `YES` | Set to `NO` if CFG Lock is disabled in BIOS |
| `AppleXcpmCfgLock` | `YES` | Set to `NO` if CFG Lock is disabled in BIOS |
| `DisableIoMapper` | `YES` | Required if VT-d is not disabled in BIOS |
| `XhciPortLimit` | `YES` | Only for macOS ≤ 11 (Big Sur); disable on Monterey+ |
| `ResizeAppleGpuBars` | `0` | Required with Above 4G Decoding enabled |
| `ProvideCurrentCpuInfo` | `YES` | Coffee Lake CPU power management |

***

## 🗂️ Required SSDTs (Coffee Lake Desktop)

| SSDT | Role |
|---|---|
| `SSDT-PLUG` | CPU Power Management (P-States & C-States) |
| `SSDT-EC-USBX` | Embedded Controller + USB power |
| `SSDT-AWAC` | RTC clock fix for Z370 (replaces AWAC with RTC) |
| `SSDT-PMC` | Power Management Controller — required for Z370 chipset |

***

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
- [ ] SMBIOS `iMacPro1,1` generated with GenSMBIOS (unique values per machine)
- [ ] Audio Layout-id = `7` (ALC1220S)

***

## 📚 Credits
- [Dortania OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/)
- [Acidanthera](https://github.com/acidanthera) for OpenCore and Kexts.
