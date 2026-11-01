# Hackintosh ASUS PRIME Z370-A — règles projet

## Matériel
ASUS PRIME Z370-A · i7-9700 · 32 Go DDR4-2666 · Gigabyte RX Vega 64 · ALC1220S (layout-id 7) · NVMe · macOS Tahoe 26 · OpenCore 1.0.8
USB : Intel Z370 `XHC` · ASMedia ASM2142 intégré (`RP05`, USB-C + USB 3.1 Gen2 arrière) · carte PCIe ASMedia ASM1242 (`RP21`, 2 × USB-C, alim SATA, slot fixe). Machine destinée à la revente.

## Source de vérité
- `EFI/OC/config.plist` fait foi. Le README peut être en retard.
- README.md est généré depuis `README.template.md` et l'EFI par `tools/render_readme.py` (en local ou par `.github/workflows`) : modifier le template, jamais README.md directement. Après une modif d'EFI ou du template, relancer `python3 tools/render_readme.py`.

## Choix volontaires — NE PAS "corriger"
- SMBIOS MacPro7,1 + `revpatch=sbvmm` + RestrictEvents.kext : stratégie voulue (accélération Vega 64 + OTA).
- Quirks : AppleXcpmCfgLock=true / AppleCpuPmCfgLock=false.
- SSDT-AWAC et SSDT-PMC sont mutuellement exclusifs : un seul Enabled=true à la fois.
- SecureBootModel=Disabled : requis par Dortania pour Tahoe (14.4–26.x) avec MacPro7,1 + `revpatch=sbvmm`. Avec Default, l'install boucle en fin de 2e phase.
- Thunderbolt désactivé dans le BIOS, définitivement : aucune carte ThunderboltEX 3. Activé, il réserve des bus PCI et décale les `pcidebug` des ASMedia dans UTBMap.kext. Ne pas proposer de le réactiver ni d'ajouter de SSDT Thunderbolt.
- Pas de Wi-Fi ni de Bluetooth, volontairement (rien de compatible Tahoe). Le module BT (ancien port interne HS10 Intel) est débranché : ne pas le mapper, ne pas proposer de kext sans fil.
- UTBMap.kext : Intel matché par `IONameMatch` XHC ; les 2 ASMedia (tous deux `PXSX`) par `pcidebug` = adresse PCI **macOS** (`RP05` 8:0:0, `RP21` 6:0:0, soit bus Windows + 1). Une map générée sous Windows doit être corrigée sur ce point. Ports compagnons HS/SS d'une même prise = même `#comment`. Max 15 ports par contrôleur. À vérifier sous Tahoe : `ioreg -l -w0 | grep '"pcidebug"'`.
- Audio intégré : SimpleHDA.kext (réinjecte AppleHDA, absent de Tahoe) + AppleALC.kext, ordre Lilu → AppleALC → SimpleHDA, `layout-id` 7 en DeviceProperties sur `PciRoot(0x0)/Pci(0x1F,0x3)` (pas d'`alcid`). `keepsyms=1` est requis par SimpleHDA. Codec vu par Windows : 10EC:1168. Pas d'autre restauration AppleHDA ni root patch en parallèle.
- Le connecteur USB-C de façade du boîtier n'est pas branché (pas de header sur la carte) : rien à mapper.

## Règles d'édition
- Éditer les plist via Python `plistlib` (load/dump, sort_keys=False), jamais par regex/sed.
- Après toute modif d'EFI : `powershell -ExecutionPolicy Bypass -File tools/validate.ps1` (macOS : `tools/validate.sh`) doit passer.
- Ajout/suppression de kext ou SSDT : mettre à jour Kernel/Add ou ACPI/Add (Lilu en premier, puis ses plugins). Ordre actuel de Kernel/Add : Lilu → VirtualSMC → SMCProcessor → SMCSuperIO → AppleALC → SimpleHDA → RestrictEvents → NVMeFix → IntelMausi → USBToolBox → UTBMap.
- Ne jamais committer de valeurs PlatformInfo réelles (SystemSerialNumber, MLB, SystemUUID, ROM) : repo public.
- Les vraies valeurs PlatformInfo vivent uniquement dans `tools/bin/platforminfo.local.json`, injectées au déploiement (`tools/inject_platforminfo.py`). GenSMBIOS sert à générer seulement : s'il écrit dans `config.plist`, lancer `inject_platforminfo.py sanitize`. Ne jamais afficher ces valeurs en clair.
- Outils locaux (gitignorés) dans `tools/bin/` : `ocvalidate.exe` + `ocvalidate`, `GenSMBIOS/`, `USBToolBox/Windows.exe` (les ASMedia doivent être sous pilote Microsoft xHCI pour être vus).
- Un changement = une branche + un commit explicite. Jamais de push --force, jamais de commit sans que je le demande.
- Jamais `git add -A` ni `git add .` : toujours lister les fichiers explicitement, puis vérifier `git diff --cached --stat` avant commit.
