#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright (C) 2026 Carter Lee
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
import os
import sys
import subprocess
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import evdev
    from evdev import InputDevice, list_devices, ecodes
except ImportError:
    print("Missing python-evdev. Install it first.", file=sys.stderr)
    sys.exit(1)

try:
    import tkinter.colorchooser as colorchooser
except ImportError:
    colorchooser = None

RGB_BASE = "/sys/devices/platform/hp-wmi/rgb_zones"
OMEN_KEY_CODE = ecodes.KEY_PROG2
DEVICE_NAME = "HP WMI hotkeys"
GUI_SIZE = "860x1050"
ZONES = ("zone00", "zone01", "zone02", "zone03")

animation_running = False
animation_thread = None

presets = {
    "red": ["FF0000"] * 4,
    "green": ["00FF00"] * 4,
    "blue": ["0000FF"] * 4,
    "white": ["FFFFFF"] * 4,
    "rainbow": ["FF0000", "00FF00", "0000FF", "FFFFFF"],
    "sunset": ["FF4500", "FF8800", "FFB347", "FFE0B2"],
    "ice": ["00FFFF", "66CCFF", "3399FF", "FFFFFF"],
    "ocean": ["000033", "0000CC", "0066FF", "00CCFF"],
    "forest": ["003300", "006600", "339933", "99CC66"],
    "desert": ["CC6600", "FF9933", "FFCC66", "FFF2CC"],
    "deep_space": ["0B0C2A", "1A1B4B", "3A3B7A", "6A6BFF"],
    "vaporwave": ["FF00FF", "FF66CC", "9966FF", "6600FF"],
    "midnight": ["000000", "111133", "222266", "4444AA"],
    "soft_purple": ["220022", "440044", "880088", "CC66CC"],
    "lava": ["330000", "990000", "FF3300", "FFCC00"],
    "electric": ["000000", "0033FF", "00CCFF", "FFFFFF"],
    "matrix": ["001100", "003300", "00FF00", "00AA00"],
    "neon": ["FF00FF", "00FFFF", "FF00FF", "00FFFF"],
    "grayscale": ["111111", "333333", "777777", "FFFFFF"],
    "warm_white": ["FFF5E1", "FFE4B5", "FFDEAD", "FFDAB9"],
    "blue_fade": ["000033", "0000AA", "3333FF", "9999FF"],
    "soft_gray": ["222222", "444444", "666666", "888888"],
    "rainbow_soft": ["FF0000", "FF7F00", "00FF00", "0000FF"],
    "candy": ["FF66CC", "FFCC66", "66FFCC", "6699FF"],
    "aurora": ["00FFAA", "00CCFF", "6600FF", "FF00AA"],
    "party": ["FF0000", "00FF00", "0000FF", "FFFF00"],
    "galactic_nebula": ["4B0082", "6A5ACD", "9370DB", "CBA0E0"],
    "cyberpunk_glitch": ["FF00FF", "00FFFF", "FFA500", "39FF14"],
    "tropical_lagoon": ["20B2AA", "48D1CC", "7FFFD4", "98FB98"],
    "smokey_dusk": ["36454F", "4682B4", "708090", "A9A9A9"],
    "emerald_forest_mist": ["013220", "006400", "2E8B57", "6A994E"],
    "arena_red": ["FF0000", "FF2200", "AA0000", "550000"],
    "hacker_green": ["00FF00", "00AA00", "005500", "003300"],
    "zen_blue": ["1E90FF", "42A5F5", "7BC5FF", "B3E5FC"],
    "sunset_horizon": ["FF7F50", "FFA500", "FFD700", "FFFFE0"],
    "ocean_depth": ["191970", "4B0082", "6A5ACD", "9370DB"],
    "volcanic_ash": ["2F4F4F", "696969", "808080", "1C1C1C"],
    "neon_ghost": ["FFFFFF", "00FFFF", "FF00FF", "ADFF2F"],
    "off": ["000000"] * 4,
}

