# PowerAgen PRD — v2.1

> **Changelog**
> v2.1 — Added MVP Acceptance Criteria, Non-goals, Responsibility Boundary, Strategy B v0.1 Contract, S2 Minimal Aggregation Rules, First End-to-End Slice. Refined Strategy C (split into C0 / C1), layout vocabulary (family/variant two-tier), `template_schema.json` (renamed `weak_layouts` → `coverage_report`), `slide_specs.json` (structured `slot_values` instead of freeform dict). Phase 0 split into 0A/0B/0C; revision deferred. Reviewer's deeper suggestions tracked separately in `PowerAgen_OpenExploration.md`.
> v2.0 — Initial Skeleton/Heart split.

> **Status legend**
> ✅ implemented and stable · ⚙️ implemented, needs hardening · 📐 interface defined, implementation pending · 🔬 active research · ⭕ not started

---

## Part 0 — How to Read This Document

PowerAgen is a template-aware PPT generation agent. Its differentiation lives in one specific research problem: **how to compile a user-provided PPT template into reusable design knowledge that an LLM can apply.**

This document is structured around a deliberate split:

- **Part 1** — Product positioning, capability model, MVP acceptance criteria, non-goals.
- **Part 2** — The **Skeleton**. Stable engineering parts: agent state machine, context flow, JSON contracts, rendering, validation, responsibility boundaries. These interfaces are designed to stabilize at v1.0 so that work can proceed in parallel against them.
- **Part 3** — The **Heart**. The Template Compiler — the actively evolving research component. Defined as a sequence of Stages (S1 → S4), each with its own scope and evaluation method.
- **Part 4** — Roadmap. Skeleton-first, Heart-iterative. Includes the **First End-to-End Slice** as the minimum viable closed loop.
- **Part 5** — Open questions still requiring decisions.

The reason for this split: the previous codebase coupled "agent orchestration" with "template understanding" so tightly that improving the latter destabilized the former. The PRD is structured to prevent that recurrence. **The Skeleton is the stable substrate; the Heart is the research surface.**

> **What MVP is, and is not.** MVP exists to validate the Template Compiler and the Strategy B grid extension. It is not a polished consumer PPT product. The MVP user is a technically literate research user who is comfortable with a CLI. Final consumer interaction (web UI, chat-style flow) is intentionally out of scope until the compiler is proven.

> **Document versioning.** Each JSON contract is currently at v0.1, the working baseline. The Skeleton's interfaces stabilize at v1.0 only after Phase 0 completes and the First End-to-End Slice runs successfully across at least two template families.

---

# Part 1 — Product

## 1. Summary

PowerAgen takes a user's PPT template plus content (documents, prompts, notes) and produces an editable PPTX that visually belongs to the template — not a PPT generated against the template's general "vibe," but one whose layout choices, visual system, and structural patterns are derived from the template itself.

The core technical bet: **a PPT template can be compiled into structured design knowledge, just like source code can be compiled into an AST.** Once compiled, an LLM can plan and instantiate decks against that knowledge instead of inventing structure from scratch.

## 2. Problem Statement

Most AI PPT tools generate visually plausible slides from open-ended visual styles. They are weak at one common need:

> The user already has a company / school / client / personal PPT template, and wants the AI's output to follow it.

Common failure modes in existing tools: inability to read template structure reliably, inability to distinguish editable content slots from fixed visual elements, inability to extend a template's pattern (a 4-grid layout into 6 grid items, a 3-step process into 5 steps), and an output that "looks like good slides" but visibly does not belong to the same deck as the user's template.

PowerAgen addresses this gap by treating template compilation as a first-class research problem rather than a side effect of slide generation.

## 3. Target User (MVP)

**MVP narrows to one Design Partner profile** (to be confirmed):

> A graduate student or research-track user who needs to produce 8–15 slide presentations from research papers / notes / drafts, using a school-provided or lab-provided PPTX template, where matching the template style is socially required.

Other user groups (consultants, sales, founders) are out of scope until the Heart stabilizes against the MVP profile.

> 📌 **Open question OQ-1**: confirm Design Partner profile.

## 4. Core Differentiation

PowerAgen is positioned not as another AI PPT generator, but as:

> **A stable agent skeleton wrapped around an evolving template compiler.**

| | Skeleton | Heart |
|---|---|---|
| **Stability** | Interfaces stabilize at v1.0 | Iterates across Stages 1 → 4 |
| **Components** | Agent loop, state machine, JSON contracts, Strategy A renderer, validator, interaction layer | Template Compiler, design system extractor, layout matcher, Strategy B/C renderers |
| **Engineering language** | Specifications, schemas, error codes | Methods, evaluation rubrics, known limitations |
| **Done means** | All contracts implemented, all tests pass | Specific eval rubric improvements vs. prior Stage |

Operating principle: **the Heart's progress must never require redesigning the Skeleton.** If a Heart change forces a Skeleton change, the Skeleton's contract was wrong and needs versioning, not patching.

## 5. Agent Positioning

PowerAgen is collaborative, not silently autonomous. It clarifies key missing inputs at the start, then runs the workflow to completion without further interruption unless a blocking error occurs. Front-loaded clarification, not slide-by-slide approval.

## 6. Capability Model

Two related but distinct axes: product output capability (user-visible) and Template Compiler internal stages (research-driven).

### 6.1 Output Capability Levels (user-visible)

| Level | What the user gets | Skeleton support | Heart support |
|---|---|---|---|
| **L0** | Generated deck without template | Strategy C0 renderer (generic layouts) | none |
| **L1** | Cloned template slides with text replaced | Strategy A renderer | S1 (per-slide Recipe) |
| **L2** | Template layouts adapted to new content (4-grid → 6-grid, etc.) | Strategy B renderer | S1 + slot semantics |
| **L3** | Generated deck applying full template design system | Strategy C1 renderer + design tokens | S2 (template-level aggregation) |
| **L4** | Template-native generation: new layouts that belong to the template | Strategy C1 with learned design language | S4 |

