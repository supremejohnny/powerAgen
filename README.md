# PowerAgen

PowerAgen is a template-aware PPTX generation agent MVP. It reads a user-provided PowerPoint template, compiles lightweight template knowledge, plans a deck, matches slides to template layouts, and generates an editable `.pptx`.

This repository currently represents the Phase 1 milestone:

- deterministic local generation with no required LLM call
- Strategy A clone-fill as the main rendering path
- Strategy B grid extension as a narrow MVP slice
- inspectable run artifacts for every generation
- CLI, evaluation loop, and a thin Web UI with a user view and developer debug view

## Implemented Scope

- Saves the PRD artifacts under each run directory: `user_intent.json`, `file_manifest.json`, `context_distilled.json`, `template_schema.json`, `deck_outline.json`, `slide_layout_plan.json`, `slide_specs.json`, `validation_report.json`
- Extracts slide recipes, layout catalog, basic design tokens, and grid extension capability from PPTX templates
- Renders editable PPTX output
- Supports two test templates: `test/courseplan_test.pptx` and `test/presentation_test.pptx`
- Provides `/` for user-facing generation and `/developer` for trace/artifact inspection

## Environment Setup

Use Python 3.12.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

## LLM API Configuration

Phase 1 does not require API calls. The following variables are reserved for Phase 2 text and vision evaluation with SenseNova-compatible OpenAI SDK access.

Do not hard-code API keys in source files.

```powershell
$env:SENSE_API_KEY="..."
$env:SENSE_BASE_URL="https://token.sensenova.cn/v1"
$env:SENSE_TEXT_MODEL="deepseek-v4-flash"
$env:SENSE_VISION_MODEL="sensenova-6.7-flash-lite"
```

Planned Phase 2 model split:

- Text planning and repair suggestions: `deepseek-v4-flash`
- Vision slide comparison: `sensenova-6.7-flash-lite`

## Run CLI Generation

```powershell
python -m poweragen.cli generate `
  --template test/courseplan_test.pptx `
  --prompt "Create an 8-slide report about AI-assisted course planning, including background, problems, findings, action path, execution rhythm, and next steps." `
  --slides 8 `
  --run-dir runs/demo
```

Default output:

```text
runs/demo/output.pptx
```

All intermediate artifacts and logs are written to the same run directory.

## Run Web UI

```powershell
python -m poweragen.cli web --host 127.0.0.1 --port 8000
```

Open:

- User UI: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Developer UI: [http://127.0.0.1:8000/developer](http://127.0.0.1:8000/developer)

## Evaluation Loop

Single-template MVP smoke test with Strategy B required:

```powershell
python -m poweragen.cli eval --template test/courseplan_test.pptx --run-dir runs/eval-smoke
```

Second-template smoke test where Strategy B is optional:

```powershell
python -m poweragen.cli eval --template test/presentation_test.pptx --run-dir runs/eval-presentation --no-require-strategy-b
```

Two-template suite:

```powershell
python -m poweragen.cli eval-suite --run-dir runs/eval-suite
```

Unit tests:

```powershell
python -m pytest -q
```

The evaluation checks:

- output PPTX opens with `python-pptx`
- slide count is correct
- core artifacts exist
- Strategy A clone-fill ratio is at least 70%
- at least one suite deck uses Strategy B grid extension
- validator finds no unresolved placeholder tokens

## Current Limitations

- Template understanding is heuristic, not yet the full LLM/Vision compiler described in the PRD.
- Strategy B only supports regular grid extension.
- PDF/DOCX context distillation is not implemented yet.
- `template_similarity_estimate` is an engineering estimate. Phase 2 should add screenshot export, deterministic visual metrics, and SenseNova vision judging.
