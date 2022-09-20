# ASUS-PRIME-Z370-A-Hackintoshed

Tested on :
- Mojave 10.14.x
- Catalina 10.15.x
- BigSur 11.6.2 (20G314)
- Monterrey 12.6

The config i'm using :

- Motherboard: https://www.asus.com/fr/Motherboards/PRIME-Z370-A/
  * ALC1220S - > Layout-id = 7
- Intel i7 9700 (~~forced type i7 in config.plist : 0x0705~~)
  * Seen as Intel Xeon with iMacPro1,1
  * Seen as Intel i9-8cores with iMac19,1
- Graphic Card: https://www.gigabyte.com/fr/Graphics-Card/GV-RXVEGA64GAMING-OC-8GD#kf
- Wifi + Bluetooth PCI Card : https://www.amazon.fr/gp/offer-listing/B00MBP25UK/ref=dp_olp_new_mbc?ie=UTF8&condition=new
- Sabrent Rocket 4.0 500GB (Largeur du câble :	x4 - Vitesse de la liaison :	8.0 GT/s)



- Full Working

- With VEGA 64 -> No fan speed problem -no more patch neeeded
- No sleep problem
- No black screen

For Step 2: After you've got to built you're own SMBIOS values with iMacPro1,1 or iMac19,1
SMBIOS: Working on DRM ...
iMacPro1,1 -> iGpu must be disable in BIOS
or
iMac19,1 -> could be enable or not, system not affected

Good luck!
