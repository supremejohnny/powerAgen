# PowerAgen MVP Progress

## Milestone

Phase 1 is a runnable MVP skeleton for PRD v2.1. It proves that a template-aware generation pipeline can produce editable PPTX output, save inspectable artifacts, and run a local evaluation loop.

## Assumptions

- Phase 1 may use deterministic rules instead of real LLM calls.
- `test/courseplan_test.pptx` is the primary MVP smoke template because it exercises Strategy B grid extension.
- `test/presentation_test.pptx` is a second template family used for clone-fill and cross-template smoke testing.
- Open exploration topics are deferred until after this milestone.

## Completed

- Python package: `poweragen`
- Agent pipeline:
  - intake
  - file manifest
  - context distillation
  - template compilation
  - deck outline
  - layout matching
  - slide spec generation
  - PPTX rendering
  - validation
- Strategy A clone-fill
- Strategy B grid extension MVP slice
- Run artifacts, `agent_trace.json`, and `run.log`
- CLI commands:
  - `generate`
  - `eval`
  - `eval-suite`
  - `web`
- Web UI:
  - `/` user-facing generation entry
  - `/developer` debug/artifact entry
- Pytest smoke coverage

## Latest Evaluation

Commands:

```powershell
python -m poweragen.cli eval --template test/courseplan_test.pptx --run-dir runs/eval-smoke
python -m poweragen.cli eval --template test/presentation_test.pptx --run-dir runs/eval-presentation --no-require-strategy-b
python -m poweragen.cli eval-suite --run-dir runs/eval-suite
python -m pytest -q
```

Expected result:

- `courseplan_test.pptx`: pass, includes Strategy B
- `presentation_test.pptx`: pass with Strategy B optional
- suite: pass, at least one deck includes Strategy B
- pytest: pass

## Phase 2 Direction

Phase 2 should add visual pass/fail evaluation:

1. Export template and generated PPTX slides to PNG.
2. Compute deterministic visual metrics.
3. Call SenseNova vision model for slide-by-slide design comparison.
4. Save `visual_evaluation_report.json`.
5. Show screenshots, diffs, scores, and comments in the developer UI.

Reserved API configuration:

```powershell
$env:SENSE_API_KEY="..."
$env:SENSE_BASE_URL="https://token.sensenova.cn/v1"
$env:SENSE_TEXT_MODEL="deepseek-v4-flash"
$env:SENSE_VISION_MODEL="sensenova-6.7-flash-lite"
```

## Known Limits

- Template compiler is still heuristic.
- Strategy B only covers regular grid extension.
- No screenshot-based visual evaluation yet.
- No PDF/DOCX content distillation yet.
