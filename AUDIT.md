# pinger — lineage audit

> **Status:** open audit. Operator-approved canonical head is **pinger.solo**.
> Everything else in this directory is staged for deprecation: keep for reference, do not import, do not extend, do not run.

Auditor: gondrand (brick) · Date: 2026-05-10 · Charter: `../../charter.txt`

---

## Canonical (release-approved)

| Head | Local path (live) | Repo | Status |
|---|---|---|---|
| **pinger.solo** | `C:\Users\ctgau\dev\pinger\` | `artificer3120/pinger` (main, 88a646b) | live, running PID 24556 |

`solo/` in this directory is intentionally empty until the live relocation is approved by the operator. The canonical codebase remains at `~/dev/pinger/` with a working git remote and an active AHK binding (Home key). Source of truth is the repo, not this audit dir.

### What pinger.solo actually requires

- **Itself**: `~/dev/pinger/pinger.py`, `pinger.ico`, `requirements.txt`, `VERSION`, `README.md`, `.gitignore`
- **untitledSDK radix theme** (sibling dependency, not a pinger head): `~/dev/untitledSDK/core/themes/radix.py`
- **Spawn targets** (these are *targets* of pinger buttons, not parts of pinger):
  - `~/dev/retro-mac/retro_mac.pyw` (Mini-Mac button)
  - `~/forge3/scrollstack/scrollstack.py` (scrollstack button)
  - `C:\Program Files\ShareX\ShareX.exe` (snap button)
- **AHK binding**: `C:\Users\ctgau\library\0-system\config\hotkeys.ahk` lines 28-47 (Home key toggle)

Anything not in that list is a candidate for deprecation.

---

## Deprecated heads

> Packaged into `archives/pinger-deprecated-2026-05-10.zip`. A discovery-time `NOTICE.md` sits next to the zip and is also mirrored inside it. The loose tree was removed after archival to prevent file-by-file cherry-picking.

### `sdk-pinger/` (in archive) — untitledSDK desktop pinger

| File | Origin |
|---|---|
| `pinger.py` | `dev/untitledSDK/shells/desktop/pinger.py` |
| `pingerSLA.py` | `dev/untitledSDK/shells/desktop/pingerSLA.py` |
| `pinger-logic-tree.txt` | same dir |
| `pinger.ico` | `dev/untitledSDK/shells/desktop/.design/icons/pinger.ico` |

Lineage: SDK-framed 5-button pinger with a paired SLA timer widget. Per memory `project_pinger_promote.md` (2026-05-02), this pair was at one point proposed as the canonical promotion target. That direction was overtaken by pinger.solo. Do not promote.

### `pingle/` (in archive) — questboard standalone pinger

| File | Origin |
|---|---|
| `pinger.pyw` | `dev/questboard/pingle/pinger.pyw` |

Lineage: older standalone in the questboard tree. Same memory above flags it as superseded by SDK pinger due to code drift; SDK pinger was then itself superseded by pinger.solo. Two generations behind canonical.

### `designs/` (in archive) — design artifacts for the SDK lineage

| File | Origin |
|---|---|
| `pinger-sdk.processFlow-schema.json` | `forge3/processFlow/schemas/pinger-sdk.json` |
| `pinger-sdk.visualiz3r.html` | `forge3/visualiz3r/development/pinger-sdk.html` |
| `pinger-sdk.visualiz3r.json` | `forge3/visualiz3r/development/pinger-sdk.json` |
| `pinger-sdk-review-04262026.jpg` | `forge3/visualiz3r/customer feedback/pinger-sdk-review-04262026.jpg` |

Lineage: design-time docs for SDK pinger (the `-sdk` suffix dates them to that head). Filed here so the design trail follows the deprecated codeset.

### `plans/` (in archive) — rebuild plans

| File | Origin |
|---|---|
| `pinger-rebuild-plan.md` | `dev/untitledSDK/plans/pinger-rebuild-plan.md` |
| `pinger-rebuild-plan.md.provenance.json` | same dir |
| `pinger-rebuild-plan.library-mirror.md` | `library/1-source/untitledSDK/docs/plans/pinger-rebuild-plan.md` (likely a mirror of the above; same byte count) |

Lineage: planning docs for the SDK-pinger rebuild that became pinger.solo. Reference value, no longer prescriptive.

---

## Adjacent — NOT a pinger head, flagged for clarity

### Mesh pinger (inside theMesh)

`~/dev/localMesh/` bundles a "mesh pinger" UI as part of the localMesh service. It shares the `pinger` window-title family with solo but is a different tool entirely (maps to **theMesh** in the systemCore charter, not to pinger). Not staged here.

This name collision is exactly the scope-blob the systemCore project exists to untangle. When solo relocates and theMesh stabilizes, recommend renaming mesh pinger's window class to remove the ambiguity.

---

## Cross-reference: what still points at deprecated heads

Quick spot-check of live references — not exhaustive:

- AHK `library/0-system/config/hotkeys.ahk` — points at solo only ✓
- untitledSDK still ships `shells/desktop/pinger.py` + `pingerSLA.py` in tree — anything importing those is on a deprecated head
- forge3 design artifacts — passive, no live consumer

A full grep for `pinger` across `~/dev/` and `~/library/` should be run before promotion to release. Out of scope for this initial audit pass.

---

## Open decisions for the operator

1. **Live relocation of pinger.solo** — leave at `~/dev/pinger/` or move into `solo/` here? Move requires brief downtime + AHK path update.
2. **Originals** — do the deprecated originals stay where they are (this dir is the canonical archive copy) or get removed from their source locations after this is approved?
3. **Mesh-pinger rename** — defer to theMesh stabilization, or schedule now to kill the name collision?