ANIMATIONS = {
    "rainbow_cycle": {
        "frames": [
            ["FF0000"] * 4,
            ["FF7F00"] * 4,
            ["FFFF00"] * 4,
            ["00FF00"] * 4,
            ["00FFFF"] * 4,
            ["0000FF"] * 4,
            ["8B00FF"] * 4,
            ["FF00FF"] * 4,
        ],
        "delay": 0.10,
    },
    "blue_wave": {
        "frames": [
            ["00CCFF", "003366", "000022", "000011"],
            ["003366", "00CCFF", "003366", "000022"],
            ["000022", "003366", "00CCFF", "003366"],
            ["000011", "000022", "003366", "00CCFF"],
            ["000022", "003366", "00CCFF", "003366"],
            ["003366", "00CCFF", "003366", "000022"],
        ],
        "delay": 0.08,
    },
    "red_scanner": {
        "frames": [
            ["FF0000", "220000", "000000", "000000"],
            ["220000", "FF0000", "220000", "000000"],
            ["000000", "220000", "FF0000", "220000"],
            ["000000", "000000", "220000", "FF0000"],
            ["000000", "220000", "FF0000", "220000"],
            ["220000", "FF0000", "220000", "000000"],
        ],
        "delay": 0.08,
    },
    "fire_wave": {
        "frames": [
            ["FF6600", "552200", "110000", "000000"],
            ["552200", "FFAA00", "552200", "110000"],
            ["110000", "552200", "FF3300", "552200"],
            ["000000", "110000", "552200", "FF6600"],
            ["110000", "552200", "FFAA00", "552200"],
            ["552200", "FF3300", "552200", "110000"],
        ],
        "delay": 0.08,
    },
    "rainbow_wave": {
        "frames": [
            ["FF0000", "00FF00", "0000FF", "FF00FF"],
            ["FF00FF", "FF0000", "00FF00", "0000FF"],
            ["0000FF", "FF00FF", "FF0000", "00FF00"],
            ["00FF00", "0000FF", "FF00FF", "FF0000"],
        ],
        "delay": 0.12,
    },
}


def normalize_hex(value: str) -> str:
    color = value.strip().upper().lstrip("#")
    if len(color) != 6 or any(ch not in "0123456789ABCDEF" for ch in color):
        raise ValueError(f"Invalid hex color: {value}")
    return color



def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"{r:02X}{g:02X}{b:02X}"



def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = normalize_hex(color)
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)



def write_zone(zone: str, color: str) -> None:
    path = os.path.join(RGB_BASE, zone)
    subprocess.run(
        ["sudo", "tee", path],
        input=(normalize_hex(color) + "\n").encode(),
        stdout=subprocess.DEVNULL,
        check=True,
    )



def apply_all(color: str) -> None:
    color = normalize_hex(color)
    for zone in ZONES:
        write_zone(zone, color)



def apply_preset(colors: list[str]) -> None:
    for zone, color in zip(ZONES, colors):
        write_zone(zone, normalize_hex(color))



def run_animation(frames: list[list[str]], delay: float = 0.08) -> None:
    global animation_running
    while animation_running:
        for frame in frames:
            if not animation_running:
                return
            apply_preset(frame)
            time.sleep(delay)



def start_animation(frames: list[list[str]], delay: float = 0.08) -> None:
    global animation_running, animation_thread
    animation_running = False
    if animation_thread is not None and animation_thread.is_alive():
        time.sleep(0.05)
    animation_running = True
    animation_thread = threading.Thread(
        target=run_animation,
        args=(frames, delay),
        daemon=True,
    )
    animation_thread.start()



def stop_animation() -> None:
    global animation_running
    animation_running = False


