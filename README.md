# pinger

> **For agents reading this cold:** this is **solo pinger**, an independent radix-shelled control panel widget at `~/dev/pinger/`. It is NOT the same as **mesh pinger**, which lives inside `~/dev/localMesh/` and is bundled into the localMesh server. They share the window title `pinger`. AHK's `Home` key targets mesh pinger, not this one. When the operator says "pinger" without a qualifier, ask which one they mean before acting.

| Attribute | Value |
|---|---|
| Repo | [artificer3120/pinger](https://github.com/artificer3120/pinger) |
| Local path | `C:\Users\ctgau\dev\pinger\` |
| Entry point | `pinger.py` |
| Window title | `pinger.solo` (distinct from mesh pinger's `pinger`) |
| AppUserModelID | `artificer3120.pinger` |
| AHK Home key | bound to solo pinger toggle (see `hotkeys.ahk`) |
| Version | see `VERSION` file (currently `0.1.0`) |
| Theme | radix (from `~/dev/untitledSDK/core/themes/radix.py`) |
| Concept doc | [docs-pinger on neonforge](http://questboard-ec2.tail7f6073.ts.net:8080/?p=docs-pinger) |

---

## What it does

Four-button radix control panel. Each button is hardcoded in `build_content()`; future direction is registry-driven (see docs-pinger).

| Button | Kind | Behavior |
|---|---|---|
| **Ping!** | primary | Plays a randomized `winsound.Beep` chirp; writes a pseudo-notification to the statusbar; increments counter. Local only — does NOT call localMesh. |
| **Mini-Mac** | toggle (secondary ↔ danger) | Spawns `~/dev/retro-mac/retro_mac.pyw` via `pythonw`; second press calls `proc.terminate()`. |
| **scrollstack()** | toggle (purple) | Spawns `~/forge3/scrollstack/scrollstack.py` with the `--zone left_third --display 1 --class CASCADIA --scroll-from center_third` preset; second press terminates. |
| **snap** | secondary | Fires `C:\Program Files\ShareX\ShareX.exe -RectangleRegion`. |

Optional deps degrade gracefully — missing target script writes a red statusbar line, does NOT crash.

---

## Run

```powershell
# foreground (logs to console)
python C:\Users\ctgau\dev\pinger\pinger.py

# background (taskbar widget, what the operator usually wants)
pythonw C:\Users\ctgau\dev\pinger\pinger.py
```

The widget auto-positions to bottom-center of the work area on launch. It uses `Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint`. Drag the titlebar to move; drag the edges to resize (invisible grips, last 4–16px of each side).

---

## Required deps

- **Python 3.10+**
- **PyQt5 ≥ 5.15** — `pip install PyQt5`
- **untitledSDK** checked out at `C:\Users\ctgau\dev\untitledSDK\` — pinger imports `core.base_frame.BaseFrame` and `core.themes.get_theme` from there. The SDK path is hardcoded in `pinger.py` line ~21 (`SDK_PATH = os.path.expanduser("~/dev/untitledSDK")`).

## Optional deps (per button)

| Button | Required path |
|---|---|
| Mini-Mac | `C:\Users\ctgau\dev\retro-mac\retro_mac.pyw` |
| scrollstack() | `C:\Users\ctgau\forge3\scrollstack\scrollstack.py` |
| snap | `C:\Program Files\ShareX\ShareX.exe` |

If the path is missing, the button still renders and is clickable, but reports a red error to the statusbar instead of acting.

---

## Targeting from outside

Solo pinger has **no HTTP / IPC surface**. External agents target it via window manipulation only.

- **AHK / WinActivate**: `WinActivate "pinger.solo"` finds it unambiguously. The `Home` key in `library/0-system/config/hotkeys.ahk` is the canonical launcher (toggle pattern: kills if running, launches if not).
- **AppUserModelID**: solo's is `artificer3120.pinger`, mesh's is `untitledSDK.pinger`. Use this if you need to target via Win32 `Shell_NotifyIcon` or jump-list APIs.
- **Click-from-script**: `pyautogui` after `WinGetPos`. The button row is laid out left-to-right in the order Ping / Mini-Mac / scrollstack / snap.

There is no `/ping` HTTP endpoint, mesh registration, or pub/sub hook. The statusbar shows `localMesh :8801` as a static label — pinger does NOT actually connect to localMesh in this build.

---

## Adding a button

Editing `pinger.py` is the only way in v0.1. Three changes:

**1. In `Pinger.build_content()`, add to the `row = QHBoxLayout()` block:**

```python
self.btn_thing = RadixButton("Thing", kind="primary")
self.btn_thing.clicked.connect(self.doThing)
row.addWidget(self.btn_thing)
```

`kind=` must be one of: `primary` (blue), `secondary` (slate), `danger` (red), `purple`. Add new kinds in `RadixButton.KIND_STYLES` if you need another color — use `rgba(r, g, b, 0.13)` form for backgrounds with alpha, NOT `#RRGGBBAA` (see Gotchas below).

**2. Define the handler as a method on `Pinger`:**

```python
def doThing(self):
    # ... your logic
    self._status("thing fired")
```

The `_status(text, color=None)` helper updates the statusbar. Pass `self.theme.accent_red` as color for errors.

**3. If adding a 5th+ button to the same row,** increase the widget width at `Pinger.__init__()`:

```python
self.setFixedSize(620, self.sizeHint().height())
#                ^^^ bump this for more buttons in one row
```

For a 2-row layout, add a second `QHBoxLayout()` and `bv.addLayout(row2)` after the first. The widget will grow vertically via `sizeHint().height()` automatically.

---

## Removing a button

In `Pinger.build_content()`, delete:
1. The `RadixButton(...)` construction
2. The `clicked.connect(...)` call
3. The `row.addWidget(...)` call

In `Pinger`:
4. The handler method (e.g., `def snapRegion(self): ...`)
5. Any state attribute used by the handler (e.g., `self.minimac_proc = None` in `__init__`)

The widget resizes itself on next launch — no manual width adjustment needed.

---

## Toggle button pattern

For start/stop behavior (like Mini-Mac), the template is:

```python
def toggleX(self):
    if self.x_proc and self.x_proc.poll() is None:   # running → stop
        self.x_proc.terminate()
        self.x_proc = None
        self.btn_x.setText("X")
        self.btn_x.setKind("secondary")
        self._status("x stopped")
        return

    # not running → start
    if not os.path.exists(X_PATH):
        self._status("x script not found", self.theme.accent_red)
        return
    try:
        self.x_proc = subprocess.Popen([...], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        self.btn_x.setText("stop X")
        self.btn_x.setKind("danger")
        self._status("x running")
    except Exception as e:
        self._status(f"x failed: {e}", self.theme.accent_red)
```

Initialize `self.x_proc = None` in `Pinger.__init__()`.

---

## Layout invariants — DO NOT break

These are load-bearing for the radix shell to look right:

- `header.setFixedHeight(36)` in `_reshape_titlebar()` — without this, the QFrame stretches when inner widgets resize, bloating the titlebar.
- `self.layout().activate()` then `self.setFixedSize(620, self.sizeHint().height())` at end of `__init__()` — without this, BaseFrame's `h = w` default leaves a 620-tall widget with empty middle.
- `badge.setFixedHeight(18)` in `_reshape_titlebar()` — without this, the QLabel stretches vertically inside its QHBoxLayout (default sizePolicy is Preferred → expand).
- `self.setObjectName("RadixButton")` in `RadixButton.__init__()` and `#RadixButton { ... }` selector in `_apply()` — without this, BaseFrame's global `QPushButton { ... }` rule wins on cascade and overrides per-button colors.

---

## Gotchas (these will burn you again if you don't know)

- **Qt QSS uses `#AARRGGBB` (alpha first), NOT CSS3's `#RRGGBBAA`.** Writing `#8e4ec622` for "purple at 13% alpha" actually parses as alpha=0x8e, R=0x4e, G=0xc6, B=0x22 → bright green. Always use `rgba(r, g, b, 0.13)` for QSS color values with alpha. Never copy hex-with-alpha from CSS3 mockups directly.
- **BaseFrame's stylesheet sets a global `QPushButton { ... }` rule** at `~/dev/untitledSDK/core/base_frame.py` lines 95–104. Any QPushButton descendant inherits it unless overridden by a more specific selector. ID selectors (`#RadixButton`) win over typename selectors (`QPushButton`).
- **BaseFrame defaults to a square widget** (`h = w` at line 74 of `base_frame.py`). Setting `setFixedWidth(620)` alone leaves you with `620×620`; the middle of the body stretches. Always pair width with `sizeHint().height()` after `layout().activate()`.
- **`QLabel` default vertical sizePolicy is Preferred → Expanding inside HBox.** Any pill/badge label needs `setFixedHeight(...)` or it grows to fill the row, which then triggers a feedback loop where the row height grows because the badge filled it.

---

## Future direction

Next phase generalizes pinger into a **mobile detachable hub** — buttons + bound functions become entries in a JSON registry, edited via GUI, and the rack travels between mesh nodes carrying its registry, with mesh-aware routing via a `scope` field. Concept + diagrams + UI proposals at:

[neonforge.untitledprojects.io/?p=docs-pinger](http://questboard-ec2.tail7f6073.ts.net:8080/?p=docs-pinger)

The current build is the v0.1 frame the future work will generalize from. When working on solo pinger toward the registry model, read docs-pinger first.

---

## Status

- v0.1.0 — first independent-repo build, four-button surface, radix shell.
- Coexists with mesh pinger; same window title. Operator decides which to keep running.
- No tests, no CI, no PyInstaller spec. Run from source.
