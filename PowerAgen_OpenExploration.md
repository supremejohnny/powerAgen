# PowerAgen Open Exploration

> Companion document to `PowerAgen_PRD_v2_1.md`. Contains research questions, deferred suggestions, and exploration topics that are intentionally **not** part of the MVP commitment. Each topic states: what the question is, why it's deferred, what to explore when the time comes, and any first-pass thoughts.
>
> This is a **working notebook**, not a specification. Things here will be added, removed, and reorganized as understanding develops. When a topic stabilizes enough to commit, it graduates into the PRD body.

---

## How to Use This Document

- **Adding topics**: when a question surfaces during development that doesn't block MVP but deserves to be remembered, write it here with the section template at the bottom.
- **Resolving topics**: when a topic gets answered, move the resolution into the PRD and link from here. Don't delete — keep a one-line "→ moved to PRD §X" record.
- **Pruning**: every few months, prune topics that are no longer relevant.

---

# Section 1 — Reviewer Feedback Tracker

Status of each suggestion from the v2.0 review:

## 1.1 Adopted into PRD v2.1

| # | Suggestion | Where it landed |
|---|---|---|
| 2 | MVP Acceptance Criteria | PRD §7 |
| 4 | Strategy B v0.1 Contract | PRD §14 |
| 5 | S2 Minimal Aggregation Rules | PRD §17 |
| 6 | MVP scope clarification ("validates compiler, not interaction") | PRD Part 0 |
| 8 | Layout family / variant two-tier vocabulary | PRD §11.4, §11.6 |
| 9 | `template_schema.json` logical partitioning + `coverage_report` rename | PRD §11.4 |
| 10 | Responsibility Boundary section | PRD §13 |
| 11 | Phase 0 split into 0A/0B/0C; revision deferred | PRD §21 |
| 12 | First End-to-End Slice | PRD §22 |
| 13 | Terminology cleanups (Strategy C0/C1, contract versioning) | PRD throughout |
| 14 | Six new sections | PRD §7, §13, §14, §17, §22, §8 (Non-goals) |
| 21 | Non-goals section | PRD §8 |

## 1.2 Partially Adopted

| # | Suggestion | Adopted as | Deferred portion |
|---|---|---|---|
| 3 | Strict JSON Schema for core contracts | Restructured contracts in §11 with stronger field typing; `slide_specs.json` `slot_values` now structured | Full JSON Schema documents not produced — see §3.1 below |
| 7 | Evaluation Dataset v0.1 | PRD §20.3–§20.4 spec what coverage is needed; concrete T1/T2/T3 samples not enumerated | Sourcing operations — see §3.4 below |

## 1.3 Deferred (tracked here)

All deeper exploration topics from the review are continued in Sections 2–4 below.

---

# Section 2 — Strategy B: Beyond v0.1

PRD §14 commits to a conservative grid extension contract. Real templates will eventually demand more.

## 2.1 Asymmetric Grids

**Question**: how to extend a 1+3 layout (one large hero card + three smaller cards), or a 2+1+3 magazine-style mosaic?