class ColorControl:
    def __init__(
        self,
        parent: ttk.Frame,
        label_text: str,
        default_hex: str,
        preview_width: int = 12,
    ) -> None:
        self.hex_var = tk.StringVar(value=normalize_hex(default_hex))
        r, g, b = hex_to_rgb(default_hex)
        self.r_var = tk.IntVar(value=r)
        self.g_var = tk.IntVar(value=g)
        self.b_var = tk.IntVar(value=b)
        self._updating = False

        outer = ttk.LabelFrame(parent, text=label_text, padding=10)
        outer.pack(fill="x", padx=8, pady=6)
        self.frame = outer

        top = ttk.Frame(outer)
        top.pack(fill="x", pady=(0, 8))

        ttk.Label(top, text="HEX").pack(side="left")
        self.hex_entry = ttk.Entry(top, textvariable=self.hex_var, width=12)
        self.hex_entry.pack(side="left", padx=(6, 10))
        self.hex_entry.bind("<KeyRelease>", self._on_hex_typed)
        self.hex_entry.bind("<FocusOut>", self._on_hex_focus_out)

        ttk.Button(top, text="Pick Color", command=self.choose_color).pack(side="left")

        self.preview = tk.Label(
            top,
            text="      ",
            relief="sunken",
            bd=1,
            width=preview_width,
        )
        self.preview.pack(side="right", padx=(10, 0))

        self.hex_label = ttk.Label(top, text="")
        self.hex_label.pack(side="right")

        self._make_slider_row(outer, "Red", self.r_var, self._on_rgb_changed)
        self._make_slider_row(outer, "Green", self.g_var, self._on_rgb_changed)
        self._make_slider_row(outer, "Blue", self.b_var, self._on_rgb_changed)

        self._sync_preview()

    def _make_slider_row(self, parent: ttk.Frame, text: str, variable: tk.IntVar, command) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=text, width=8).pack(side="left")
        scale = tk.Scale(
            row,
            from_=0,
            to=255,
            orient="horizontal",
            variable=variable,
            command=command,
            showvalue=True,
            length=330,
        )
        scale.pack(side="left", fill="x", expand=True)

    def _sync_preview(self) -> None:
        color = "#" + self.hex_var.get().strip().upper().lstrip("#")
        self.preview.configure(bg=color)
        self.hex_label.configure(text=color)

    def _on_rgb_changed(self, _value=None) -> None:
        if self._updating:
            return
        self._updating = True
        try:
            self.hex_var.set(rgb_to_hex(self.r_var.get(), self.g_var.get(), self.b_var.get()))
            self._sync_preview()
        finally:
            self._updating = False

    def _apply_hex_to_sliders(self, color: str) -> None:
        r, g, b = hex_to_rgb(color)
        self.r_var.set(r)
        self.g_var.set(g)
        self.b_var.set(b)

    def _on_hex_typed(self, _event=None) -> None:
        if self._updating:
            return
        raw = self.hex_var.get().strip().upper().lstrip("#")
        filtered = "".join(ch for ch in raw if ch in "0123456789ABCDEF")[:6]
        if raw != filtered:
            self._updating = True
            try:
                self.hex_var.set(filtered)
            finally:
                self._updating = False
        if len(filtered) == 6:
            self._updating = True
            try:
                self._apply_hex_to_sliders(filtered)
                self.hex_var.set(filtered)
                self._sync_preview()
            finally:
                self._updating = False

    def _on_hex_focus_out(self, _event=None) -> None:
        try:
            color = normalize_hex(self.hex_var.get())
        except ValueError:
            return
        self._updating = True
        try:
            self.hex_var.set(color)
            self._apply_hex_to_sliders(color)
            self._sync_preview()
        finally:
            self._updating = False

    def choose_color(self) -> None:
        if colorchooser is None:
            messagebox.showerror("Color Picker Error", "Color picker not available in this environment")
            return
        selected = colorchooser.askcolor(color="#" + self.get_hex(), title="Select Keyboard Color")
        if selected[1] is None:
            return
        color = normalize_hex(selected[1])
        self.set_hex(color)

    def get_hex(self) -> str:
        return normalize_hex(self.hex_var.get())

    def set_hex(self, color: str) -> None:
        color = normalize_hex(color)
        self._updating = True
        try:
            self.hex_var.set(color)
            self._apply_hex_to_sliders(color)
            self._sync_preview()
        finally:
            self._updating = False



