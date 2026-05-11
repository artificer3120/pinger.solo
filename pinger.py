"""
pinger — radix-shelled control panel widget

Independent widget on the untitledSDK BaseFrame with theme=radix.
Ships four buttons: Ping! / Mini-Mac (toggle) / scrollstack (toggle) / snap.

Usage:
    python pinger.py
    pythonw pinger.py    # background
"""

import sys
import os
import random
import subprocess
import threading
import winsound
import ctypes
import ctypes.wintypes

try:
    import psutil
except ImportError:
    psutil = None

SDK_PATH = os.path.expanduser("~/dev/untitledSDK")
sys.path.insert(0, SDK_PATH)

from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from core.base_frame import BaseFrame
from core.themes import get_theme

try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")) as _vf:
        __version__ = _vf.read().strip()
except OSError:
    __version__ = "unknown"

LOCALMESH_URL  = "http://127.0.0.1:8801"
RETRO_MAC_PATH = os.path.expanduser("~/dev/retro-mac/retro_mac.pyw")
SCROLLSTACK_PATH = os.path.expanduser("~/forge3/scrollstack/scrollstack.py")
SHAREX = r"C:\Program Files\ShareX\ShareX.exe"
AETHERFLOW_PROFILE = os.path.expanduser("~/dev/aetherflow/profile.ps1")
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pinger.ico")

TEST_PINGS = [
    "Zug Zug! Job Done!",
    "The forge grows quiet...",
    "Picass0 rendered your portrait",
    "Agent down! Sindri needs help",
    "New quest on the board!",
    "Pebble is buzzing",
    "EC2 instance needs attention",
    "LoRA training complete",
    "Deployment finished — verify",
    "Artificer, your attention please",
]


def droid_chirp():
    def _chirp():
        import time
        patterns = [
            [(1200, 80), (800, 120), (1600, 60), (1000, 100), (1400, 150)],
            [(900, 100), (1300, 70), (700, 130), (1500, 90), (1100, 110)],
            [(1400, 60), (1000, 80), (1800, 50), (600, 140), (1200, 100)],
        ]
        for freq, dur in random.choice(patterns):
            try:
                winsound.Beep(freq, dur)
            except RuntimeError:
                pass
            time.sleep(0.05)
    threading.Thread(target=_chirp, daemon=True).start()


# Hex literals — bypass theme attr lookup to defeat BaseFrame's global QSS.
COLOR_PRIMARY = "#3e63dd"
COLOR_PURPLE  = "#8e4ec6"
COLOR_RED     = "#e5484d"
COLOR_TEXT    = "#edeef0"
COLOR_BG_ALT  = "#1b1c1e"
COLOR_BORDER  = "#2b2c2e"
COLOR_BORDER_HI = "#3a3b3e"


class RadixButton(QPushButton):
    """Padded radix button with semantic kinds; uses hex literals so BaseFrame's
    global QPushButton rule cannot override the per-button color/background."""

    # Qt QSS uses #AARRGGBB (alpha first), not CSS3's #RRGGBBAA. Use rgba().
    KIND_STYLES = {
        "primary":   (COLOR_PRIMARY,                  "#fff",       "#4f71e5"),
        "secondary": (COLOR_BG_ALT,                   COLOR_TEXT,   "#343538"),
        "danger":    ("rgba(229, 72, 77, 0.13)",      COLOR_RED,    "rgba(229, 72, 77, 0.20)"),
        "purple":    ("rgba(142, 78, 198, 0.13)",     COLOR_PURPLE, "rgba(142, 78, 198, 0.20)"),
    }

    def __init__(self, text, kind="secondary", parent=None):
        super().__init__(text, parent)
        self.setObjectName("RadixButton")
        self._apply(kind)
        self.setCursor(Qt.PointingHandCursor)

    def setKind(self, kind):
        self._apply(kind)

    def _apply(self, kind):
        bg, color, hover = self.KIND_STYLES[kind]
        border = COLOR_BORDER_HI if kind == "secondary" else "transparent"
        self.setStyleSheet(f"""
            #RadixButton {{
                background: {bg};
                color: {color};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: 600;
            }}
            #RadixButton:hover {{
                background: {hover};
                color: {color if kind != 'secondary' else COLOR_TEXT};
            }}
            #RadixButton:pressed {{
                padding: 13px 15px 11px 17px;
            }}
        """)


