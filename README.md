HP Omen RGB Control and Macro Key Support
-----------------------------------------

This repo was forked from [https://github.com/xddxdd/hp-omen-linux-module](https://github.com/xddxdd/hp-omen-linux-module)
in order to adapt his working usage to newer kernels and to add a gui app. 

I own and use an HP Omen 17 cm2047nr. I forked/updated this for my own use, but hopefully someone else can benefit too.

## Device Info

**HP Omen 17 cm2047nr**
- Gentoo Linux
  - OpenRC init system
  - KDE Plasma (Wayland, don't see why it wouldn't work on X11 or XLibre)
- Kernel Version 7.0.0 [kernel.org](https://www.kernel.org) 
  - mainline version as of writing
- `cat /sys/devices/virtual/dmi/id/board_name` = 8BB0

Currently the patched module is used as a dkms module. Once built, it will override the stock hp-wmi
in-tree kernel module. So far, I have not noticed any issues day-to-day with this module. Currently,
please **USE AT YOUR OWN RISK.** While I have tested only on mainline kernel 7.0.0 and Gentoo, 
it may work on other kernels/distros. 

There are plans to port this over to other distros and/or init systems where applicable. 
In my testing I have a python gui script that can modify the led's much easier. 

## What is working with the kernel module

1. HP Omen Key (next to the calculator button on the top right of the keyboard)
2. Mapped P/Macro Keys as Numpad keys (thanks [xddxdd](https://github.com/xddxdd/hp-omen-linux-module))
 - Once Numlock is on:
   - P1 is 1, P2 is 2, P3 is 3, P4 is 4, P5 is 5, P6 is 6
 - With the FN key held:
   - P1 is 7, P3 is 8, P3 is 9, P4 is 0, P5 is -, P6 is +
3. RGB Led's on keyboard
 - check original readme at the bottom for info on added files

I use a combination of x11-misc/numlockx to turn on numlock, and KDE's option to toggle numlock on startup.
The way the P Keys are mapped, this should be good enough in order to bind them as shortcuts.

## Installation

1. Install dkms and kernel headers 

2. Run `sudo make install` 

3. Then you can `sudo reboot`


## GUI app
Currently the python script is not in the makefile. It will need to be ran as root in order to work.
Running `sudo ./omen-keygui.py gui` should work. 
`omen-keygui.py listen` lets the app run in the background and wait for an Omen key press.

Features:
- Presets of static/solid colors
- Animations/dynamically changing colors
- Custom color picker
  - A static color for the 4 zones independently
  - Or one static color for all 4 zones
  - A preview of the color


More Information/Reading
-----------------------------------------

For more reading on this please read xddxdd's 
- [reverse engineering notes](https://lantian.pub/en/article/modify-computer/reverse-engineered-linux-driver-for-hp-omen-macro-keys.lantian/) 
- [his comment on pelrun's repo](https://github.com/pelrun/hp-omen-linux-module/issues/18)


Original Readme
-----------------------------------------

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

