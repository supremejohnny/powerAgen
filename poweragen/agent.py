from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .planner import build_outline, build_slide_specs, match_layouts
from .renderer import PptxRenderer
from .template_compiler import TemplateCompiler
from .utils import (
    Trace,
    detect_file_type,
    ensure_dir,
    now_iso,
    read_text_file,
    slugify,
    split_points,
    write_json,
)
from .validator import PptxValidator


class PowerAgen:
    def run(
        self,
        template_path: Path,
        prompt: str,
        slide_count: int = 8,
        run_dir: Path | None = None,
        output_path: Path | None = None,
        context_paths: list[Path] | None = None,
        language: str = "zh-CN",
        audience: str = "academic",
        visual_strictness: str = "adaptive",
    ) -> dict[str, Any]:
        template_path = template_path.resolve()
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        context_paths = [path.resolve() for path in (context_paths or [])]
        topic = self._topic_from_prompt(prompt)
        run_dir = (run_dir or Path("runs") / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(topic)}").resolve()
        ensure_dir(run_dir)
        trace = Trace(run_dir)

        trace.log("intake", "start", "Building user intent.")
        intent = {
            "schema_version": "0.1",
            "task_type": "generate_deck",
            "topic": topic,
            "audience": audience,
            "slide_count": slide_count,
            "language": language,
            "template_required": True,
            "template_path": str(template_path),
            "context_paths": [str(path) for path in context_paths],
            "visual_strictness": visual_strictness,
            "output_format": "pptx",
            "output_path": str(output_path) if output_path else None,
        }
        write_json(run_dir / "user_intent.json", intent)
        trace.log("intake", "done", "Saved user_intent.json.")

        trace.log("manifest", "start", "Scanning input files.")
        manifest = self._file_manifest(template_path, context_paths)
        write_json(run_dir / "file_manifest.json", manifest)
        trace.log("manifest", "done", "Saved file_manifest.json.", file_count=len(manifest["files"]))

        trace.log("context", "start", "Distilling prompt and source files.")
        context = self._distill_context(prompt, context_paths, topic)
        write_json(run_dir / "context_distilled.json", context)
        trace.log("context", "done", "Saved context_distilled.json.")

        trace.log("template_compile", "start", "Compiling template schema.")
        template_schema = TemplateCompiler().compile(template_path)
        write_json(run_dir / "template_schema.json", template_schema)
        trace.log(
            "template_compile",
            "done",
            "Saved template_schema.json.",
            slide_count=len(template_schema["slides"]),
            grid_extendable=template_schema["extension_capabilities"]["grid_extendable"],
        )

        trace.log("planning", "start", "Planning deck outline.")
        outline = build_outline(intent, context)
        write_json(run_dir / "deck_outline.json", outline)
        trace.log("planning", "done", "Saved deck_outline.json.", slide_count=len(outline["slides"]))

        trace.log("layout_matching", "start", "Matching slides to template layouts.")
        layout_plan = match_layouts(outline, template_schema, visual_strictness)
        write_json(run_dir / "slide_layout_plan.json", layout_plan)
        trace.log("layout_matching", "done", "Saved slide_layout_plan.json.")

        trace.log("spec_generation", "start", "Building renderer specs.")
        slide_specs = build_slide_specs(outline, layout_plan, template_schema)
        write_json(run_dir / "slide_specs.json", slide_specs)
        trace.log("spec_generation", "done", "Saved slide_specs.json.")

        output_path = (output_path or run_dir / "output.pptx").resolve()
        trace.log("rendering", "start", "Rendering editable PPTX.")
        PptxRenderer().render(template_path, slide_specs, output_path)
        trace.log("rendering", "done", "Saved output.pptx.", output_path=str(output_path))

        trace.log("validation", "start", "Validating generated PPTX.")
        validation_report = PptxValidator().validate(output_path, slide_specs, layout_plan)
        write_json(run_dir / "validation_report.json", validation_report)
        trace.log("validation", validation_report["status"], "Saved validation_report.json.")

        result = {
            "run_dir": str(run_dir),
            "output_path": str(output_path),
            "status": validation_report["status"],
            "artifacts": [
                "user_intent.json",
                "file_manifest.json",
                "context_distilled.json",
                "template_schema.json",
                "deck_outline.json",
                "slide_layout_plan.json",
                "slide_specs.json",
                "validation_report.json",
                "agent_trace.json",
                "run.log",
                "output.pptx",
            ],
        }
        write_json(run_dir / "run_result.json", {"schema_version": "0.1", **result, "generated_at": now_iso()})
        return result

    def _topic_from_prompt(self, prompt: str) -> str:
        clean = " ".join((prompt or "").split()).strip()
        if not clean:
            return "Untitled Deck"
        for splitter in ["。", ".", "\n", "；", ";"]:
            if splitter in clean:
                clean = clean.split(splitter)[0]
        return clean[:42]

    def _file_manifest(self, template_path: Path, context_paths: list[Path]) -> dict[str, Any]:
        files = [
            {
                "path": str(template_path),
                "type": "pptx",
                "role": "template_candidate",
                "size_bytes": template_path.stat().st_size,
            }
        ]
        for path in context_paths:
            role = "context" if path.exists() else "ignored"
            files.append(
                {
                    "path": str(path),
                    "type": detect_file_type(path),
                    "role": role,
                    "size_bytes": path.stat().st_size if path.exists() else 0,
                }
            )
        return {"schema_version": "0.1", "files": files}

    def _distill_context(self, prompt: str, context_paths: list[Path], topic: str) -> dict[str, Any]:
        sources = [
            {
                "source_id": "prompt",
                "path": "prompt",
                "type": "txt",
                "summary": prompt[:300] or topic,
                "key_points": [
                    {"claim": point, "support": "prompt", "source_ref": "prompt"}
                    for point in split_points(prompt, topic, count=8)
                ],
                "usable_figures": [],
                "tables": [],
            }
        ]
        gathered_text = [prompt]
        for idx, path in enumerate(context_paths, start=1):
            if not path.exists() or detect_file_type(path) not in {"txt", "md"}:
                continue
            text = read_text_file(path)
            gathered_text.append(text)
            points = split_points(text, topic, count=8)
            sources.append(
                {
                    "source_id": f"source_{idx}",
                    "path": str(path),
                    "type": detect_file_type(path),
                    "summary": " ".join(points[:2]),
                    "key_points": [
                        {"claim": point, "support": str(path), "source_ref": f"source_{idx}"}
                        for point in points
                    ],
                    "usable_figures": [],
                    "tables": [],
                }
            )
        combined = "\n".join(gathered_text)
        sections = [point[:28] for point in split_points(combined, topic, count=6)]
        return {
            "schema_version": "0.1",
            "sources": sources,
            "aggregated": {
                "topic_summary": combined[:1600] or topic,
                "suggested_sections": sections,
            },
        }
