# Hackintosh ASUS PRIME Z370-A — règles projet

## Matériel
ASUS PRIME Z370-A · i7-9700 · Gigabyte RX Vega 64 · ALC1220S (alcid=7) · NVMe · macOS Tahoe 26 · OpenCore 1.0.8

## Source de vérité
- `EFI/OC/config.plist` fait foi. Le README peut être en retard.
- README.md est généré par `.github/workflows` depuis `README.template.md` : modifier le template, jamais README.md directement. Vérifier le workflow avant de toucher à l'un ou l'autre.

## Choix volontaires — NE PAS "corriger"
- SMBIOS MacPro7,1 + `revpatch=sbvmm` + RestrictEvents.kext : stratégie voulue (accélération Vega 64 + OTA).
- Quirks : AppleXcpmCfgLock=true / AppleCpuPmCfgLock=false.
- SSDT-AWAC et SSDT-PMC sont mutuellement exclusifs : un seul Enabled=true à la fois.
- SecureBootModel=Disabled : requis par Dortania pour Tahoe (14.4–26.x) avec MacPro7,1 + `revpatch=sbvmm`. Avec Default, l'install boucle en fin de 2e phase.

## Règles d'édition
- Éditer les plist via Python `plistlib` (load/dump, sort_keys=False), jamais par regex/sed.
- Après toute modif d'EFI : `powershell -ExecutionPolicy Bypass -File tools/validate.ps1` doit passer.
- Ajout/suppression de kext ou SSDT : mettre à jour Kernel/Add ou ACPI/Add (Lilu en premier, puis ses plugins).
- Ne jamais committer de valeurs PlatformInfo réelles (SystemSerialNumber, MLB, SystemUUID, ROM) : repo public.
- Les vraies valeurs PlatformInfo vivent uniquement dans `tools/bin/platforminfo.local.json`, injectées au déploiement (`tools/inject_platforminfo.py`).
- Un changement = une branche + un commit explicite. Jamais de push --force, jamais de commit sans que je le demande.
- Jamais `git add -A` ni `git add .` : toujours lister les fichiers explicitement, puis vérifier `git diff --cached --stat` avant commit.
