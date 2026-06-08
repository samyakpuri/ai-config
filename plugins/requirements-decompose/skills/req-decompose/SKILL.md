---
name: req-decompose
description: >-
  This skill should be used when the user wants to decompose, structure, or extract requirements from any document — product briefs, specs, firmware docs, Polarion PDF exports, or informal notes — or compare an updated requirements document against an existing baseline to identify what is new, outdated, or changed. Triggers on: "decompose requirements", "break down this spec", "extract requirements", "generate requirements from this doc", "requirements traceability", "parse this PRD", "spec this feature", "use this Polarion export", "populate component templates", "compare requirements against baseline", "diff requirements", "requirements delta", "identify outdated requirements", "what's missing from our system requirements", or any request to convert a raw document into layered SYS/FW/SW/UI/API/COMP requirements. Full trigger list: references/triggers.md.
argument-hint: "<doc-path-or-paste> [--domain firmware|backend|ui|full-stack] [--scope firmware,backend,...] [--api-contract] [--arch <path>] [--baseline <path>] [--populate-templates <dir>]"
allowed-tools: Read, mcp__markitdown__convert_to_markdown, mcp_markitdown_convert_to_markdown
---

## Dependencies

Sub-agents (same plugin):
- `requirements-decompose:req-classifier` — cleans input, extracts SYS-NNN requirements, preserves Polarion source IDs
- `requirements-decompose:sys-diff` — diffs fresh SYS reqs against an existing baseline; tags NEW, UNCHANGED, NEEDS-UPDATE, and OUTDATED (dispatched after req-classifier when `--baseline` is provided)
- `requirements-decompose:fw-decomposer` — decomposes to FW-NNN (firmware layer)
- `requirements-decompose:backend-decomposer` — decomposes to SW-NNN (Python backend layer)
- `requirements-decompose:ui-decomposer` — decomposes to UI-NNN (Electron/Vue/Python UI layer)
- `requirements-decompose:api-contract` — generates API-NNN boundary specs between layer seams
- `requirements-decompose:component-mapper` — maps all layer reqs to COMP-NNN with traceability matrix
- `requirements-decompose:template-populator` — writes COMP reqs into existing component skeleton docs (dispatched by component-mapper when `--populate-templates` is set)

---

## Role

Act as a senior systems engineer. Treat the input as authoritative but incomplete — your job is to surface what's missing, make inferences explicit, and produce requirements that an engineer can implement without ambiguity. Never silently fill gaps; always tag inferred content as `[INFERRED]`.

---

## Input

Accept one of:
- File path to a requirements doc (`.md`, `.txt`, `.docx` via markitdown MCP, `.pdf` via markitdown MCP)
- Pasted raw text in `$ARGUMENTS`
- A mix (file + clarifying notes)

**Polarion PDFs**: Convert via `markitdown` MCP tool. Polarion exports contain structured req IDs (e.g. `REQ-042`, `SWR-007`) — these are preserved as source IDs alongside SYS-NNN for traceability back to Polarion.

**Flags** (parsed from `$ARGUMENTS`):
- `--domain firmware|backend|ui|full-stack` — override auto-detection; default: auto-detect
- `--scope <comma-list>` — restrict layers to decompose (e.g. `--scope firmware,backend`); omit = all detected layers
- `--api-contract` — always emit API boundary specs, even for single-layer runs
- `--arch <path>` — path to an architecture analysis doc (codebase analysis, design doc, existing driver inventory); used alongside the requirements doc to enrich inferences and confirm existing implementations
- `--baseline <path>` — path to an existing SYS requirements document; triggers sys-diff after req-classifier to produce a delta report (NEW / UNCHANGED / NEEDS-UPDATE / OUTDATED) before layer decomposition
- `--populate-templates <dir>` — directory containing component-level skeleton docs to populate with COMP reqs; never touches SYS/FW/SW/UI/API-level docs

---

## Requirement ID Scheme