Strategies are split for clarity:

- **Strategy A** — clone-fill an existing template slide.
- **Strategy B** — extend an existing template layout (grid expansion, sequence expansion, list expansion).
- **Strategy C0** — generate a slide from generic defaults when no template is provided.
- **Strategy C1** — generate a template-native slide from the compiled design system when the template lacks the needed layout.

### 6.2 Template Compiler Stages (internal)

| Stage | What is compiled | Status |
|---|---|---|
| **S1** | Per-slide Recipe: intent, topology, slots, slot↔shape bindings, brand elements | ✅ Implemented (existing `powerT` v1.0 protocol) |
| **S2** | Per-template aggregation: cross-slide design system, layout type index, brand element resolution | 🔬 Active research |
| **S3** | Cross-slide brand layer detection (true Layer 4 of the 4-layer protocol) | 🔬 Future research |
| **S4** | Layout generalization & generation (template-native invention) | 🔬 Long-term |

The MVP target is **L1 + a narrow slice of L2** (specifically: grid extension), backed by **S1 + early S2**. L3 and L4 are research roadmap, not MVP.

## 7. MVP Acceptance Criteria

MVP is accepted only if all of the following hold:

1. Given one PPTX template and one content source (prompt or single file), PowerAgen generates a valid editable PPTX without unrecoverable error.
2. The output deck contains 8–15 slides.
3. At least 70% of generated slides are produced via Strategy A clone-fill and load correctly in PowerPoint.
4. At least one slide in at least one MVP test deck is produced via Strategy B grid extension successfully.
5. No generated slide contains unresolved placeholder text from the source template.
6. All generated slide titles remain editable text (not rasterized).
7. A `validation_report.json` is produced for every run, regardless of outcome.
8. All intermediate artifacts (`user_intent.json`, `template_schema.json`, `deck_outline.json`, `slide_specs.json`, `validation_report.json`) are saved under the run directory and are inspectable.
9. A human evaluator rates template similarity ≥ 4/5 on at least 3 distinct test decks (rubric defined in §19).
10. The complete workflow runs successfully on at least 2 unrelated template families.

Failing any criterion blocks MVP acceptance.

## 8. Non-goals

To prevent scope drift, MVP explicitly does not include:

- Complex animation extraction or reuse.
- Full SmartArt reconstruction (preserve via clone-fill only).
- Advanced chart redrawing (preserve via clone-fill where possible; otherwise warn).
- Multi-template fusion (combining layouts from different templates).
- Web UI polish or chat-style interface.
- Cloud deployment, multi-user collaboration, enterprise permissions.
- Fully automatic visual similarity scoring (human evaluation is the MVP standard).
- Real-time editing or live preview.
- Bilingual / multilingual auto-rewriting (output language matches user intent declaration only).
- Image generation or AI illustration (images come from context sources or template only).

These belong in V1.0+ or later, after MVP validates the compiler.

---

# Part 2 — Skeleton

The Skeleton is the engineered substrate around the Heart. Every component below has a defined contract; once stabilized at v1.0, contract changes are versioned, not silently revised.

## 9. Agent Workflow

The end-to-end flow from user input to final PPTX. Each Step has a defined input → output contract (JSON schemas in §11), and a current implementation status.

### Step 1 — Project Intake

Parse user prompt, scan files, identify task type, topic, slide count, language, audience, template requirement. Ask front-loaded clarification questions if essential information is missing.

- **Output**: `user_intent.json`, `file_manifest.json`
- **Status**: ⚙️ basic intent parsing exists; clarification flow needs to be built; manifest schema needs to distinguish template_candidates / context_candidates

### Step 2 — Context Distillation

Convert source documents (PDF, DOCX, TXT, MD) into structured PPT-ready knowledge. The agent must not stuff raw documents into the model context.

- **Output**: `context_distilled.json`
- **Status**: ⭕ not started

### Step 3 — Template Compilation

Compile the reference PPTX into structured design knowledge. **This is the Heart.** Skeleton's role here is only to define the contract (`template_schema.json`) and to call the compiler; what happens inside the compiler is Part 3.

- **Output**: `template_schema.json` (per-slide Recipes + aggregated design system)
- **Status**: 🔬 S1 ✅, S2 🔬, S3+ 🔬

### Step 4 — Deck Planning

Generate the deck's narrative structure: a slide-by-slide outline of what each slide is *for* (purpose, intended message), independent of visual layout decisions.

- **Output**: `deck_outline.json`
- **Status**: ⚙️ partial — current implementation generates outlines but does not consume `template_schema.json`

### Step 5 — Layout Matching

Match each planned slide to a suitable template layout. Decision logic combines content shape (item count, comparison structure, sequentiality) with template availability.

- **Output**: `slide_layout_plan.json`
- **Status**: 📐 contract defined, decision logic needs to be specified beyond LLM black-box scoring

### Step 6 — Slide Spec Generation

Produce the renderer-ready specification for each slide: layout choice, content per slot, rendering strategy.

- **Output**: `slide_specs.json`
- **Status**: 📐 contract defined; existing `text_map` format needs to be wrapped into `slide_spec.json` v0.1

### Step 7 — Rendering

Generate editable PPTX from slide specs. Strategies as defined in §6.1.

- **Strategy A** (clone-fill): ✅ implemented
- **Strategy B** (template-extend): ⭕ contract defined in §14, implementation pending — MVP differentiator
- **Strategy C0** (generic generation, no template): ⭕ stub exists
- **Strategy C1** (design-system-native): ⭕ not started, post-MVP

### Step 8 — Validation

Inspect the generated PPTX for text overflow, missing placeholders, empty slides, illegible font sizes, contrast issues, missing images, count mismatches, editability.

- **Output**: `validation_report.json`
- **Status**: ⭕ not started (a Recipe-level validator exists from `powerT` but does not validate generated PPTX)

