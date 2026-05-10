# pinger

Radix-shelled control panel widget. Independent of the SDK shells folder — its own repo.

## Buttons (this build)

- **Ping!** — fires a droid_chirp + a random test ping into the statusbar
- **Mini-Mac** — toggle. Starts `~/dev/retro-mac/retro_mac.pyw`; press again to stop
- **scrollstack()** — toggle. Starts `~/forge3/scrollstack/scrollstack.py` with the left-third / Cascadia preset; press again to stop
- **snap** — fires `ShareX -RectangleRegion`

## Stack

- PyQt5 frameless on **untitledSDK** `BaseFrame(theme="radix")`
- Imports the SDK from `~/dev/untitledSDK` at runtime via `sys.path.insert`
- No build step — run from source

## Run

```
python pinger.py
pythonw pinger.py    # background
```

## Requirements

- Python 3.10+
- PyQt5
- untitledSDK checked out at `~/dev/untitledSDK`
- Optional, per-button:
  - retro-mac at `~/dev/retro-mac/retro_mac.pyw`
  - scrollstack at `~/forge3/scrollstack/scrollstack.py`
  - ShareX at `C:\Program Files\ShareX\ShareX.exe`

Missing optional deps degrade gracefully — the button reports the failure in the statusbar and stays usable.

## Status

v0.1.0 — first independent-repo build. Future direction in `docs-pinger` on questboard-ec2 (registry-driven, mobile detachable hub).
