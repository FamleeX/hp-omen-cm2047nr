.PHONY: all install uninstall install-module install-gui install-udev uninstall-module uninstall-gui uninstall-udev

PREFIX ?= /usr/local
BINDIR := $(PREFIX)/bin

UDEVDIR := /etc/udev/rules.d
RGB_GROUP := omen
DESKTOPDIR := /usr/share/applications
ICONDIR := /usr/share/pixmaps

DKMS_CONF := dkms.conf
PACKAGE_NAME := $(shell awk -F= '/^PACKAGE_NAME=/{print $$2}' $(DKMS_CONF))
PACKAGE_VERSION := $(shell awk -F= '/^PACKAGE_VERSION=/{print $$2}' $(DKMS_CONF))

install: install-module install-gui install-udev

install-module:
	dkms install .

install-gui:
	@echo "Installing GUI"
	install -d $(BINDIR)
	install -m 755 gui/omen-keygui.py $(BINDIR)/omen-keygui

	@echo "Installing icon"
	install -d $(ICONDIR)
	install -m 644 icons/omen-keygui.png $(ICONDIR)/omen-keygui.png

	@echo "Installing desktop entry"
	install -d $(DESKTOPDIR)
	install -m 644 desktop/omen-keygui.desktop $(DESKTOPDIR)/omen-keygui.desktop

	@echo "Refreshing desktop database"
	-kbuildsycoca6 >/dev/null 2>&1 || true

install-udev:
	@echo "Creating RGB access group if needed"
	getent group $(RGB_GROUP) >/dev/null || groupadd $(RGB_GROUP)

	@echo "Installing udev rule"
	install -d $(UDEVDIR)
	install -m 644 udev/99-omen-rgb.rules $(UDEVDIR)/99-omen-rgb.rules

	@echo "Reloading udev rules"
	udevadm control --reload-rules
	udevadm trigger

	@echo
	@echo "To use the GUI without sudo, add your user to the $(RGB_GROUP) group:"
	@echo "  sudo usermod -aG $(RGB_GROUP) YOUR_USERNAME"
	@echo "Then log out and back in."

uninstall: uninstall-gui uninstall-module uninstall-udev

uninstall-module:
	dkms remove $(PACKAGE_NAME)/$(PACKAGE_VERSION) --all

uninstall-gui:
	@echo "Uninstalling GUI"
	rm -f $(BINDIR)/omen-keygui
	rm -f $(DESKTOPDIR)/omen-keygui.desktop
	rm -f $(ICONDIR)/omen-keygui.png
	
	@echo "Refreshing desktop database"
	-kbuildsycoca6 >/dev/null 2>&1 || true

uninstall-udev:
	@echo "Uninstalling udev rule"
	rm -f $(UDEVDIR)/99-omen-rgb.rules
	udevadm control --reload-rules

all: install