### Step 9 — Revision

Targeted modification after generation, without rerunning the full workflow. Loads prior run artifacts, identifies target slides, updates only the affected slide specs, rerenders, revalidates.

- **Output**: revised PPTX + updated artifacts
- **Status**: ⚙️ plan-level revision exists; per-slide revision deferred to post-MVP

## 10. Component Inventory

The 14 named tools, organized by maturity. Each entry: name, responsibility, status.

### 10.1 Already implemented (interface to be stabilized at v1.0)

| Component | Responsibility | Status |
|---|---|---|
| `project_scanner` | Scan project directory, build file manifest | ⚙️ basic version exists; needs role classification |
| `pptx_xml_extractor` | Read PPTX structure (slides, layouts, masters, theme, relationships, media) | ✅ |
| `template_inventory_builder` | Build structured shape inventory per slide | ✅ (consolidate two existing implementations into one) |
| `template_annotator` | LLM-based slot/role/layout-type annotation per slide (S1) | ✅ |
| `slide_cloner` (Strategy A) | Clone template slides, fill slots, preserve layout | ✅ (known issues with placeholder resolution and theme font fallback — see §[Known Issues]) |

### 10.2 Interface defined, implementation pending

| Component | Responsibility |
|---|---|
| `intent_parser` | Parse natural-language input into `user_intent.json` |
| `deck_planner` | Generate `deck_outline.json` from intent + distilled context |
| `layout_matcher` | Map outline slides to template layouts |
| `slide_spec_generator` | Produce `slide_specs.json` |
| `pptx_validator` | Validate generated PPTX |

### 10.3 Heart components (research-driven, see Part 3)

| Component | Responsibility |
|---|---|
| `template_compiler` | S2 aggregation: combine per-slide Recipes into per-template `template_schema.json` |
| `design_system_extractor` | Extract template-level visual rules |
| `layout_type_classifier` | Cross-slide layout type unification |

### 10.4 Not started / deferred

| Component | Responsibility | Phase |
|---|---|---|
| `document_parser` | Parse PDF / DOCX / TXT / MD into structured chunks | Phase 2 |
| `context_distiller` | Distill parsed documents into PPT-ready content | Phase 2 |
| `pptx_renderer` (Strategy B) | Template-extending rendering | Phase 3 |
| `pptx_renderer` (Strategy C1) | Design-system-native rendering | Post-MVP |
| `revision_engine` (per-slide) | Per-slide targeted revision | Post-MVP |

## 11. JSON Contracts

This section is the **load-bearing wall of the Skeleton**. Every contract is a frozen interface that the Heart and the rest of the system bind against.

All contracts include `schema_version` (string, exact match required). Some contracts also include `generated_at` (ISO 8601) — marked explicitly per contract below; not all contracts need it.

> **Note on schema strictness.** Tables below describe each contract for human readers. As Phase 0A reaches implementation, the code's dataclass / pydantic models become the executable single source of truth, replacing prose ambiguity. v0.1 here is the working baseline; v1.0 will be locked when the First End-to-End Slice (§22) runs across two template families without contract changes.

### 11.1 `user_intent.json` v0.1

Captures the parsed user request.

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | yes | "0.1" |
| `task_type` | enum | yes | `generate_deck` \| `revise_deck` \| `single_slide` \| `learn_template` |
| `topic` | string | yes | Subject matter |
| `audience` | enum | yes | `academic` \| `business_internal` \| `business_external` \| `investor` \| `general` |
| `slide_count` | integer \| null | no | null → planner chooses |
| `language` | string | yes | BCP-47 (`en`, `zh-CN`, ...) |
| `template_required` | bool | yes | If true, generation aborts when no template available |
| `template_path` | string \| null | conditional | Required when `template_required` |
| `context_paths` | string[] | no | Files used as content sources |
| `visual_strictness` | enum | yes | `strict` (clone only) \| `adaptive` (allow extension) \| `creative` (allow generation) |
| `output_format` | enum | yes | `pptx` for v0.1 |
| `output_path` | string \| null | no | null → derived from topic |

### 11.2 `file_manifest.json` v0.1

```
{
  "schema_version": "0.1",
  "files": [
    {
      "path": string,
      "type": "pptx" | "pdf" | "docx" | "txt" | "md" | "image" | "data",
      "role": "template_candidate" | "context" | "previous_output" | "ignored",
      "size_bytes": int
    }
  ]
}
```

### 11.3 `context_distilled.json` v0.1

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | "0.1" |
| `sources[].source_id` | string | Unique identifier |
| `sources[].path` | string | Original file path |
| `sources[].type` | enum | `pdf` \| `docx` \| `txt` \| `md` \| `pptx` |
| `sources[].summary` | string | 2–4 sentences |
| `sources[].key_points[]` | object | `{claim, support, source_ref}` |
| `sources[].usable_figures[]` | object | `{caption, page, asset_path}` (optional) |
| `sources[].tables[]` | object | `{caption, page, csv_path}` (optional) |
| `aggregated.topic_summary` | string | Synthesized across all sources |
| `aggregated.suggested_sections[]` | string | Candidate deck section titles |

### 11.4 `template_schema.json` v0.1

The most important contract. Output of `template_compiler` (Heart). Logically partitioned into five sections (single physical file).

