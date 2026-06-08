# requirements-decompose

Ingests messy requirements documents and decomposes them into structured, traceable requirements across firmware, backend, and UI layers. Designed for embedded + instrumentation systems (STM32-class firmware, Python backends, Electron/Vue UIs).

## What it does

- Cleans up informal/incomplete requirement docs
- Accepts Polarion PDF exports (converted via markitdown) — preserves source IDs (REQ-NNN, SWR-NNN) for traceability back to Polarion
- Accepts an architecture analysis doc (`--arch`) alongside requirements to confirm existing implementations and avoid re-specifying what already exists
- Tags inferred requirements as `[INFERRED]` — never silently fills gaps
- Tags architecture-confirmed items as `[CONFIRMED-BY-ARCH]` / `[EXISTS-IN-ARCH]`
- Flags ambiguities and conflicts for user resolution
- Produces layered requirements: SYS → FW / SW / UI → COMP
- Generates API boundary contracts at every communication seam
- Outputs a full traceability matrix (forward + reverse), including Polarion source IDs
- Populates existing component-level skeleton docs (`--populate-templates`) — never touches upstream/Polarion docs

## Requirement ID scheme

| Prefix | Layer |
|--------|-------|
| `SYS-NNN` | System-level |
| `FW-NNN` | Firmware |
| `SW-NNN` | Backend (Python) |
| `UI-NNN` | UI (Electron/Vue or Python) |
| `API-NNN` | API boundary contract |
| `COMP-NNN` | Component-level |

**Source ID preservation**: `SYS-001 [←REQ-042]` — Polarion/DOORS IDs carried through to traceability matrix.

## Usage

```
/req-decompose <doc-path-or-paste> [--domain firmware|backend|ui|full-stack] [--scope fw,backend] [--api-contract] [--arch <path>] [--populate-templates <dir>]
```

**Examples:**

```
# Auto-detect domain from doc
/req-decompose specs/system-brief.md

# Firmware + backend only, with architecture doc for context
/req-decompose specs/system-brief.md --scope firmware,backend --arch docs/architecture-analysis.md

# Polarion PDF export (converted via markitdown automatically)
/req-decompose exports/polarion-srs.pdf --domain full-stack

# Populate existing component skeleton docs after decomposition
/req-decompose specs/system-brief.md --populate-templates docs/components/

# Full run: Polarion + arch + template population
/req-decompose exports/polarion-srs.pdf --arch docs/architecture-analysis.md --populate-templates docs/components/

# Delta analysis: what's new, outdated, or changed vs existing SYS requirements
/req-decompose specs/updated-product-brief.md --baseline docs/system-requirements-v1.md

# Full delta run: updated product brief + arch context + baseline comparison
/req-decompose specs/updated-product-brief.md --arch docs/architecture-analysis.md --baseline docs/system-requirements-v1.md
```

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--domain` | auto-detect | Force domain: `firmware`, `backend`, `ui`, `full-stack` |
| `--scope` | all detected layers | Comma-list of layers to decompose |
| `--api-contract` | auto (emitted when 2+ layers in scope) | Always emit API boundary specs |
| `--arch <path>` | none | Architecture analysis doc — enriches inferences, tags existing implementations |
| `--baseline <path>` | none | Existing SYS requirements doc — triggers delta analysis (NEW / UNCHANGED / NEEDS-UPDATE / OUTDATED) |
| `--populate-templates <dir>` | none | Directory of component skeleton docs to populate with COMP reqs |

## Input formats

| Format | How handled |
|--------|-------------|
| Markdown / plain text | Read directly |
| `.docx` | Converted via markitdown MCP |
| `.pdf` (including Polarion exports) | Converted via markitdown MCP; Polarion IDs preserved |
| Pasted text | Read from `$ARGUMENTS` |

## Output

A single `requirements-<name>-<date>.md` file containing:
1. System requirements (SYS), with source IDs if from Polarion
2. Layer requirements (FW / SW / UI) for layers in scope
3. API contracts for each communication seam
4. Component requirements with file-level assignments
5. Traceability matrix (forward + reverse), including source IDs column
6. Architecture notes (if `--arch` used)
7. Requirements delta (if `--baseline` used): NEW / UNCHANGED / NEEDS-UPDATE / OUTDATED with mapping table
8. Open items (ambiguities, conflicts, gaps)

If `--populate-templates` used: template population report listing updated files and unmatched COMP reqs.

## Components

| Component | Role |
|-----------|------|
| `req-decompose` skill | Orchestrator — parses input, dispatches agents, assembles output |
| `req-classifier` agent | Extracts SYS reqs; detects Polarion IDs; cross-references architecture doc |
| `sys-diff` agent | Diffs fresh SYS reqs against an existing baseline; produces delta report (NEW / UNCHANGED / NEEDS-UPDATE / OUTDATED) |
| `fw-decomposer` agent | Decomposes to FW reqs (bare-metal + RTOS, STM32-focused); arch-aware |
| `backend-decomposer` agent | Decomposes to SW reqs (Python drivers, FastAPI, image pipeline); arch-aware |
| `ui-decomposer` agent | Decomposes to UI reqs (Electron+Vue, IPC, WebSocket/REST consumption); arch-aware |
| `api-contract` agent | Generates API boundary specs for firmware↔backend and backend↔UI seams |
| `component-mapper` agent | Maps layer reqs to source files, produces traceability matrix; dispatches template-populator |
| `template-populator` agent | Writes COMP reqs into component skeleton docs; never touches upstream docs |