| Prefix | Layer | Example |
|--------|-------|---------|
| `SYS` | System-level | `SYS-001` |
| `FW` | Firmware | `FW-001` |
| `SW` | Backend (Python) | `SW-001` |
| `UI` | UI (Electron/Vue/Python) | `UI-001` |
| `API` | API boundary contract | `API-001` |
| `COMP` | Component-level | `COMP-FW-001` |

IDs are zero-padded to 3 digits, sequential per prefix, stable across runs (same input → same IDs).

**Source ID preservation**: When input has existing structured IDs (Polarion `REQ-NNN`, `SWR-NNN`, etc.), every derived SYS req carries the source ID: `SYS-001 [←REQ-042]`. This preserves traceability back to the authoritative source.

**Tags**:
- `[INFERRED]` — requirement not stated explicitly; derived from context or other requirements
- `[AMBIGUOUS]` — requirement stated but underspecified; flagged for user clarification
- `[CONFLICT]` — contradicts another requirement; both flagged with cross-reference
- `[CONFIRMED-BY-ARCH]` — inference validated by the architecture doc (not just inferred)
- `[EXISTS-IN-ARCH]` — component or interface already implemented per the architecture doc

---

## Workflow

### 1. Parse input

Read the provided requirements file or text. If a `.docx` or `.pdf` is referenced, convert using `markitdown` MCP tool; otherwise ask the user to paste the content.

If `--arch <path>` is provided, read the architecture doc now as a separate document. Do not merge it with the requirements — keep them as distinct inputs throughout.

### 2. Detect domain

If `--domain` is not specified, detect from content:
- Firmware indicators: MCU names, register maps, ISR, RTOS, HAL, peripheral names, timing budgets, baud rates
- Backend indicators: API, endpoint, Python, driver, serial, USB, image, frame, FastAPI, protocol
- UI indicators: screen, button, display, user, panel, Vue, Electron, event, WebSocket

If `--arch` is provided, also scan the architecture doc for domain signals — it may reveal layers not mentioned in the requirements doc.

Set active layers. If `--scope` is provided, intersect with detected layers.

### 3. Dispatch req-classifier

Launch `requirements-decompose:req-classifier` with:
- `raw_doc`: the requirements text
- `arch_doc`: architecture doc content (if `--arch` provided; pass `null` otherwise)
- `domain_hints`: detected layer tags

Wait for it to return:
- Cleaned system-level requirements list (SYS-NNN), with source IDs preserved if input is Polarion-format
- Inferred requirements list (tagged `[INFERRED]`)
- Architecture-confirmed items (tagged `[CONFIRMED-BY-ARCH]`)
- Ambiguity and conflict flags

**If `--baseline` was NOT provided:** present the SYS-level list to the user and get confirmation before decomposing. If there are `[AMBIGUOUS]` items, ask the user to resolve them now. If user says "proceed anyway", tag them and continue. If the user requests changes, re-dispatch `req-classifier` with corrections appended and repeat until confirmed.

**If `--baseline` was provided:** proceed to step 4 before presenting to the user.

### 4. Dispatch sys-diff (if `--baseline` provided)

Launch `requirements-decompose:sys-diff` with:
- `new_sys_reqs`: the SYS-NNN list returned by req-classifier
- `baseline_reqs`: contents of the `--baseline` file
- `original_product_doc`: the original requirements text

Wait for it to return the delta report (NEW / UNCHANGED / NEEDS-UPDATE / OUTDATED).

**Present the delta report to the user for confirmation.** Ask the user to:
1. Confirm NEEDS-UPDATE items — accept the rewrite or provide corrections
2. Confirm OUTDATED reqs should be removed from scope (or retain them with `[OUTDATED — retained]`)
3. Confirm NEW reqs are correct

If the user requests changes, re-dispatch `req-classifier` with corrections then re-dispatch `sys-diff`. Repeat until confirmed.

The delta report is the SYS-level confirmation gate for this run — the raw SYS list from req-classifier is not presented separately when `--baseline` is active.

### 5. Dispatch layer decomposers (parallel)

For each active layer, launch in parallel:
- **firmware in scope** → `requirements-decompose:fw-decomposer`
- **backend in scope** → `requirements-decompose:backend-decomposer`
- **ui in scope** → `requirements-decompose:ui-decomposer`

