"""
UntitledSDK — pinger2 (framed)

Test control panel for Pingle notifications + Mini-Mac + scrollStack.
Built on SDK frame with titlebar (minimize + close), button body, status bar.

Usage:
    python pinger.py
    pythonw pinger.py    # background
"""

import sys
import os
import random
import subprocess
import winsound
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame,
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QIcon

from core.styles import (
    SURFACE, BTN_HIGHLIGHT, BTN_SHADOW, BTN_FACE, FRAME_EDGE,
    TITLE_ACTIVE, TITLE_ACTIVE_LIGHT, TEXT_COLOR, FONT_NAME,
    MARLETT_FONT, raised, sunken, btn_stylesheet,
)
from elements.button import SDKButton

QB_URL = "https://questboard-ec2.tail7f6073.ts.net"
RETRO_MAC_PATH = os.path.join(os.path.expanduser("~"), "dev", "retro-mac", "retro_mac.pyw")
SCROLLSTACK_PATH = os.path.join(os.path.expanduser("~"), "forge3", "scrollstack", "scrollstack.py")
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".design", "icons", "pinger.ico")


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
        beeps = random.choice(patterns)
        for freq, dur in beeps:
            winsound.Beep(freq, dur)
            time.sleep(0.05)
    threading.Thread(target=_chirp, daemon=True).start()


class TitleBarControl(QPushButton):
    """Marlett window control button."""
    def __init__(self, marlett_char, parent=None):
        super().__init__(marlett_char, parent)
        self.setFixedSize(16, 14)
        self.setFont(QFont(MARLETT_FONT, 7))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE};
                border: none;
                border-top: 1px solid {BTN_HIGHLIGHT};
                border-left: 1px solid {BTN_HIGHLIGHT};
                border-right: 1px solid {BTN_SHADOW};
                border-bottom: 1px solid {BTN_SHADOW};
                padding: 0;
                font-family: Marlett;
                font-size: 8px;
            }}
            QPushButton:pressed {{
                border-top: 1px solid {BTN_SHADOW};
                border-left: 1px solid {BTN_SHADOW};
                border-right: 1px solid {BTN_HIGHLIGHT};
                border-bottom: 1px solid {BTN_HIGHLIGHT};
            }}
        """)


class TitleBar(QWidget):
    """Draggable titlebar with minimize + close."""
    def __init__(self, title="pinger", parent=None):
        super().__init__(parent)
        self.setFixedHeight(18)
        self._drag_pos = None
        self._parent = parent

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(1)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont(FONT_NAME, 8, QFont.Bold))
        self.title_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.btn_min = TitleBarControl("0")
        self.btn_close = TitleBarControl("r")
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_close)

        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(TITLE_ACTIVE))
        gradient.setColorAt(1, QColor(TITLE_ACTIVE_LIGHT))
        painter.fillRect(self.rect(), gradient)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self._parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self._parent.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class StatusBar(QWidget):
    """Sunken Win95 status bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(18)
        self.setStyleSheet(f"background: {SURFACE};")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(2, 1, 2, 1)
        self._layout.setSpacing(4)
        self._fields = []
        self.set_fields(["Ready"])

    def set_fields(self, texts):
        for f in self._fields:
            self._layout.removeWidget(f)
            f.deleteLater()
        self._fields = []
        for text in texts:
            label = QLabel(text)
            label.setFont(QFont(FONT_NAME, 7))
            label.setStyleSheet(f"""
                color: {TEXT_COLOR}; background: {SURFACE};
                border-top: 1px solid {BTN_SHADOW};
                border-left: 1px solid {BTN_SHADOW};
                border-right: 1px solid {BTN_HIGHLIGHT};
                border-bottom: 1px solid {BTN_HIGHLIGHT};
                padding: 1px 4px;
            """)
            self._layout.addWidget(label)
            self._fields.append(label)