**Why deferred**: detection alone is hard (Recipe v1.0 doesn't model "hero vs supporting role"); extension semantics are unclear (does adding one item create another hero or another supporting?); single-template MVP doesn't need it.

**To explore**:
- Augment Recipe v1.0 with item-role classification (hero / standard / supporting) — would this be S1 work or a new layer?
- Define extension semantics per asymmetric pattern (1+N → 1+M, 2+N → 2+M).
- Decide whether asymmetric grids should auto-degrade to symmetric on extension or refuse.

**First thoughts**: most asymmetric grids people use in practice are 1+N "hero + supporting" patterns. Other shapes (2+1+3, diagonal mosaics) are rare. Worth surveying real templates before designing.

## 2.2 Decoration-Aware Extension

**Question**: a grid with arrows or curves connecting items — extension must redraw connectors, not just clone items.

**Why deferred**: decoration semantics are slide-specific; v0.1 explicitly refuses these cases.

**To explore**:
- Detect inter-item decoration in S2 (shape relationships across item bounding boxes).
- Define a decoration adapter interface: given (source connector geometry, source item count, target item count) → generate target connectors.
- Common cases: linear arrows (timeline-style), curved bezier (process flow), parallel lines (comparison divider).

**First thoughts**: this might belong in Strategy C1 territory (design-system-native generation) rather than B (template-extend). Connector generation is more like "creating a new sequence" than "extending a grid".

## 2.3 Multi-Direction Expansion

**Question**: a 2x3 grid extended to 2x4 vs 3x3 vs 2x6 — which direction?

**Why deferred**: requires intent input from the planner that doesn't exist yet.

**To explore**:
- Add `extension_direction` hint to `extension_params` (vertical / horizontal / preserve_ratio / auto).
- Define heuristic for `auto`: prefer the direction with more whitespace; respect aspect ratio of items.

## 2.4 Cross-Strategy Fallback Policies

**Question**: when Strategy B refuses, the fallback to "split across multiple slides" is naive. Real users may prefer "skip last items" or "summarize into N items".

**Why deferred**: requires user intent capture that v0.1 doesn't have.

**To explore**:
- Surface `overflow_policy` as a top-level option in `user_intent.json`: `split` / `truncate` / `summarize` / `refuse`.
- Map each policy to a deterministic Strategy B fallback path.

---

# Section 3 — S2 Aggregation: Refinement Beyond Baseline

PRD §17 ships baseline rules. They will produce visibly wrong output on some templates. Refinement work below.

## 3.1 Color Clustering Refinement

**Baseline**: RGB Euclidean distance threshold ≤ 12.

**Known weakness**: RGB distance does not match human color perception. Two colors that look identical might exceed threshold (especially in dark or saturated regions); two visibly different colors might fall under threshold.

**To explore**:
- Switch to perceptual distance (CIEDE2000 or simpler LAB Euclidean).
- Consider hue-aware clustering (group by hue first, then luminance).
- Sample real templates to find actual clustering threshold that matches human judgment.

**First thoughts**: don't over-engineer. The MVP target is "MS Office–style decks", which mostly use distinct accent colors. Baseline RGB clustering probably fails on visually rich templates more than on academic templates. Test on actual MVP test deck first; refine only if the baseline visibly fails.

## 3.2 Master XML vs Slide XML Authority

**Baseline**: master XML > layout XML > slide XML majority vote.

**Known weakness**: many real-world templates have master/layout XML that's stale or never populated correctly (designer set everything per-slide). Trusting master can produce defaults that no slide actually uses.

**To explore**:
- Add a "manifest fidelity" check: if master values don't appear in any slide, downgrade master authority for that field.
- Make authority per-attribute, not global: master might be authoritative for primary color but unreliable for spacing.

## 3.3 Layout Family Classification: LLM Confidence Calibration

**Baseline**: rule-based first, LLM fallback when confidence < 0.6, store confidence score.

**Known weakness**: rule-based confidence is heuristic; the threshold 0.6 is arbitrary; LLM doesn't have its own grounded confidence.

**To explore**:
- Calibrate threshold against eval samples (when does rule-based fail?).
- Have the LLM output structured confidence with rationale, not a number.
- Allow per-template override: a template that violates conventions gets `force_llm_classification = true`.

## 3.4 Brand Element Promotion (S3 prep work)

**Baseline**: S2 only inherits per-slide brand_elements from S1; no cross-slide promotion.

**Real S3**: shapes that recur on ≥ N slides with stable position and style get promoted.

**To explore**:
- Define stability metrics: position tolerance (EMU range), size tolerance, fill tolerance.
- Define promotion threshold N (probably 3+ for short decks, ratio-based for long decks).
- Decide whether promotion happens in S2 (extends `template_schema.json`) or in S3 (separate output).

---

# Section 4 — Operational and Logistical

Things the PRD assumes will happen but doesn't specify how.

## 4.1 Sourcing Test Templates

**The problem**: PRD §20.3 requires ≥ 2 unrelated template families for MVP. Currently 3 samples exist, all from one family ("courseplan").

**To explore**:
- T1 (academic): the existing courseplan template family is candidate; alternatively, a real graduate-program presentation template.
- T2 (corporate): need a clean source. Options: Microsoft template gallery free templates, real but anonymized template from a company contact.
- T3 (visually rich): SlidesCarnival, Slidesgo, or similar free template libraries.

**First thoughts**: avoid templates that would violate licensing if redistributed. If real templates are used, keep them out of the public repo and reference by hash.

## 4.2 Strict JSON Schema Documents

**Reviewer suggestion**: produce real `*.schema.json` JSON Schema documents alongside markdown contracts.

**Decision in v2.1**: deferred. Rationale: contracts are still evolving; double-maintaining markdown + JSON Schema is overhead before contracts stabilize.

**When to revisit**: after Phase 0C (First End-to-End Slice) runs cleanly. At that point contracts are real enough to deserve formal Schema.

**To explore**:
- Generate JSON Schema from Python dataclass / pydantic models, not by hand-writing both.
- Consider OpenAPI-style spec for the CLI commands as well.
- Decide where Schema lives: alongside code (`schemas/` directory) vs alongside docs.

## 4.3 Editability Contract (OQ-5 elaboration)

**The problem**: NFR says editable; actual boundary is undefined.

**To explore**:
- Audit python-pptx capabilities against real template shape types: which shapes round-trip cleanly through clone, which lose properties.
- Catalog placeholder types (`title`, `body`, `obj`, `pic`, `chart`, `tbl`, `dt`, `ftr`, `sldNum`, etc.) and document round-trip behavior of each.
- Define editability tiers in the contract:
  - **Tier 1 — Guaranteed editable**: title text, body text, image replacement
  - **Tier 2 — Best-effort editable**: tables (clone preserves; auto-extension does not), charts (cloned but data link breaks)
  - **Tier 3 — Image-only**: complex SmartArt, embedded videos, animation sequences

**First thoughts**: do this audit during Phase 0B when fixing the placeholder resolution bug — same code paths.

## 4.4 State Directory Convention (OQ-6 elaboration)

**The problem**: three conventions exist (`.powergen/`, `.claude/`, proposed `.powerAgen/`).

**To explore**:
- Decide whether per-project memory is MVP or V1.0.
- If MVP: pick one directory name and migrate; deprecate the others with deprecation warnings on read.
- If V1.0: keep run artifacts only (no user preferences), simpler structure.

**First thoughts**: for the MVP CLI user, per-project state is probably useful (rerun the same template, iterate on a deck). But user preferences (powerAgen.md style) may be over-engineering. Run artifacts yes, user profile no for MVP.

---

# Section 5 — Future Stages: S3, S4

PRD §18 and §19 treat S3 and S4 as "after MVP". Open exploration on what they'd actually be.

## 5.1 S3 — Cross-Slide Brand Detection: Method Design

**Approach to consider**:
- Build a per-shape feature vector: (position bucket, size bucket, fill color, line color, role-in-Recipe).
- Cluster shapes across slides by feature vector similarity.
- A cluster of size ≥ N (where N depends on deck length) with low variance → brand element.
- Output: `brand_layer.json` extending `template_schema.json` with promoted brand elements per "global slot" (e.g. `header_logo`, `footer_page_number`).

**Open**:
- Position bucketing: absolute EMU vs ratio of slide dimensions vs grid quantization?
- How to handle template-master brand elements (the "real" answer is in master XML, but co-occurrence is more reliable when templates are sloppy).

## 5.2 S4 — Layout Generalization: Method Design

**Approach to consider**:
- Extract per-slide layout patterns into a `design_pattern` representation: (alignment rule, color rule, typography rule, decoration rule).
- Cluster patterns across slides; common patterns become the template's "design language".
- Strategy C1 instantiates new slides by sampling the design language and applying it to content shape.

**Open**:
- Representation of design language: structured rules (declarative) or learned model (statistical)?
- Quality bar: a generated slide must pass "would a human designer accept this as belonging to the template"?
- Evaluation: human rubric or automated style-similarity metric?

**First thoughts**: S4 is research-grade hard. It's the real differentiator for the long term but not commercially necessary for MVP. Worth reading academic literature on style transfer in document layouts before committing to an approach.

---

# Section 6 — Interaction & UX (Post-MVP)

PRD §12 commits MVP to CLI-only. Post-MVP web/chat surface needs design.

## 6.1 Web UI: Wrapping CLI vs. Native Web App

**V1.0 decision in PRD**: thin web UI wrapping CLI.

**To explore**:
- What does "thin" actually mean? Electron with terminal embed? Web app with WebSocket to CLI process? FastAPI backend?
- File upload UX: drag-drop folder vs. file selector vs. cloud-drive integration.
- How to surface clarification questions in chat without breaking the CLI's "front-loaded clarification" model.

## 6.2 Chat-Style Generation Loop

**V2.0 territory**: actual conversational generation.

**To explore**:
- Streaming progress: how much internal state to surface (high-level only per PRD principle, but how visible?).
- Mid-generation revision: PRD says no slide-by-slide approval; chat users may demand it. What's the policy?
- Multi-turn template iteration: "make slide 3 look more like slide 7" — needs different intent parsing than initial intent.

## 6.3 Revision UX (Post-MVP feature)

**Per-slide revision is post-MVP**.

**To explore**:
- Reference resolution: "the conclusion slide", "slide 4", "the comparison one" — needs a slide-naming layer.
- Revision intent vs. initial intent: same parser or different?
- Conflict handling: revision request contradicts an earlier constraint.

---

# Section 7 — Topic Template

When adding new topics, use this template:

```
## X.Y — Topic Name

**Question / problem**: one or two sentences.

**Why deferred**: why this isn't in the PRD's MVP commitment.

**To explore**:
- specific sub-questions
- methods to consider
- evaluations needed

**First thoughts**: initial intuition that may or may not hold up.
```

Keep entries short. This is a notebook, not a specification.

---

# Section 8 — Resolved (Archive)

When topics are answered and migrated to the PRD, log them here as a one-line archive:

> *(empty — first archive entries will appear after Phase 0C)*