class Pinger(BaseFrame):
    """pinger — four-button radix control panel."""

    def __init__(self):
        self.counter = 900
        self.minimac_proc = None
        self.scrollstack_proc = None

        # Adopt-or-kill orphans from prior pinger sessions. When pinger restarts,
        # any subprocess it previously spawned (scrollstack, mini-mac) loses its
        # parent reference but the process keeps running. Multiple instances
        # fighting over the same zone is the "weird scrollstack" symptom.
        self._reapOrphans()

        super().__init__(app_name="pinger.solo", default_pct=0.18, theme="radix")
        self._reshape_titlebar()
        self.layout().activate()
        self.setFixedSize(760, self.sizeHint().height())
        self._auto_position()

    def _reshape_titlebar(self):
        """Move traffic dots to the LEFT and add version badge inline.

        BaseFrame builds: [title] [stretch] [close] [min] [pin]
        Approved layout: [close] [min] [pin] [title] [v_badge] [stretch]
        """
        header = self._root_layout.itemAt(0).widget()
        header.setFixedHeight(36)
        layout = header.layout()
        layout.setContentsMargins(12, 6, 12, 6)

        # collect all children, then reorder
        items = []
        while layout.count():
            items.append(layout.takeAt(0))

        # original order: title, stretch, dot, dot, dot
        title = items[0].widget()
        stretch = items[1]
        dots = [items[i].widget() for i in (2, 3, 4)]

        # rebuild: dots, title, badge, stretch
        for d in dots:
            layout.addWidget(d)

        # spacer between dots and title
        title.setStyleSheet(title.styleSheet() + " margin-left: 8px;")
        layout.addWidget(title)

        badge = QLabel(f"v{__version__}")
        badge.setObjectName("VersionBadge")
        badge.setFixedHeight(18)
        badge.setStyleSheet(
            f"#VersionBadge {{"
            f"  background: rgba(62, 99, 221, 0.20); color: {COLOR_PRIMARY};"
            f"  font-size: 10px; font-weight: 600;"
            f"  padding: 2px 8px; border-radius: 4px; margin-left: 6px;"
            f"}}"
        )
        layout.addWidget(badge)

        layout.addItem(stretch)

    def _reapOrphans(self):
        """Kill any python processes running scrollstack.py or retro_mac.pyw —
        they're orphans from previous pinger sessions."""
        if psutil is None:
            return
        patterns = ("scrollstack.py", "retro_mac.pyw")
        own_pid = os.getpid()
        for p in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if p.info["pid"] == own_pid:
                    continue
                if not p.info["name"] or p.info["name"].lower() not in ("python.exe", "pythonw.exe"):
                    continue
                cmd = " ".join(p.info["cmdline"] or [])
                if any(pat in cmd for pat in patterns):
                    p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def _auto_position(self):
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
        work_w = rect.right - rect.left
        work_h = rect.bottom - rect.top
        x = rect.left + (work_w - self.width()) // 2
        y = rect.top + work_h - self.sizeHint().height() - 8
        self.move(x, y)

    def build_content(self, layout):
        t = self.theme

        body = QFrame()
        body.setStyleSheet(f"background: {t.bg};")
        bv = QVBoxLayout(body)
        bv.setContentsMargins(16, 12, 16, 16)
        bv.setSpacing(8)

        controls_label = QLabel("CONTROLS")
        controls_label.setStyleSheet(
            f"color: {t.text_dim}; font-size: 10px; font-weight: 600;"
            f"letter-spacing: 1px; padding: 0 0 4px 0; border: none;"
        )
        bv.addWidget(controls_label)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.btn_ping = RadixButton("Ping!", kind="primary")
        self.btn_ping.clicked.connect(self.firePing)
        row.addWidget(self.btn_ping)

        self.btn_minimac = RadixButton("Mini-Mac", kind="secondary")
        self.btn_minimac.clicked.connect(self.toggleMinimac)
        row.addWidget(self.btn_minimac)

        self.btn_ss = RadixButton("scrollstack()", kind="purple")
        self.btn_ss.clicked.connect(self.toggleScrollstack)
        row.addWidget(self.btn_ss)

        self.btn_snap = RadixButton("snap", kind="secondary")
        self.btn_snap.clicked.connect(self.snapRegion)
        row.addWidget(self.btn_snap)

        self.btn_aether = RadixButton("aetherflow", kind="purple")
        self.btn_aether.clicked.connect(self.launchAetherflow)
        row.addWidget(self.btn_aether)

        bv.addLayout(row)
        layout.addWidget(body)

        sf = QFrame()
        sf.setStyleSheet(f"background: {t.panel}; border-top: 1px solid {t.border};")
        sl = QHBoxLayout(sf)
        sl.setContentsMargins(14, 8, 14, 8)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {t.accent_green}; font-size: 8px; border: none;")
        sl.addWidget(self.status_dot)

        self.status_label = QLabel("ready -- all services nominal")
        self.status_label.setStyleSheet(f"color: {t.text_dim}; font-size: 11px; border: none;")
        sl.addWidget(self.status_label)
        sl.addStretch()

        self.mesh_label = QLabel("localMesh :8801")
        self.mesh_label.setStyleSheet(f"color: {t.text_dim}; font-size: 11px; border: none;")
        sl.addWidget(self.mesh_label)

        layout.addWidget(sf)

    def _status(self, text, color=None):
        if color is None:
            color = self.theme.accent_green
        self.status_dot.setStyleSheet(f"color: {color}; font-size: 8px; border: none;")
        self.status_label.setText(text)

    def firePing(self):
        self.counter += 1
        title = random.choice(TEST_PINGS)
        droid_chirp()
        self._status(f"sent ping #{self.counter} -- {title}")

    def toggleMinimac(self):
        if self.minimac_proc and self.minimac_proc.poll() is None:
            self.minimac_proc.terminate()
            self.minimac_proc = None
            self.btn_minimac.setText("Mini-Mac")
            self.btn_minimac.setKind("secondary")
            self._status("mini-mac stopped")
            return

        if not os.path.exists(RETRO_MAC_PATH):
            self._status("mini-mac script not found", self.theme.accent_red)
            return
        try:
            self.minimac_proc = subprocess.Popen(
                ["pythonw", RETRO_MAC_PATH],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            self.btn_minimac.setText("stop Mini-Mac")
            self.btn_minimac.setKind("danger")
            self._status("mini-mac running")
        except Exception as e:
            self._status(f"mini-mac failed: {e}", self.theme.accent_red)

    def toggleScrollstack(self):
        if self.scrollstack_proc and self.scrollstack_proc.poll() is None:
            self.scrollstack_proc.terminate()
            self.scrollstack_proc = None
            self.btn_ss.setText("scrollstack()")
            self._status("scrollstack stopped")
            return

        if not os.path.exists(SCROLLSTACK_PATH):
            self._status("scrollstack script not found", self.theme.accent_red)
            return
        try:
            self.scrollstack_proc = subprocess.Popen(
                ["python", SCROLLSTACK_PATH,
                 "--zone", "left_third",
                 "--display", "1",
                 "--class", "CASCADIA",
                 "--scroll-from", "center_third"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            self.btn_ss.setText("stop scrollstack")
            self._status("scrollstack active")
        except Exception as e:
            self._status(f"scrollstack failed: {e}", self.theme.accent_red)

    def snapRegion(self):
        if not os.path.exists(SHAREX):
            self._status("ShareX not installed", self.theme.accent_red)
            return
        try:
            subprocess.Popen([SHAREX, "-RectangleRegion"])
            self._status("snap fired")
        except Exception as e:
            self._status(f"snap failed: {e}", self.theme.accent_red)

    def launchAetherflow(self):
        """Spawn a new pwsh console, dot-source aetherflow profile, run menu.

        aetherflow itself spawns wt tabs for the chosen persona, so we don't
        need to wrap our launch in wt. A plain new pwsh console is enough —
        and avoids the wt.exe argument-parsing mangling we hit before.
        """
        if not os.path.exists(AETHERFLOW_PROFILE):
            self._status("aetherflow profile not found", self.theme.accent_red)
            return
        # Rocky has Windows PowerShell 5.1 (powershell.exe), not pwsh (PS7).
        # aetherflow profile.ps1 is PS5.1-compatible.
        try:
            subprocess.Popen(
                ["powershell.exe", "-NoExit", "-ExecutionPolicy", "Bypass",
                 "-Command", f". '{AETHERFLOW_PROFILE}'; aetherflow"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            self._status("aetherflow launched")
        except Exception as e:
            self._status(f"aetherflow failed: {e}", self.theme.accent_red)


def main():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("artificer3120.pinger")

    app = QApplication(sys.argv)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    p = Pinger()
    if os.path.exists(ICON_PATH):
        p.setWindowIcon(QIcon(ICON_PATH))
    p.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