class Pinger(QWidget):
    """pinger2 — framed widget with titlebar, button body, status bar."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(550, 100)

        self.counter = 900
        self.minimac_proc = None
        self.scrollstack_proc = None

        # Outer frame (raised border)
        self.setStyleSheet(f"background: {SURFACE}; {raised()}")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(0)

        # Inner border
        inner = QFrame()
        inner.setStyleSheet(f"QFrame {{ border: 1px solid {BTN_SHADOW}; background: {SURFACE}; }}")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        # Title bar
        self.titlebar = TitleBar("pinger", parent=self)
        self.titlebar.btn_close.clicked.connect(self.close)
        self.titlebar.btn_min.clicked.connect(self.showMinimized)
        inner_layout.addWidget(self.titlebar)

        # Body — button row
        body = QWidget()
        body.setStyleSheet(f"background: {SURFACE};")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(6, 6, 6, 6)
        body_layout.setSpacing(6)

        btn_ping = SDKButton("Ping!")
        btn_ping.clicked.connect(self.fire_ping)
        body_layout.addWidget(btn_ping)

        btn_minimac = SDKButton("Mini-Mac")
        btn_minimac.clicked.connect(self.start_minimac)
        body_layout.addWidget(btn_minimac)

        btn_stop = SDKButton("Stop Mini-Mac")
        btn_stop.clicked.connect(self.stop_minimac)
        body_layout.addWidget(btn_stop)

        self.ss_btn = SDKButton("scrollstack()")
        self.ss_btn.clicked.connect(self.toggle_scrollstack)
        body_layout.addWidget(self.ss_btn)

        btn_snap = SDKButton("snap.region()")
        btn_snap.clicked.connect(self.snap_region)
        body_layout.addWidget(btn_snap)

        inner_layout.addWidget(body)

        # Status bar
        self.statusbar = StatusBar()
        inner_layout.addWidget(self.statusbar)

        main_layout.addWidget(inner)

        # Auto-position bottom center
        import ctypes.wintypes
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
        work_w = rect.right - rect.left
        work_h = rect.bottom - rect.top
        x = rect.left + (work_w - self.width()) // 2
        y = rect.top + work_h - self.height()
        self.move(x, y)


    def fire_ping(self):
        self.counter += 1
        title = random.choice(TEST_PINGS)
        droid_chirp()
        self.statusbar.set_fields([f"Ping #{self.counter}", title])

    def start_minimac(self):
        if self.minimac_proc and self.minimac_proc.poll() is None:
            return
        self.minimac_proc = subprocess.Popen(
            ["pythonw", RETRO_MAC_PATH],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        self.statusbar.set_fields(["Mini-Mac running"])

    def stop_minimac(self):
        if self.minimac_proc and self.minimac_proc.poll() is None:
            self.minimac_proc.terminate()
            self.minimac_proc = None
            self.statusbar.set_fields(["Mini-Mac stopped"])

    def snap_region(self):
        SHAREX = r"C:\Program Files\ShareX\ShareX.exe"
        subprocess.Popen([SHAREX, "-RectangleRegion"])
        self.statusbar.set_fields(["snap.region() fired"])

    def toggle_scrollstack(self):
        if self.scrollstack_proc and self.scrollstack_proc.poll() is None:
            self.scrollstack_proc.terminate()
            self.scrollstack_proc = None
            self.ss_btn.label_text = "scrollstack()"
            self.ss_btn.setStyleSheet(btn_stylesheet())
            self.statusbar.set_fields(["scrollStack stopped"])
        else:
            self.scrollstack_proc = subprocess.Popen(
                ["python", SCROLLSTACK_PATH,
                 "--zone", "left_third",
                 "--display", "1",
                 "--class", "CASCADIA",
                 "--scroll-from", "center_third"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            self.ss_btn.label_text = "stop scrollstack"
            self.ss_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #800080;
                    color: #ffffff;
                    font-family: "{FONT_NAME}", Arial, sans-serif;
                    font-size: 11px;
                    padding: 4px 12px;
                    {raised()}
                }}
                QPushButton:hover {{ background: #9a009a; }}
                QPushButton:pressed {{ {sunken()} padding: 5px 11px 3px 13px; }}
            """)
            self.statusbar.set_fields(["scrollStack active"])


def main():
    # Set AppUserModelID so Windows gives pinger its own taskbar identity
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("untitledSDK.pinger")

    app = QApplication(sys.argv)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    pinger = Pinger()
    if os.path.exists(ICON_PATH):
        pinger.setWindowIcon(QIcon(ICON_PATH))
    pinger.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