Pass each agent: confirmed SYS requirements list, domain context, original doc, and `arch_doc` (if provided).

### 6. Dispatch api-contract

Launch `requirements-decompose:api-contract` unconditionally when two or more layers are active — any multi-layer system has at least one communication seam. Also launch for single-layer runs when `--api-contract` is passed.

Pass: all layer reqs produced in step 4, plus `arch_doc` if provided (may contain existing protocol specs).

### 7. Second confirmation gate

After layer decomposers and api-contract complete, collect all layer-level ambiguities (FW-AMB, SW-AMB, UI-AMB, API-AMB). If any exist, present them grouped by layer and ask for resolution. If user says "proceed anyway", tag all unresolved items and continue.

Any layer req derived from an `[INFERRED]` SYS req is tagged `[INFERRED — derived from INFERRED SYS-NNN]` to preserve the inference chain.

### 8. Dispatch component-mapper

Launch `requirements-decompose:component-mapper` with:
- SYS reqs, all layer reqs, API contracts, domain context
- `arch_doc` (if provided) — used to map reqs to existing files rather than inventing paths
- `template_dir` (if `--populate-templates` was passed) — directory of skeleton docs to populate

### 9. Assemble output

Produce a single structured Markdown document:

```
# Requirements: <system name>

## System Requirements
SYS-001 [←REQ-042] ...         ← source ID preserved if Polarion input
SYS-002 ... [INFERRED]
SYS-003 ... [CONFIRMED-BY-ARCH]

## Firmware Requirements (FW)
FW-001 (← SYS-001) ...

## Backend Requirements (SW)
SW-001 (← SYS-001) [EXISTS-IN-ARCH] ...

## UI Requirements (UI)  [omitted if not in scope]
UI-001 (← SYS-002) ...

## API Contracts
API-001 Firmware ↔ Backend: ...
API-002 Backend ↔ UI: ...

## Component Requirements
COMP-FW-001 (← FW-001): camera_trigger.c — ...
COMP-SW-001 (← SW-001): framegrabber_driver.py [EXISTS-IN-ARCH] — ...

## Traceability Matrix
| COMP ID       | Layer Req | SYS Req  | Source ID |
|---------------|-----------|----------|-----------|
| COMP-FW-001   | FW-001    | SYS-001  | REQ-042   |
...

## Inferred Requirements
List of all [INFERRED] items with reasoning.

## Architecture Notes  [omitted if no --arch]
Items confirmed or discovered from the architecture doc.

## Open Items
List of all [AMBIGUOUS] and [CONFLICT] items with recommended resolutions.

## Requirements Delta  [omit if no --baseline]
Delta summary table and OUTDATED list from sys-diff, showing NEW / UNCHANGED / NEEDS-UPDATE / OUTDATED counts and the full fresh → baseline ID mapping.
```

Derive `<system-name>`: (1) source filename without extension, (2) title of SYS-001 lowercased and hyphenated, (3) prompt the user. Write output to `requirements-<system-name>-<date>.md` in the current directory and print the path.

If `--populate-templates` was used, also list which template files were updated.

---

## Rules

- Never silently fill gaps — always tag inferences as `[INFERRED]`
- Never mark `[AMBIGUOUS]` items as resolved without user input
- Confirm SYS-level list before decomposing
- If `req-classifier` returns zero SYS reqs, stop and ask the user whether the input was the right document
- Component-level reqs must always trace to at least one layer req; layer reqs must trace to at least one SYS req
- API contracts are mandatory when two or more layers are in scope
- Architecture doc enriches inferences — it never overrides the requirements doc; requirements are authoritative
- When `--baseline` is provided, the confirmed SYS list carries delta tags (`[NEW]`, `[UNCHANGED]`, `[NEEDS-UPDATE]`, `[OUTDATED — retained]` if kept) throughout all downstream agents
- `--populate-templates` writes only into component-level skeleton docs — never modifies SYS/FW/SW/UI/API-level documents or the original Polarion source
