# HP Omen RGB Control and Macro Key Support

This repository was forked from  
https://github.com/xddxdd/hp-omen-linux-module  

It has been adapted for newer kernels and extended with a Python GUI for easier RGB control.

This project was developed and tested on an **HP Omen 17 cm2047nr** for personal use, but may be useful for others with similar hardware.

---

## Overview

This project provides:

- A patched `hp-wmi` kernel module (via DKMS)
- Support for OMEN macro (P) keys
- RGB keyboard control via sysfs
- A Python GUI for easier RGB management

⚠️ **Experimental:** This replaces a core kernel driver (`hp-wmi`).  
Use at your own risk and be prepared to revert if issues occur.

---

## Device Info

**HP Omen 17 cm2047nr**
- Gentoo Linux  
  - OpenRC init system  
  - KDE Plasma (Wayland — should also work on X11/XLibre)  
- Kernel Version 7.0.0 (mainline)  
- `board_name`: `8BB0`

---

## Tested On

- HP Omen 17 cm2047nr  
- Gentoo Linux (OpenRC)  
- Kernel 7.0.0 (mainline)

Other systems may work but are untested.

---

## Kernel Module

The patched module is used via DKMS.

Once installed, it **replaces the in-tree `hp-wmi` module at load time**, meaning your system will use this version instead of the stock kernel driver.

So far, no major issues have been observed in day-to-day use, but stability is not guaranteed.

---

## What is Working

### 1. OMEN Key
- Dedicated OMEN key (top-right of keyboard)

### 2. Macro (P) Keys  
Mapped as numpad keys (credit to original author)

**With NumLock enabled:**
- P1 → 1  
- P2 → 2  
- P3 → 3  
- P4 → 4  
- P5 → 5  
- P6 → 6  

**With FN held:**
- P1 → 7  
- P2 → 8  
- P3 → 9  
- P4 → 0  
- P5 → -  
- P6 → +  

I use `x11-misc/numlockx` along with KDE’s startup option to ensure NumLock is enabled.  
This allows the P keys to be easily used for shortcuts.

---

### 3. RGB Keyboard Control

RGB zones are exposed via:

```
/sys/devices/platform/hp-wmi/rgb_zones/
```

Zones:
- `zone00`
- `zone01`
- `zone02`
- `zone03` (WASD area)

Colors are written as hex values (RRGGBB).

---

## Installation

1. Install DKMS and kernel headers

2. Install the module:
```bash
sudo make install
```

3. Reboot:
```bash
sudo reboot
```

---

## GUI App

A Python GUI is included for controlling keyboard RGB.

⚠️ **Requires root privileges**

### Launch GUI
```bash
sudo ./omen-keygui.py gui
```

### Background listener (OMEN key launch)
```bash
omen-keygui.py listen
```

### Enable the listening service if needed:
```bash
sudo rc-update add omen-keygui-listener default
sudo rc-service omen-keygui-listener start
``` 

---

### Features

- Preset static colors  
- Animations  
- Custom color control:
  - Individual zone control  
  - Single color for all zones  
  - RGB sliders  
  - HEX input  
  - Live color preview  

---

## Notes

- Requires root access to write to sysfs  

---

## More Information / Reading

For more details on the original reverse engineering work:

- https://lantian.pub/en/article/modify-computer/reverse-engineered-linux-driver-for-hp-omen-macro-keys.lantian/  
- https://github.com/pelrun/hp-omen-linux-module/issues/18  

## Original Project

This repository is based on:

https://github.com/xddxdd/hp-omen-linux-module

<details>
<summary>Original README (click to expand)</summary>

HP Omen special feature control for Linux
-----------------------------------------

This is a version of the hp-wmi kernel module that implements some of the features of HP Omen Command Centre.

It's totally experimental right now, and could easily crash your machine. 

**USE AT YOUR OWN RISK**

Currently working:

- FourZone keyboard colour control (`/sys/devices/platforms/hp-wmi/rgb-zones/zone0[0-3]`)
- Omen hotkeys

## Installation

1. Install dkms and kernel headers if needed (already present on Ubuntu)

1. Run `sudo make install`

Module will be built and installed, and DKMS will manage rebuilding it on kernel updates.

## Usage

The module creates four files in `/sys/devices/platform/hp-wmi/rgb_zones/` named `zone00 - zone03`.

To change zone highlight color, just print hex colour value in RGB format to the respective file. e.g:

`sudo bash -c 'echo 00FFFF > /sys/devices/platform/hp-wmi/rgb_zones/zone00'` to get sky-blue zone 0.

Omen and other hotkeys are bound to regular X11 keysyms, use your chosen desktop's hotkey manager to assign them to functions like any other key.

## To do:

- [ ] FourZone brightness control
- [ ] Fan control 

</details>