```
{
  "schema_version": "0.1",
  "generated_at": string,                // ISO 8601

  // --- 1. Template metadata ---
  "source_pptx": string,                 // relative path
  "slide_dimensions_emu": [int, int],

  // --- 2. Per-slide Recipes (S1 output) ---
  "slides": [
    // One Recipe v1.0 object per slide. Recipe schema defined in
    // powerT/references/recipe_schema.md (Appendix B reference).
    { "schema_version": "1.0", ... }
  ],

  // --- 3. Template-level design system (S2 output) ---
  "design_system": {
    "colors": {
      "primary": "#RRGGBB",
      "accent":  "#RRGGBB",
      "background": "#RRGGBB",
      "text_primary":   "#RRGGBB",
      "text_secondary": "#RRGGBB",
      "palette": ["#RRGGBB", ...]
    },
    "typography": {
      "title":   { "font": string, "size_range_pt": [int, int], "weight": "bold"|"regular" },
      "body":    { "font": string, "size_range_pt": [int, int], "weight": "regular" },
      "caption": { "font": string, "size_range_pt": [int, int], "weight": "regular" }
    },
    "spacing_emu": {
      "margin_left": int, "margin_right": int,
      "title_y": int, "content_top": int, "grid_gap": int
    },
    "shape_style": {
      "corner_radius": "none"|"small"|"medium"|"large",
      "line_width_pt": float,
      "shadow": "none"|"minimal"|"strong"
    }
  },

  // --- 4. Layout catalog (two-tier classification, S2 output) ---
  "layout_catalog": [
    {
      "slide_index": int,
      "layout_family": "cover" | "divider" | "agenda" | "content" |
                       "comparison" | "grid" | "sequence" | "chart" |
                       "quote" | "closing" | "generic",
      "layout_variant": string,           // e.g. "two_column", "four_grid", "timeline", "process"
      "item_count": int | null,           // for grid / sequence variants
      "grid_shape": string | null,        // e.g. "2x2", "1x3" — for grid family
      "confidence": float                 // 0–1
    }
  ],

  // --- 5. Extension capabilities (S2 output) ---
  "extension_capabilities": {
    "grid_extendable": [int, ...],        // slide indices supporting grid extension
    "sequence_extendable": [int, ...],    // slide indices supporting timeline/process extension
    "list_extendable": [int, ...]
  },

  // --- 6. Coverage report (planner-facing diagnostic) ---
  "coverage_report": {
    "available_layout_families": [string, ...],
    "missing_common_layout_families": [string, ...],   // e.g. ["chart", "comparison"]
    "low_confidence_layouts": [int, ...]               // slide indices below confidence threshold
  }
}
```

**Layout vocabulary uses two tiers**: `layout_family` is a small controlled set (planner uses this for coarse matching); `layout_variant` is freeform within a family (renderer uses this for fine strategy). This prevents vocabulary explosion as new variants emerge.

> 📌 **Open question OQ-3**: design system aggregation conflict resolution. Baseline rules in §17.2; refinement is open exploration.

### 11.5 `deck_outline.json` v0.1

```
{
  "schema_version": "0.1",
  "title": string,
  "slides": [
    {
      "slide_no": int,                   // 1-indexed
      "purpose": string,                 // freeform agent-authored
      "title": string,                   // intended slide title
      "intent": string,                  // 1-sentence what this slide must communicate
      "content_shape": {                 // structural hint to layout_matcher
        "kind": "single" | "list" | "comparison" | "sequence" | "grid" | "data",
        "item_count": int | null
      },
      "evidence_refs": [string]          // source_id references from context_distilled.json
    }
  ]
}
```

### 11.6 `slide_layout_plan.json` v0.1

```
{
  "schema_version": "0.1",
  "plan": [
    {
      "slide_no": int,
      "selected_template_slide_index": int | null,    // null when Strategy C
      "layout_family": string,
      "layout_variant": string,
      "rendering_strategy": "clone_fill" | "template_extend" | "design_system_generate",
      "extension_params": {                            // present only for template_extend
        "kind": "grid" | "sequence" | "list",
        "target_count": int
      } | null,
      "match_reason": string,
      "match_confidence": float                        // 0–1
    }
  ]
}
```

### 11.7 `slide_specs.json` v0.1

The handoff to the renderer. Each spec is self-contained: the renderer must not consult any other file. Content uses **structured slot values**, not freeform dicts, to prevent upstream/downstream key drift.

```
{
  "schema_version": "0.1",
  "specs": [
    {
      "slide_no": int,
      "rendering_strategy": "clone_fill" | "template_extend" | "design_system_generate",
      "template_ref": int | null,                     // source slide index in template
      "recipe_ref": object | null,                    // FULL Recipe v1.0 embedded (not pointer)

      // Slot values — structured, validated against the recipe's slot schema
      "slot_values": [
        {
          "slot_id": string,                          // matches a slot.field in Recipe
          "value_type": "text" | "number" | "image",
          "value": string,                            // text content, number as string, or image path
          "fit_policy": "strict" | "shrink_or_summarize" | "split"  // overflow policy
        }
      ],

      // Repeat slot groups — for array slots in Recipe
      "item_groups": [
        {
          "slot_id": string,                          // matches array slot.field in Recipe
          "items": [
            {
              "<item_field>": string,                 // values for each field in slots[].item
              ...
            }
          ]
        }
      ],

      // Strategy-specific params
      "extension_params": object | null,              // for template_extend; see §14
      "design_tokens": object | null                  // for design_system_generate

      // Note: 'recipe_ref' must be a complete Recipe object, not a reference id.
      // This is what makes 'self-contained' work.
    }
  ]
}
```

**Key drift prevention**: `slot_id` must match a `slot.field` declared in the embedded `recipe_ref`. The validator (Phase 0B) checks this; renderer can refuse to render specs that fail.

### 11.8 `validation_report.json` v0.1

```
{
  "schema_version": "0.1",
  "generated_at": string,
  "status": "pass" | "warn" | "fail",
  "issues": [
    {
      "slide_no": int,
      "severity": "info" | "warn" | "error",
      "code": string,    // e.g. "TEXT_OVERFLOW", "EMPTY_PLACEHOLDER", "FONT_TOO_SMALL"
      "message": string,
      "shape_id": string | null
    }
  ],
  "metrics": {
    "slide_count": int,
    "editable_text_ratio": float,
    "template_similarity_estimate": float
  }
}
```

### 11.9 Versioning Policy

