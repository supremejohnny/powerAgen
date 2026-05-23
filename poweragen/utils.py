from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EMU_PER_INCH = 914400


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str, fallback: str = "deck") -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return slug[:48] or fallback


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_text_file(path: Path, limit: int = 12000) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    return text[:limit]


def split_points(text: str, fallback_topic: str, count: int = 10) -> list[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    pieces = [
        piece.strip(" -:;,.，。；！!?")
        for piece in re.split(r"[。；;.!?\n\r]+", text)
        if piece.strip(" -:;,.，。；！!?")
    ]
    points: list[str] = []
    for piece in pieces:
        if 5 <= len(piece) <= 110 and piece not in points:
            points.append(piece)
    defaults = [
        f"{fallback_topic} 的背景和目标",
        "当前约束与关键风险",
        "最重要的用户需求",
        "可执行的方案路径",
        "资源、时间与质量之间的取舍",
        "阶段性里程碑",
        "验证方式与成功标准",
        "下一步行动建议",
        "需要持续观察的问题",
        "预期产出与复盘方式",
    ]
    for item in defaults:
        if len(points) >= count:
            break
        if item not in points:
            points.append(item)
    return points[:count]


def detect_file_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pptx":
        return "pptx"
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".docx":
        return "docx"
    if suffix == ".txt":
        return "txt"
    if suffix == ".md":
        return "md"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return "image"
    return "data"


def shape_text(shape: Any) -> str:
    if getattr(shape, "has_text_frame", False):
        return shape.text_frame.text.strip()
    return ""


def iter_shapes(shapes: Any):
    for shape in shapes:
        yield shape
        if hasattr(shape, "shapes"):
            yield from iter_shapes(shape.shapes)


def clear_text_frame(text_frame: Any) -> None:
    text_frame.clear()
    text_frame.paragraphs[0].text = ""


@dataclass
class Trace:
    run_dir: Path
    steps: list[dict[str, Any]] = field(default_factory=list)

    def log(self, step: str, status: str, message: str, **extra: Any) -> None:
        entry = {
            "at": now_iso(),
            "step": step,
            "status": status,
            "message": message,
            **extra,
        }
        self.steps.append(entry)
        log_path = self.run_dir / "run.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{entry['at']}] {step} {status}: {message}\n")
        write_json(self.run_dir / "agent_trace.json", {"schema_version": "0.1", "steps": self.steps})
