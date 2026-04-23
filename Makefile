.PHONY: all install uninstall install-module install-gui uninstall-module uninstall-gui

PREFIX ?= /usr/local
BINDIR := $(PREFIX)/bin
INITDIR := /etc/init.d

DKMS_CONF := dkms.conf
PACKAGE_NAME := $(shell awk -F= '/^PACKAGE_NAME=/{print $$2}' $(DKMS_CONF))
PACKAGE_VERSION := $(shell awk -F= '/^PACKAGE_VERSION=/{print $$2}' $(DKMS_CONF))

install: install-module install-gui

install-module:
	dkms install .

install-gui:
	@echo "Installing gui"
	install -d $(BINDIR)
	install -m 755 gui/omen-keygui.py $(BINDIR)/omen-keygui

	@echo "Installing OpenRC service"
	install -d $(INITDIR)
	install -m 755 scripts/omen-keygui-listener $(INITDIR)/omen-keygui-listener

uninstall: uninstall-gui uninstall-module

uninstall-module:
	dkms remove $(PACKAGE_NAME)/$(PACKAGE_VERSION) --all

uninstall-gui:
	@echo "Uninstalling gui"
	rm -f $(BINDIR)/omen-keygui.py

	@echo "Uninstalling OpenRC service"
	rm -f $(INITDIR)/omen-keygui-listener

all: install