def open_gui() -> None:
    if not os.path.isdir(RGB_BASE):
        messagebox.showerror("Omen RGB", f"RGB path not found:\n{RGB_BASE}")
        return

    root = tk.Tk()
    root.title("Omen RGB")
    root.geometry(GUI_SIZE)
    root.resizable(True, True)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=12, pady=12)

    presets_frame = ttk.Frame(notebook)
    notebook.add(presets_frame, text="Presets")

    def do_preset(name: str) -> None:
        try:
            stop_animation()
            apply_preset(presets[name])
        except Exception as e:
            messagebox.showerror("RGB Error", str(e))

    preset_grid = ttk.Frame(presets_frame)
    preset_grid.pack(fill="both", expand=True, padx=10, pady=10)

    for i, name in enumerate(list(presets.keys())):
        row = i // 4
        col = i % 4
        btn = ttk.Button(
            preset_grid,
            text=name.replace("_", " ").title(),
            command=lambda n=name: do_preset(n),
            width=18,
        )
        btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

    animations_frame = ttk.Frame(notebook)
    notebook.add(animations_frame, text="Animations")

    for key, label in [
        ("rainbow_cycle", "Rainbow Cycle"),
        ("blue_wave", "Blue Wave"),
        ("red_scanner", "Red Scanner"),
        ("fire_wave", "Fire Wave"),
        ("rainbow_wave", "Rainbow Wave"),
    ]:
        ttk.Button(
            animations_frame,
            text=label,
            command=lambda k=key: start_animation(ANIMATIONS[k]["frames"], ANIMATIONS[k]["delay"]),
        ).pack(fill="x", padx=10, pady=2)

    ttk.Button(animations_frame, text="Stop Animation", command=stop_animation).pack(pady=(5, 10))

    custom_frame = ttk.Frame(notebook)
    notebook.add(custom_frame, text="Custom Colors")

    custom_notebook = ttk.Notebook(custom_frame)
    custom_notebook.pack(fill="both", expand=True, padx=8, pady=8)

    all_frame = ttk.Frame(custom_notebook)
    individual_frame = ttk.Frame(custom_notebook)
    custom_notebook.add(all_frame, text="All 4 At Once")
    custom_notebook.add(individual_frame, text="Individual Zones")

    ttk.Label(
        all_frame,
        text="Set one color for all four zones. Use the sliders, a HEX code, or the color picker.",
    ).pack(anchor="w", padx=10, pady=(10, 0))

    all_control = ColorControl(all_frame, "All Zones", "FFFFFF", preview_width=18)

    def apply_all_custom() -> None:
        try:
            stop_animation()
            apply_all(all_control.get_hex())
        except Exception as e:
            messagebox.showerror("RGB Error", str(e))

    ttk.Button(all_frame, text="Apply To All Zones", command=apply_all_custom).pack(pady=(4, 10))

    ttk.Label(
        individual_frame,
        text="Set each zone separately. Every zone supports sliders, HEX input, and the color picker.",
    ).pack(anchor="w", padx=10, pady=(10, 0))

    zone_controls = [
        ColorControl(individual_frame, "Zone 0", "FF0000"),
        ColorControl(individual_frame, "Zone 1", "00FF00"),
        ColorControl(individual_frame, "Zone 2", "0000FF"),
        ColorControl(individual_frame, "Zone 3", "FFFFFF"),
    ]

    def apply_individual_custom() -> None:
        try:
            stop_animation()
            apply_preset([control.get_hex() for control in zone_controls])
        except Exception as e:
            messagebox.showerror("RGB Error", str(e))

    ttk.Button(individual_frame, text="Apply Individual Zones", command=apply_individual_custom).pack(pady=(4, 10))

    ttk.Button(root, text="Close", command=root.destroy).pack(pady=(5, 10))

    root.mainloop()



def find_hp_wmi_device() -> InputDevice | None:
    for path in list_devices():
        dev = InputDevice(path)
        if dev.name == DEVICE_NAME:
            return dev
    return None



def gui_running() -> bool:
    result = subprocess.run(
        ["pgrep", "-f", "omen-keygui.py gui"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0



def launch_gui() -> None:
    subprocess.Popen(
        ["/usr/local/bin/omen-keygui-launch"],
        start_new_session=True,
    )



def listen_loop() -> None:
    dev = find_hp_wmi_device()
    if dev is None:
        print(f"Could not find input device: {DEVICE_NAME}", file=sys.stderr)
        sys.exit(1)

    print(f"Listening for OMEN key events on {dev.path} ({dev.name})...")
    last_launch = 0.0

    for event in dev.read_loop():
        if event.type != ecodes.EV_KEY:
            continue

        key_event = evdev.categorize(event)
        if key_event.scancode == OMEN_KEY_CODE and key_event.keystate == key_event.key_down:
            now = time.time()
            if now - last_launch > 0.5 and not gui_running():
                launch_gui()
                last_launch = now



def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: omen-keygui.py [gui|listen]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "gui":
        open_gui()
    elif mode == "listen":
        listen_loop()
    else:
        print("Usage: omen-keygui.py [gui|listen]")
        sys.exit(1)


if __name__ == "__main__":
    main()
