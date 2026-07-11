# 🍏 ASUS PRIME Z370-A Hackintosh

A fully working OpenCore build for the **ASUS PRIME Z370-A** paired with an **Intel i7-9700**, **Gigabyte Vega 64**, **ALC1220S audio**, and full Bluetooth support. 🚀

This repository contains the configuration to successfully boot macOS on this Coffee Lake hardware setup. 

---

## 💻 Hardware Configuration

- **Motherboard:** [ASUS PRIME Z370-A](https://www.asus.com/Motherboards/PRIME-Z370-A/)
- **CPU:** Intel Core i7-9700 (Coffee Lake)
- **GPU:** [Gigabyte RX Vega 64](https://www.gigabyte.com/Graphics-Card/GV-RXVEGA64GAMING-OC-8GD#kf)
- **Audio:** Realtek ALC1220S (`layout-id=7`)
- **Storage:** NVMe SSD (e.g., WD Black SN850X or Sabrent Rocket 4.0)
- **Bluetooth:** Fully working (requires `-ibtcompatbeta` boot-arg on macOS Tahoe 26)

## 🎭 SMBIOS Selection

Depending on your configuration, you should choose the appropriate SMBIOS:

- 🖥️ **`iMacPro1,1` (Recommended):** The best choice if you have a dedicated AMD GPU (like the Vega 64) and the iGPU is **disabled** in the BIOS. This setup is highly recommended for stability and full dGPU utilization.
- 🖥️ **`iMac19,1`:** An alternative option if you intend to keep the iGPU enabled (e.g., for computing tasks), though it is less optimal for a pure dGPU build.

---

## ⚙️ BIOS Settings

For OpenCore to boot macOS smoothly on Coffee Lake, your BIOS must be configured correctly. Press `DEL` or `F2` at boot to enter the ASUS UEFI BIOS.

### ❌ Disable
- Fast Boot
- Secure Boot
- Serial/COM Port
- Parallel Port
- VT-d (can be enabled if `DisableIoMapper=YES` is set in OpenCore)
- CSM (Compatibility Support Module)
- Thunderbolt (during initial installation)
- Intel SGX
- Intel Platform Trust
- CFG-Lock (If this option is missing in your BIOS, ensure `AppleXcpmCfgLock` is enabled in `Kernel -> Quirks`)

### ✅ Enable
- VT-x
- Above 4G Decoding
- Hyper-Threading
- Execute Disable Bit
- EHCI/XHCI Hand-off
- OS Type: `Windows 8.1/10 UEFI Mode` (or `Other OS`)
- DVMT Pre-Allocated (iGPU Memory): **64MB or higher**
- SATA Mode: **AHCI**

> **Note:** If using the recommended `iMacPro1,1` SMBIOS, make sure your integrated graphics (iGPU) are completely disabled in the BIOS.

---

## 🛠️ Installation Guide

Follow these steps to create your bootable USB and install macOS.

### Step 1: Prepare the Tools
1. Download the latest release of [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg/releases).
2. Download [ProperTree](https://github.com/corpnewt/ProperTree) to properly edit your `config.plist` (avoid third-party OpenCore configurator apps!).
3. Download macOS (using the App Store or Munki's script for Mac users, or the online installer method for Windows/Linux).

### Step 2: Create the Bootable USB 💾
1. Format a USB drive (at least 16GB) as **Mac OS Extended (Journaled)** with a **GUID Partition Map**.
2. Run the `createinstallmedia` command in the Terminal (macOS) to flash the installer to your USB drive. 
3. Mount the hidden `EFI` partition of your USB drive (using tools like MountEFI or terminal commands).
4. Copy the `EFI` folder from this repository into the `EFI` partition of the USB drive.

### Step 3: Finalize config.plist 📝
1. Open the copied `config.plist` using **ProperTree**.
2. Run a **Clean Snapshot** (`Cmd/Ctrl + Shift + R`) and select your `EFI/OC` folder to ensure all kexts and ACPI files are correctly linked.
3. Save the file.

### Step 4: Install macOS 🍎
1. Reboot your PC and boot from the USB drive.
2. In the OpenCore picker, choose **Install macOS**.
3. Open **Disk Utility**, format your target drive as **APFS** with a **GUID Partition Map**.
4. Proceed with the macOS installation. The system will reboot multiple times—always select the macOS installer partition (not the USB drive) during these intermediate reboots until you reach the setup screen.

---

## 📚 Credits & Resources

- [Dortania OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/) - The ultimate reference for Hackintosh.
- [Acidanthera](https://github.com/acidanthera) - For OpenCore, WhateverGreen, AppleALC, and other essential kexts.

✨ *Happy Hackintoshing!* ✨
