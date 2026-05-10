# pinger

Radix-shelled control panel widget. Independent of untitledSDK's `shells/` folder — its own repo, own process, own version line.

Often referred to as **solo pinger** to distinguish it from **mesh pinger** (the older Win95-styled widget bundled inside [localMesh](https://github.com/artificer3120/localMesh) that AHK's `Home` key targets). Same family, different lifecycle.

## What it does

Four-button surface, radix slate theme, frameless on the untitledSDK BaseFrame.

| Button | Behavior |
|---|---|
| **Ping!** | Plays a randomized droid_chirp via `winsound.Beep` and writes a pseudo-notification line to the statusbar. Counter increments. |
| **Mini-Mac** | Toggle. Spawns `~/dev/retro-mac/retro_mac.pyw` via `pythonw`. Press again to terminate. Button colors swap secondary → danger when running. |
| **scrollstack()** | Toggle. Spawns `~/forge3/scrollstack/scrollstack.py` with the `--zone left_third --display 1 --class CASCADIA --scroll-from center_third` preset. Press again to terminate. |
| **snap** | Fires `ShareX -RectangleRegion`. Drops you into rectangle-snip mode. |

Optional dependencies degrade gracefully — a missing target script reports the failure in the statusbar instead of crashing.

## Stack

- PyQt5 frameless, on **untitledSDK** `BaseFrame(theme="radix")`
- Imports the SDK at runtime via `sys.path.insert(0, ~/dev/untitledSDK)` — no install step
- No build step required to run; `pythonw pinger.py` is the deployment

## Run

```powershell
python pinger.py        # foreground (logs to console)
pythonw pinger.py       # background (taskbar widget)
```

The widget auto-positions to bottom-center of the work area on launch.

## Requirements

- Python 3.10+
- PyQt5 ≥ 5.15
- **untitledSDK** checked out at `~/dev/untitledSDK` (the `core/base_frame.py` and `core/themes/radix.py` are required)

### Per-button optional deps

| Button | Needs |
|---|---|
| Mini-Mac | `~/dev/retro-mac/retro_mac.pyw` |
| scrollstack() | `~/forge3/scrollstack/scrollstack.py` |
| snap | `C:\Program Files\ShareX\ShareX.exe` |

## Connecting to pinger

Pinger is a Qt widget — there is **no IPC surface yet**. External tools target it the same way Windows targets any window: by title.

| What | How |
|---|---|
| Window title | `pinger` (set via `BaseFrame.app_name`) |
| App User Model ID | `artificer3120.pinger` (so it gets its own taskbar group, separate from mesh pinger's `untitledSDK.pinger`) |
| AHK example | `WinActivate "ahk_class Qt5152QWindowToolSaveBits ahk_exe pythonw.exe"` — or simpler, `WinActivate "pinger"` if no other widget is using that title |
| Click-from-script | `pyautogui` against the running window after `WinGetPos` |

**Heads-up:** mesh pinger uses the same window title (`pinger`). If both are running, `WinActivate "pinger"` grabs whichever Windows ranks first. Kill the one you don't want, or rename solo's title (edit `app_name="pinger (solo)"` in `Pinger.__init__`).

There is no `/ping` HTTP endpoint, message-bus subscription, or registry handle in this build. Adding one is part of the future direction (see below).

## Adding / removing buttons

In v0.1, buttons are **hardcoded in source**. The registry-driven model (add/remove via GUI, no code edit) is the next phase — see [docs-pinger](http://questboard-ec2.tail7f6073.ts.net:8080/?p=docs-pinger). Until then:

### Add a button

Open `pinger.py`, find `build_content()`, add a row after the existing four:

```python
self.btn_thing = RadixButton("Thing", kind="primary")  # primary | secondary | danger | purple
self.btn_thing.clicked.connect(self.doThing)
row.addWidget(self.btn_thing)
```

Then define the handler on `Pinger`:

```python
def doThing(self):
    # ... your logic
    self._status("thing fired")
```

The four `kind=` values map to the radix palette: primary (blue, the Ping! style), secondary (slate, Mini-Mac/snap), danger (red), purple (scrollstack). Add new kinds in `RadixButton.KIND_STYLES` if you need another.

If you add a fifth button to the same row, increase `setFixedSize(620, ...)` in `Pinger.__init__()` to give it room — or move to a 2-row layout by adding a second `QHBoxLayout`.

### Remove a button

Delete the four lines for that button in `build_content()` (the `RadixButton(...)` construction, the `clicked.connect()`, the `row.addWidget()`, and any state attribute used in the handler — e.g., `self.minimac_proc`). Remove the handler method if nothing else calls it. The widget will resize itself to fit on next launch (sizeHint-driven).

### Toggle vs one-shot

For a toggle button (start/stop pattern like Mini-Mac), keep a process handle on `self`, check `proc.poll() is None` for "still running," and swap `setKind()` on the button between secondary/danger to signal state. The `toggleMinimac` and `toggleScrollstack` methods are the templates.

## Layout details

- Traffic dots are placed on the **left** of the titlebar (the SDK default is right; pinger reshapes the header in `_reshape_titlebar()` after `super().__init__()`).
- Version badge sits inline with the title, blue at 20% alpha.
- Header is clamped to `setFixedHeight(36)` to prevent inner-widget reflow from bloating the titlebar.
- Widget is sized to content via `layout().activate()` + `setFixedSize(620, sizeHint().height())`, since BaseFrame's default is a square (h=w) which left a tall stretch in the middle of the body.

## Gotchas (learned the hard way)

- **Qt QSS hex with alpha is `#AARRGGBB`, not CSS3's `#RRGGBBAA`.** Writing `#8e4ec622` for "purple at 13% alpha" actually parses as alpha=0x8e, R=0x4e, G=0xc6, B=0x22 — bright green. Use `rgba()` form for any color with alpha.
- **BaseFrame sets a global `QPushButton { ... }` rule in its stylesheet.** A child's `setStyleSheet("QPushButton { ... }")` ties on specificity with the ancestor's rule. Use an ID selector (`#RadixButton { ... }`) on `setObjectName("RadixButton")` to win the cascade.
- **A bare `QLabel` inside a `QHBoxLayout` will stretch vertically** (default sizePolicy is Preferred). The version badge needs `setFixedHeight(...)` or it expands to fill the row.

## Future direction

The next phase generalizes pinger into a **registry-driven button rack** — buttons + their bound functions become entries in a JSON registry, edited via GUI; pinger becomes a portable hub that travels between mesh nodes carrying its registry, with mesh-aware routing. Concept doc + UI proposals live at:

[neonforge.untitledprojects.io/?p=docs-pinger](http://questboard-ec2.tail7f6073.ts.net:8080/?p=docs-pinger)

The current build is the v0.1 frame the future work will generalize from.

## Status

- v0.1.0 — first independent-repo build, four-button surface, radix shell.
- Repo: [artificer3120/pinger](https://github.com/artificer3120/pinger)
- Coexists with mesh pinger; they share window title `pinger`, so AHK Home-key targeting prefers whichever it finds first. Kill solo if it interferes.