- Each contract has independent `schema_version`.
- Adding optional fields → no version bump.
- Removing or repurposing fields, changing required fields, or changing enum values → minor version bump.
- Breaking changes requiring coordinated upgrade → major version bump.
- The Heart's evolution should never force a major version bump on Skeleton contracts. If S2 work surfaces a contract that needs reshaping, that is a Skeleton bug surfaced by Heart progress.
- Contracts stabilize at v1.0 only after Phase 0 completes and the First End-to-End Slice (§22) runs across two template families without contract changes.

## 12. Interaction Layer

### 12.1 MVP decision

**MVP: CLI-only.** Built on existing CLI scaffolding, offering an interactive REPL plus single-command modes.

**V1.0**: thin web UI wrapping the same CLI workflow (no business-logic rewrite).

**V2.0+**: native chat web app, only after MVP and V1.0 stabilize.

This is consistent with the principle stated in Part 0: MVP validates the compiler, not the final interaction experience.

### 12.2 Interaction principles

- Front-loaded clarification: ask up to 3 essential questions before starting; declare reasonable defaults for everything else.
- High-level progress messages during generation; no slide-by-slide approval gates.
- After generation, return: file path, summary, warnings, suggested revision prompts.
- Revision is always an explicit user action, never an auto-loop.

### 12.3 Layer separation

```
Interaction Layer  (CLI / Web)
        │
        ▼
Core Agent Layer  (intent → clarification → orchestration)
        │
        ▼
Tool Layer  (parsers, compiler, planner, renderer, validator)
```

The Interaction Layer never owns business logic. It displays, collects, and dispatches.

## 13. Responsibility Boundary

A single principle that prevents the most common coupling failure: LLM and renderer "covering for each other" instead of each owning its scope.

### 13.1 Deterministic code owns

- PPTX XML extraction
- Shape inventory construction
- Coordinate calculation (positions, sizes, gaps)
- Clone-fill rendering (Strategy A)
- Grid/sequence/list extension geometry (Strategy B math)
- PPTX validation
- File manifest construction
- JSON schema validation
- Run directory management

### 13.2 LLM owns

- Intent parsing (Step 1)
- Slide semantic annotation (S1 Layers 1, 2, 4)
- Deck planning (Step 4)
- Layout matching reasoning (Step 5, with deterministic scoring as input)
- Content compression and rewriting (when content overflows slot)
- Section title generation

### 13.3 Renderer responsibilities

The renderer:

- Converts `slide_specs.json` into PPTX.
- Applies geometry rules deterministically.
- Preserves editability of text slots.
- Reports failures with structured error codes.

The renderer **must not**:

- Infer missing content semantics.
- Invent slot names not declared in `recipe_ref`.
- Reinterpret user intent.
- Make stylistic decisions absent from `design_tokens` or `recipe_ref`.

### 13.4 Compiler responsibilities

The compiler (per Stage):

- S1: produces per-slide Recipes from PPTX + screenshot.
- S2: aggregates Recipes into `template_schema.json`.
- S3+: extends compilation depth (cross-slide, generative).

The compiler **must not**:

- Write content into slides (that is the renderer).
- Make planning decisions (that is the planner).
- Decide rendering strategy (that is the layout matcher).

## 14. Strategy B v0.1 — Grid Extension Contract

This is the MVP differentiator and was previously left as an open question. v0.1 below is the conservative initial contract; advanced cases are tracked in `PowerAgen_OpenExploration.md`.

### 14.1 Supported

