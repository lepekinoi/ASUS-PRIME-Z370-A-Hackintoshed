# 🍏 ASUS PRIME Z370-A Hackintosh (OpenCore)

A fully working OpenCore build for the **ASUS PRIME Z370-A** paired with an **Intel i7-9700**, **Gigabyte Vega 64**, **ALC1220S audio**, and full Bluetooth support. 🚀

## 📦 Current EFI Versions (Auto-Updated)
- **OpenCore:** 1.0.7
- **Lilu:** 1.7.2
- **WhateverGreen:** 1.7.0
- **AppleALC:** 1.9.7

---

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

- 🖥️ **`iMacPro1,1` (Recommended):** Best for a dGPU-only build (Vega 64). Ensure the iGPU is **disabled** in the BIOS.
- 🖥️ **`iMac19,1`:** Use this if you need to keep the iGPU enabled for compute tasks.

---

## ⚙️ BIOS Settings (Crucial for Coffee Lake)

### ❌ Disable
- Fast Boot, Secure Boot, CSM, VT-d (unless `DisableIoMapper=YES`), CFG-Lock, Intel SGX, Serial/Parallel Port.

### ✅ Enable
- VT-x, Above 4G Decoding, Hyper-Threading, Execute Disable Bit, EHCI/XHCI Hand-off, OS Type: `Windows 8.1/10 UEFI Mode`, DVMT Pre-Allocated: **64MB**, SATA Mode: **AHCI**.

---

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

---
## 📚 Credits
- [Dortania OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/)
- [Acidanthera](https://github.com/acidanthera) for OpenCore and Kexts.
