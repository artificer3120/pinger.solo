"""
pingerSLA — Timed audio alerts with agent /sla hook support

Two modes:
  1. Manual: pingerSLA.py ui     — opens timer UI (set time, note, pick bell)
  2. Agent:  pingerSLA.py fire <bell> [note]  — play bell immediately
  3. Agent:  pingerSLA.py sla <minutes> [note] — fire milestone bell at interval

Headless by default. UI only on demand.

Usage:
    python pingerSLA.py ui
    python pingerSLA.py fire completion "build done"
    python pingerSLA.py sla 15 "checking in"
"""

import sys, os, time, threading, wave, struct
from datetime import datetime, timedelta

BELLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bells")

BELL_NAMES = [
    "cyberpunk", "arcade_80s", "radio_static", "miyazaki",
    "midi_clean", "alert", "completion", "overrun", "milestone"
]


def play_bell(name):
    """Play a bell .wav file."""
    path = os.path.join(BELLS_DIR, f"{name}.wav")
    if not os.path.exists(path):
        print(f"bell not found: {name}")
        return
    try:
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
    except Exception as e:
        print(f"play error: {e}")


def fire(bell="milestone", note=""):
    """Fire a bell immediately with optional console note."""
    ts = datetime.now().strftime("%H:%M:%S")
    if note:
        print(f"[{ts}] pingerSLA: {note} [{bell}]")
    else:
        print(f"[{ts}] pingerSLA: {bell}")
    play_bell(bell)


def sla_timer(minutes, note="SLA checkpoint"):
    """Sleep for N minutes then fire milestone bell."""
    time.sleep(minutes * 60)
    fire("milestone", f"{note} ({minutes}m)")


def show_ui():
    """PyQt5 timer setup UI."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    from PyQt5.QtWidgets import (
        QApplication, QWidget, QLabel, QPushButton, QLineEdit,
        QComboBox, QVBoxLayout, QHBoxLayout, QTimeEdit, QFrame,
    )
    from PyQt5.QtCore import Qt, QTime, QTimer
    from PyQt5.QtGui import QFont, QIcon

    try:
        from core.styles import (
            SURFACE, BTN_HIGHLIGHT, BTN_SHADOW, FRAME_EDGE,
            TITLE_ACTIVE, TEXT_COLOR, FONT_NAME, raised, sunken, btn_stylesheet,
        )
    except ImportError:
        SURFACE = "#c0c0c0"
        FONT_NAME = "MS Sans Serif"

        def btn_stylesheet():
            return ""

    ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".design", "icons", "pinger.ico")

    class SLASetup(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("pingerSLA")
            self.setFixedSize(340, 260)
            self.setWindowFlags(Qt.WindowStaysOnTopHint)

            if os.path.exists(ICON_PATH):
                self.setWindowIcon(QIcon(ICON_PATH))

            self.setStyleSheet(f"background: {SURFACE}; font-family: '{FONT_NAME}';")

            layout = QVBoxLayout(self)
            layout.setSpacing(8)
            layout.setContentsMargins(12, 12, 12, 12)

            # Time picker
            time_row = QHBoxLayout()
            time_label = QLabel("fire at:")
            time_label.setFont(QFont(FONT_NAME, 9))
            self.time_edit = QTimeEdit()
            self.time_edit.setDisplayFormat("hh:mm AP")
            self.time_edit.setTime(QTime.currentTime().addSecs(900))
            self.time_edit.setFont(QFont(FONT_NAME, 10))
            time_row.addWidget(time_label)
            time_row.addWidget(self.time_edit)
            layout.addLayout(time_row)

            # Note
            note_row = QHBoxLayout()
            note_label = QLabel("note:")
            note_label.setFont(QFont(FONT_NAME, 9))
            self.note_edit = QLineEdit()
            self.note_edit.setPlaceholderText("optional note...")
            self.note_edit.setFont(QFont(FONT_NAME, 9))
            note_row.addWidget(note_label)
            note_row.addWidget(self.note_edit)
            layout.addLayout(note_row)

            # Bell picker
            bell_row = QHBoxLayout()
            bell_label = QLabel("bell:")
            bell_label.setFont(QFont(FONT_NAME, 9))
            self.bell_combo = QComboBox()
            self.bell_combo.addItems(BELL_NAMES)
            self.bell_combo.setCurrentText("miyazaki")
            self.bell_combo.setFont(QFont(FONT_NAME, 9))
            bell_row.addWidget(bell_label)
            bell_row.addWidget(self.bell_combo)
            layout.addLayout(bell_row)

            # Preview button
            btn_preview = QPushButton("preview")
            btn_preview.setFont(QFont(FONT_NAME, 9))
            btn_preview.clicked.connect(self.preview_bell)
            layout.addWidget(btn_preview)

            # Set button
            btn_set = QPushButton("set timer")
            btn_set.setFont(QFont(FONT_NAME, 10, QFont.Bold))
            btn_set.setStyleSheet("background: #000080; color: white; padding: 6px;")
            btn_set.clicked.connect(self.set_timer)
            layout.addWidget(btn_set)

            # Status
            self.status = QLabel("ready")
            self.status.setFont(QFont(FONT_NAME, 8))
            self.status.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.status)

        def preview_bell(self):
            bell = self.bell_combo.currentText()
            threading.Thread(target=play_bell, args=(bell,), daemon=True).start()

        def set_timer(self):
            target_time = self.time_edit.time()
            now = datetime.now()
            target = now.replace(
                hour=target_time.hour(),
                minute=target_time.minute(),
                second=0, microsecond=0
            )
            if target <= now:
                target += timedelta(days=1)

            wait_secs = (target - now).total_seconds()
            bell = self.bell_combo.currentText()
            note = self.note_edit.text() or "pingerSLA timer"

            def _wait_and_fire():
                time.sleep(wait_secs)
                fire(bell, note)
                # Pop up notification
                try:
                    import tkinter as tk
                    root = tk.Tk()
                    root.title("pingerSLA")
                    root.configure(bg="#0a0a0a")
                    root.geometry("350x100+600+400")
                    root.attributes("-topmost", True)
                    lbl = tk.Label(root, text=note, font=("Courier New", 16, "bold"),
                                   fg="#ff6600", bg="#0a0a0a", wraplength=320)
                    lbl.pack(expand=True)
                    root.after(8000, root.destroy)
                    root.mainloop()
                except Exception:
                    pass

            threading.Thread(target=_wait_and_fire, daemon=True).start()
            self.status.setText(f"set: {target.strftime('%I:%M %p')} [{bell}]")

    app = QApplication(sys.argv)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    w = SLASetup()
    w.show()
    app.exec_()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: pingerSLA.py [ui | fire <bell> [note] | sla <minutes> [note]]")
        print(f"bells: {', '.join(BELL_NAMES)}")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "ui":
        show_ui()

    elif cmd == "fire":
        bell = sys.argv[2] if len(sys.argv) > 2 else "milestone"
        note = sys.argv[3] if len(sys.argv) > 3 else ""
        fire(bell, note)

    elif cmd == "sla":
        minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        note = sys.argv[3] if len(sys.argv) > 3 else "SLA checkpoint"
        sla_timer(minutes, note)

    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)