- Source layout's `layout_family` is `grid`.
- Source layout's `grid_shape` is regular and symmetric (e.g. 2x2, 1x3, 2x3, 1x4).
- All grid items share the same slot structure (each item has the same item-level fields, declared in the Recipe's `slots[].item`).
- Each item has one container group or visually equivalent bounding box (verifiable from Recipe's `repeat_bindings.prototype_group`).
- Target item count: between source_count + 1 and source_count × 2 (e.g. 4-grid extends to 5–8 items; not to 12).
- Minimum generated body font size: 12pt.
- Minimum generated title font size: 14pt.

### 14.2 Behavior

Extension preserves: template item style (fill, border, font, decoration within item), item gap (proportionally adjusted), title and overall slide chrome.

Extension may modify: item positions (recomputed on extended grid), item dimensions (proportionally scaled), font size within allowed range.

### 14.3 Not supported (v0.1)

- Irregular or mosaic layouts (1+3 asymmetric, diagonal arrangements).
- Grid items connected by arrows, lines, or curved decorations crossing item boundaries.
- Items with unique per-card decorations (each item has different decoration).
- Target count > 2 × source count.
- Cases requiring auto-scaling below the font floors above.

### 14.4 Failure behavior

When unsupported, return error code `EXTENSION_UNSUPPORTED` with diagnostic message. The layout matcher must then either:

- Fall back to clone-fill (Strategy A) using the original item count, with a warning that some content will be omitted; or
- Split content across multiple slides (Strategy A on each), preserving the user-requested item count across the split.

### 14.5 Decision authority

- The compiler (S2) populates `extension_capabilities.grid_extendable` based on geometry analysis.
- The layout matcher (Step 5) decides whether to invoke Strategy B based on `extension_capabilities` and `content_shape.item_count`.
- The renderer (Step 7) executes the geometry; refuses execution if preconditions in §14.1 are not met at render time.

### 14.6 Beyond v0.1

Asymmetric grids, decoration-aware extension, multi-direction expansion, and cross-strategy fallback policies are tracked in `PowerAgen_OpenExploration.md`.

---

# Part 3 — Heart

The Template Compiler. The active research surface. Each Stage is a scoped milestone with its own evaluation method.

## 15. Stage 1 — Per-Slide Recipe (current state)

**Status**: ✅ implemented and validated against 3 evaluation samples.

### 15.1 What it does

Given one slide (PPTX + screenshot + slide index), the compiler produces a **Recipe v1.0 JSON** capturing:

- **Layer 1 — Intent**: what is this slide for? (vision-derived)
- **Layer 2 — Topology**: spatial skeleton, repetition pattern, slot schema, repeat field (vision-derived)
- **Layer 3 — Visual parameters**: exact colors, sizes, fonts (XML-derived, never estimated)
- **Layer 4 — Brand elements** (currently single-slide approximation): which shapes are fixed brand decoration vs. editable content
- **Bindings**: every editable slot bound to a specific shape; array slots bound through `prototype_group` and `item_bindings`

Full schema and 9 hard validation rules in `recipe_schema.md` (Appendix B).

### 15.2 Method

Two-call extraction:

- **Call 1** (Vision-heavy): screenshot + condensed shape summary → Layers 1 & 2.
- **Call 2** (XML-heavy): full XML + Call 1 output → Layers 3 & 4.

LLM tool_use forces structured JSON. System prompts include the 4-layer protocol and schema document with prompt caching.

### 15.3 Validation

A deterministic validator checks 9 hard rules per Recipe. A reference smoke consumer (`eval_round_trip`) verifies actual consumability: clone source slide, write placeholders into every binding, save valid PPTX. Two levels: Level 1 fills bindings; Level 2 also duplicates prototype groups.

### 15.4 Known limitations

- **Single-slide vision**: Layer 4 is heuristic without cross-slide context. True brand identification requires Stage 3.
- **Sample diversity**: validated on 3 samples from one template family.
- **No layout type vocabulary**: each slide's `name` field is freeform; cross-slide unification is part of S2.
- **No real image kind replacement**: smoke consumer skips picture replacement; production replacement is a consumer responsibility.

## 16. Stage 2 — Per-Template Aggregation (next)

**Status**: 🔬 active, the immediate research target.

### 16.1 Problem

Stage 1 produces N independent per-slide Recipes for an N-slide template. Stage 2 must aggregate into a single template-level artifact: unified design system, layout catalog, extension capability map, coverage report.

### 16.2 Sub-problems

- **Design system aggregation** — slides disagree on exact colors, fonts, spacing; need conflict resolution rules.
- **Layout type unification** — Stage 1 freeform `name` fields must map into the controlled `layout_family` vocabulary.
- **Extension capability resolution** — verify per-slide `extendable` claims against geometry.
- **Brand element promotion** — cross-slide co-occurrence to promote shapes from "decoration" to "global brand element".

### 16.3 Output

`template_schema.json` v0.1 (full schema in §11.4).

## 17. S2 v0.1 — Minimal Aggregation Rules

A baseline rule set that is good enough to ship Phase 1. Refinement and alternatives tracked in `PowerAgen_OpenExploration.md`.

### 17.1 Color aggregation

1. Extract all solid fill colors and font colors from every slide and from theme XML.
2. Remove near-white (`#F8F8F8`+ lighter) and near-black (`#0A0A0A`- darker) defaults unless they appear ≥ 3 times in non-default contexts.
3. Cluster colors by RGB Euclidean distance; threshold ≤ 12 collapses two colors into one cluster, with the more frequent member as the cluster centroid.
4. **Primary color** = most frequent non-neutral color used in titles or shapes occupying > 5% of slide area.
5. **Accent color** = second most frequent non-neutral color.
6. **Background color** = solid background fill on cover or first content slide.
7. **Palette** = all cluster centroids occurring on ≥ 2 slides.

### 17.2 Typography aggregation

1. Collect all `(font_name, size_pt, weight)` tuples from every text run.
2. **Title style** = largest size whose tuple recurs across ≥ 2 slides.
3. **Body style** = most frequent tuple below title size.
4. **Caption style** = smallest size tuple recurring on ≥ 2 slides.
5. When fonts use theme references (`+mj-lt`, `+mn-lt`), resolve via theme XML before clustering.

### 17.3 Spacing aggregation

1. `margin_left` = median x of title/content text boxes (across slides where present).
2. `margin_right` = slide_width - median right edge of title/content text boxes.
3. `title_y` = median y of title slots.
4. `content_top` = median y of first non-title text box.
5. `grid_gap` = median pixel gap between bounding boxes of repeated item groups.

### 17.4 Layout family classification

1. **Rule-based first**: heuristic classifier on Recipe's `topology` and `slots`:
   - 1 large title shape, no body content, often early in deck → `cover`
   - 1 large title shape, decorative section number, no body content → `divider`
   - 2 columns of similar shape → `comparison` (if titles imply contrast) or `content` (otherwise)
   - 3+ items in regular grid → `grid` (variant by `grid_shape`)
   - 3+ items in linear sequence with index/connector → `sequence` (variant: `timeline` or `process`)
   - Single quote or large body text → `quote`
   - Closing/thank-you indicators → `closing`
   - Last resort → `generic`

2. **LLM fallback**: if rule-based classification confidence < 0.6, call LLM with full Recipe to choose family + variant.

3. **Confidence score** stored alongside classification.

### 17.5 Conflict resolution defaults

- When master XML, layout XML, and slide XML disagree: master XML > layout XML > slide XML majority vote.
- When two slides claim incompatible primary colors: choose the one used in titles; if tied, choose the one used on more slides.
- When typography hierarchy is ambiguous (e.g. only one text size in template): synthesize body and caption from theme defaults rather than failing.

### 17.6 Failure mode

If aggregation cannot produce a populated `design_system` (template too sparse, only 1 slide, etc.), populate from theme XML defaults and mark `coverage_report.low_confidence_layouts` accordingly. Never fail outright.

## 18. Stage 3 — Cross-Slide Brand Detection (mid-term)

**Status**: 🔬 future research.

Identify brand elements by shape-position-style co-occurrence across slides. Shapes recurring on ≥ N slides with stable features are promoted to the template's brand layer. Affects Strategy B and C1, which must explicitly re-instantiate brand elements (Strategy A clones already preserve them).

Cannot run before S2.

## 19. Stage 4 — Layout Generalization (long-term)

**Status**: 🔬 long-term, not on MVP critical path.

Extracts higher-level patterns ("template prefers left-aligned titles with accent bar", "comparison content uses two columns with vertical divider") to enable Strategy C1 (template-native generation). Outputs a `design_language.json` artifact, extending `template_schema.json` v0.2+.

Begins only after S2 validates across multiple template families.

## 20. Compiler Evaluation Strategy

The Heart's progress is measured by evaluation rubrics, not feature checklists.

### 20.1 Existing framework (from `powerT`)

- **3 fixed evaluation samples** (one template family, three slide types: timeline / repeat-card / brand-cover).
- **Capability-dimension rubrics**: brand_layer, repeat_structure, slot_quality, slot_bindings, visual_params, topology, shape_traceability, round_trip.
- **Anti-overfit rules**: expected outputs describe reusable layout behavior, not deck-specific content; sample names describe slide type, not source template.

### 20.2 Stage 2 extension

- **Template-level rubrics**: design system fidelity, layout type coverage, brand element promotion accuracy.
- **Cross-family validation**: ≥ 2 unrelated template families before any Stage 2 capability is declared stable.

### 20.3 Evaluation dataset (spec; concrete samples to be sourced)

Not all samples need to exist before Phase 1 starts; the spec defines what coverage is required for MVP acceptance.

| Dimension | Required coverage |
|---|---|
| **Template families** | At least 2 unrelated families. One academic or research template (T1), one corporate or business template (T2). T3 (visually rich / non-Western design) optional for MVP. |
| **Slide archetypes per family** | cover, section divider, two_column, grid (any variant), at least one of {timeline, process}, closing |
| **Content sources** | short prompt only, single PDF, multiple PDFs (when context pipeline lands) |
| **Strategy coverage** | A clone-fill, B grid extension, C0 generic |

### 20.4 MVP evaluation runs

| Run | Template | Content | Validates |
|---|---|---|---|
| **A** | T1 | one paper or notes | end-to-end with Strategy A only |
| **B** | T1 | grid extension target | Strategy B 4→6 |
| **C** | T2 | short prompt | end-to-end on second template family |
| **D** | T2 | grid extension target | Strategy B on second family |
| **E** | T1 | bare prompt | L0 / Strategy C0 fallback works |

All five runs must pass MVP Acceptance Criteria (§7) for MVP to ship.

> 📌 **Open question**: where to source T2 (and ideally T3) templates — operational, tracked in OpenExploration.

---

# Part 4 — Roadmap

Skeleton-first, Heart-iterative.

## 21. Phase Structure

### Phase 0 — Skeleton Hardening

Split into three sub-phases for clarity. Phase 0A is contracts only — no behavior change. Phase 0B aligns existing code to those contracts. Phase 0C proves the minimum closed loop runs.

#### Phase 0A — Contract Freeze

- Finalize JSON contract schemas at v0.1 (§11).
- Consolidate duplicate inventory builders into one.
- Define run directory structure under `.powerAgen/runs/`.
- Define CLI task flow (commands, arguments, error codes).
- Decide CLI-only for MVP (per §12.1) — done.
- No behavior changes outside scope of contract definitions.

#### Phase 0B — Existing Strategy A Alignment

- Adapt existing clone-fill implementation to read `slide_specs.json` v0.1.
- Fix placeholder resolution after slide clone.
- Fix theme font fallback in cloned slides.
- Implement `pptx_validator` against `validation_report.json` v0.1.
- Merge no-template path and template path into one workflow with a `template_required` switch.

#### Phase 0C — First End-to-End Slice

See §22 for full definition. Goal: prove the minimum chain works.

Revision engine, context distillation, and Strategy B are explicitly deferred from Phase 0.

### Phase 1 — Heart Stage 2

Goal: per-template aggregation. `template_schema.json` v0.1 produced from any single-template input.

- Implement `template_compiler` aggregation layer using §17 baseline rules.
- Implement layout family classification (rule-based + LLM fallback).
- Implement design system aggregation.
- Add template-level evaluation rubrics.
- Validate against ≥ 2 template families.

May begin while Phase 0B finishes the validator — compiler does not depend on validator.

### Phase 2 — Context Pipeline

Goal: PowerAgen consumes PDFs / DOCX / MD as content sources.

- Implement `document_parser` per format.
- Implement `context_distiller`.
- Update `deck_planner` to consume `context_distilled.json`.

Parallelizable with Phase 1.

### Phase 3 — Strategy B (Grid Extension)

Goal: MVP differentiator shipped, against the §14 contract.

- Implement renderer for grid extension per §14 supported cases.
- Implement `EXTENSION_UNSUPPORTED` failure behavior with fallback.
- Validate against MVP evaluation runs B and D.

### Phase 4 — Per-slide Revision

Goal: targeted post-generation modification.

Out of MVP scope; this is the post-MVP first feature.

### Phase 5 — Heart Stage 3 + Strategy C1

Goal: cross-slide brand detection; design-system-native generation for layouts the template lacks.

Out of MVP scope. Begins after Phase 3 stabilizes.

### Phase 6 — Heart Stage 4 + L4 generation

Long-term research. Not committed to any timeline.

## 22. First End-to-End Slice

The minimum chain that proves Skeleton + Heart S1 work together. This is the Phase 0C deliverable.

**Input**:
- one `template.pptx`
- one user prompt (no PDFs / DOCX yet)
- one **manually authored** `slide_specs.json` (the planner is not in the loop yet)

**Process**:
1. `project_scanner` → `file_manifest.json`
2. `pptx_xml_extractor` + `template_inventory_builder` → shape inventory
3. `template_annotator` (S1) on the slides referenced in the manual spec → Recipes
4. Wrap into `template_schema.json` v0.1 (S2 trivial: empty `design_system`, layout_catalog filled with S1 outputs only)
5. Strategy A renderer consumes `slide_specs.json` (manually authored, embedding the Recipes from step 3)
6. `pptx_validator` → `validation_report.json`

**Output**:
- `output.pptx` editable in PowerPoint
- complete run directory with all intermediate artifacts

**Not included in this slice**:
- `context_distiller` (no PDF parsing)
- `deck_planner` (slide_specs is manual)
- `layout_matcher` (slide_specs encodes the choices directly)
- Strategy B / C
- Revision

**Why this matters**: the slice exists to harden the Skeleton's contracts and the integration between Recipe extraction and Strategy A rendering. It removes every component still being designed (planner, distiller, layout matcher) so failures are isolatable. After this runs cleanly across two templates, contracts can be promoted from v0.1 → v1.0.

The second slice (Phase 1 deliverable) adds: template + prompt → `deck_outline.json` → `slide_specs.json` (auto) → `output.pptx`, eliminating the manual spec authoring.

The third slice (Phase 3 deliverable) adds: context files + grid extension → `output.pptx`, the full MVP loop.

---

# Part 5 — Open Questions

Items not yet decided that block specific downstream work. Items already resolved in v2.1 (Strategy B contract, layout vocabulary baseline) have moved into the document body. Open exploration topics not blocking MVP have moved to `PowerAgen_OpenExploration.md`.

## OQ-1 — Confirm MVP Design Partner profile

Dictates which template families are in scope, which content sources are realistic, which audience defaults the agent should assume.

**Proposal**: graduate / research user with school PPT template.

**Decision needed**: confirm or replace.

## OQ-3 — Design system aggregation conflict resolution beyond §17 baseline

§17 baseline rules are good enough for MVP. Open: when baseline produces visibly wrong palette / typography on a real template, what is the refinement path? Tracked in OpenExploration.

**Decision needed**: confirm baseline is acceptable for MVP; defer refinement.

## OQ-5 — Editability guarantees

NFR says output must be editable; the actual boundary is undefined.

**Specific questions**:
- For Strategy A clones: which placeholder types are reliably editable after cloning? (Known issue: PLACEHOLDER-type shapes lose binding.)
- For Strategy C generation: are generated icons real shapes or rasterized images?
- What happens when python-pptx cannot represent a shape from the template?

**Decision needed**: a written editability contract enumerating what is guaranteed editable, what is best-effort, what may be image-only.

## OQ-6 — Memory / state directory conventions

The existing codebase has three different state directory conventions (`.powergen/`, `.claude/`, the proposed `.powerAgen/`). The PRD assumes per-project memory; the MVP user may not need it.

**Decision needed**: confirm whether `.powerAgen/` per-project structure is MVP-required or V1.0; if MVP-required, deprecate the other two.

---

# Appendix A — JSON Contract Index

| Contract | Section | Owner module | Status |
|---|---|---|---|
| `user_intent.json` | §11.1 | `intent_parser` | 📐 |
| `file_manifest.json` | §11.2 | `project_scanner` | ⚙️ |
| `context_distilled.json` | §11.3 | `context_distiller` | ⭕ |
| `template_schema.json` | §11.4 | `template_compiler` (Heart) | 🔬 |
| `deck_outline.json` | §11.5 | `deck_planner` | 📐 |
| `slide_layout_plan.json` | §11.6 | `layout_matcher` | 📐 |
| `slide_specs.json` | §11.7 | `slide_spec_generator` | 📐 |
| `validation_report.json` | §11.8 | `pptx_validator` | ⭕ |

Recipe v1.0 (embedded inside `template_schema.json.slides[]` and `slide_specs.json.specs[].recipe_ref`) is defined separately in the existing `recipe_schema.md` reference document.

---

# Appendix B — Existing Asset Inventory

PowerAgen does not start from zero. Existing assets integrated into the design above:

- **Recipe v1.0 protocol** — per-slide schema with 9 hard validation rules.
- **Recipe extractor** — 2-call Vision + XML pipeline using LLM tool_use.
- **Recipe validator** — deterministic checker for the 9 hard rules.
- **Reference smoke consumer** — eval-only round-trip tool.
- **Evaluation framework** — 3 fixed samples with capability-dimension rubrics and anti-overfit rules.
- **Strategy A renderer (clone-fill)** — slide cloning with rId remapping, formatting-preserving text replacement, repeat-clone support.
- **CLI scaffolding** — interactive REPL, slash commands, project state machine, mock LLM client.
- **Project state machine** — INIT → PLANNED → APPROVED → RENDERED with persistence.

---

# Appendix C — Known Issues

To be addressed during Phase 0B:

- **Placeholder resolution after slide clone**: some PLACEHOLDER-type shapes are not resolved post-clone, causing original template text to show through.
- **Theme font fallback**: `+mj-lt` and `+mn-lt` may fall back to system defaults in cloned slides.
- **Two parallel inventory implementations**: must consolidate.
- **Two parallel pipelines**: no-template path and template path do not share planning logic. Must merge.
- **CLI argument parsing inconsistency**: the `template` subcommand has a typo / variable mismatch preventing clean execution.

---

# Appendix D — Glossary

- **Recipe** — per-slide structured representation produced by Stage 1. JSON object conforming to Recipe v1.0.
- **Slot** — an editable content placeholder (e.g., title, body, item-2-description).
- **Binding** — the link between a slot and a specific shape, identified by `shape_id` and `shape_name`.
- **Brand element** — a shape part of the template's fixed visual identity.
- **Strategy A / B / C0 / C1** — rendering strategies (clone-fill / template-extend / generic-without-template / design-system-native).
- **Heart** — the Template Compiler. The actively evolving research component.
- **Skeleton** — the engineered substrate around the Heart.
- **L0–L4** — output capability levels (user-visible).
- **S1–S4** — Template Compiler internal stages.
- **First End-to-End Slice** — Phase 0C deliverable, the minimum chain that proves Skeleton + S1 integrate.
