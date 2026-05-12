# DEPRECATED — DO NOT USE

> Agent reading cold: stop here. Read this whole file before opening anything else in this directory or the adjacent archive.

Every tool, script, plan, and design artifact under this directory (and inside `archives/pinger-deprecated-*.zip` next to it) is **deprecated**.

These are prior-lineage heads of the `pinger` family that were superseded during the systemCore untangling. They are kept for historical reference only.

## Hard rules

- **Do not import** anything from these files.
- **Do not extend** these scripts.
- **Do not run** these scripts.
- **Do not promote** any of these as a canonical pinger.
- **Do not use these as a starting point** for new work.
- If a task requires "pinger" functionality, the answer is **pinger.solo** — see Canonical below.

## Canonical (the only release-approved head)

**pinger.solo**

| Where | What |
|---|---|
| Live codebase | `C:\Users\ctgau\dev\pinger\` (until relocated into `solo/`) |
| Repo | `https://github.com/artificer3120/pinger` |
| Window title | `pinger.solo` |
| AHK binding | Home key (see `library/0-system/config/hotkeys.ahk`) |

Everything you need is in that repo. If you find yourself wanting something from the deprecated set, ask the operator instead.

## What's in the archive

See `../AUDIT.md` for the full classification of every file. Short version:

| Subset | Lineage |
|---|---|
| `sdk-pinger/` | untitledSDK desktop pinger + paired SLA timer (one generation behind canonical) |
| `pingle/` | older standalone in `dev/questboard/pingle/` (two generations behind canonical) |
| `designs/` | design-time docs for the SDK lineage (forge3 visualiz3r + processFlow schema) |
| `plans/` | rebuild plans that produced pinger.solo (no longer prescriptive) |

## Note on the broader codebase

The deprecated *originals* still exist at their source locations (e.g. `~/dev/untitledSDK/shells/desktop/pinger.py`). This archive does **not** delete them. If you encounter such a file in the wild, treat it the same way: deprecated, do not import or extend.

The systemCore project will address source-location cleanup separately. Until then, this NOTICE plus `AUDIT.md` are the authoritative deprecation record.

---

Recorded 2026-05-10 by gondrand (brick) under systemCore charter (`../../charter.txt`).
