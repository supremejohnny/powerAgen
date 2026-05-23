from __future__ import annotations

from typing import Any

from .utils import split_points


def build_outline(intent: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    slide_count = intent.get("slide_count") or 8
    topic = intent["topic"]
    prompt_text = context["aggregated"]["topic_summary"]
    points = split_points(prompt_text, topic, count=max(10, slide_count + 3))
    blueprints = [
        ("cover", "single", 0, topic, f"围绕 {topic} 建立同一页叙事入口"),
        ("agenda", "list", 4, "今天讨论什么", "让听众先看到结构和重点"),
        ("divider", "single", 0, "关键观察", "切入最重要的背景判断"),
        ("content", "list", 3, "核心发现", "提炼可直接使用的发现"),
        ("grid", "grid", 5, "行动路径", "把建议拆成可执行模块"),
        ("divider", "single", 0, "落地计划", "从分析过渡到行动"),
        ("sequence", "sequence", 4, "执行节奏", "说明下一阶段推进顺序"),
        ("closing", "single", 0, "下一步", "收束结论并给出行动"),
    ]
    while len(blueprints) < slide_count:
        idx = len(blueprints) + 1
        blueprints.insert(-1, ("content", "list", 3, f"补充分析 {idx}", "展开额外信息"))

    slides = []
    for slide_no, (preferred_family, kind, item_count, title, intent_text) in enumerate(
        blueprints[:slide_count], start=1
    ):
        slides.append(
            {
                "slide_no": slide_no,
                "purpose": intent_text,
                "title": title,
                "intent": intent_text,
                "content_shape": {"kind": kind, "item_count": item_count or None},
                "evidence_refs": ["prompt"],
                "draft_points": points[(slide_no - 1) : (slide_no - 1) + max(item_count or 2, 2)],
                "preferred_family": preferred_family,
            }
        )
    return {"schema_version": "0.1", "title": topic, "slides": slides}


def match_layouts(outline: dict[str, Any], template_schema: dict[str, Any], strictness: str) -> dict[str, Any]:
    catalog = template_schema["layout_catalog"]
    grid_extendable = template_schema["extension_capabilities"]["grid_extendable"]
    plan = []
    for slide in outline["slides"]:
        kind = slide["content_shape"]["kind"]
        item_count = slide["content_shape"].get("item_count")
        selected = _select_template(catalog, kind, item_count, slide.get("preferred_family"))
        strategy = "clone_fill"
        extension = None
        reason = "matched nearest template family"

        if (
            strictness != "strict"
            and kind == "grid"
            and item_count
            and grid_extendable
        ):
            grid_source = _best_grid_source(catalog, grid_extendable)
            if grid_source and item_count > (grid_source.get("item_count") or 0):
                selected = grid_source
                strategy = "template_extend"
                extension = {"kind": "grid", "target_count": item_count}
                reason = "grid item count exceeds source grid and Strategy B is allowed"

        plan.append(
            {
                "slide_no": slide["slide_no"],
                "selected_template_slide_index": selected["slide_index"] if selected else None,
                "layout_family": selected["layout_family"] if selected else "content",
                "layout_variant": selected["layout_variant"] if selected else "generic",
                "rendering_strategy": strategy,
                "extension_params": extension,
                "match_reason": reason,
                "match_confidence": selected["confidence"] if selected else 0.2,
            }
        )
    return {"schema_version": "0.1", "plan": plan}


def build_slide_specs(
    outline: dict[str, Any],
    layout_plan: dict[str, Any],
    template_schema: dict[str, Any],
) -> dict[str, Any]:
    recipes = {recipe["slide_index"]: recipe for recipe in template_schema["slides"]}
    specs = []
    for outline_slide, plan in zip(outline["slides"], layout_plan["plan"]):
        template_ref = plan["selected_template_slide_index"]
        recipe = recipes.get(template_ref) if template_ref else None
        draft_points = outline_slide.get("draft_points", [])
        body = "\n".join(f"- {point}" for point in draft_points[:4])
        slot_values = []
        if recipe:
            for slot in recipe["slots"]:
                field = slot["field"]
                value = _slot_value(field, outline_slide["title"], outline_slide["intent"], body, draft_points)
                slot_values.append(
                    {
                        "slot_id": field,
                        "value_type": "text",
                        "value": value,
                        "fit_policy": "shrink_or_summarize",
                    }
                )

        item_groups = []
        if outline_slide["content_shape"]["kind"] == "grid":
            count = outline_slide["content_shape"].get("item_count") or 5
            points = draft_points
            items = []
            for idx in range(count):
                point = points[idx % len(points)] if points else f"行动 {idx + 1}"
                items.append(
                    {
                        "label": f"{idx + 1:02d}",
                        "title": point[:18],
                        "body": point if len(point) <= 80 else point[:77] + "...",
                    }
                )
            item_groups.append({"slot_id": "grid_items", "items": items})

        specs.append(
            {
                "slide_no": outline_slide["slide_no"],
                "rendering_strategy": plan["rendering_strategy"],
                "template_ref": template_ref,
                "recipe_ref": recipe,
                "slot_values": slot_values,
                "item_groups": item_groups,
                "extension_params": plan["extension_params"],
                "design_tokens": template_schema["design_system"],
            }
        )
    return {"schema_version": "0.1", "specs": specs}


def _slot_value(
    field: str,
    title: str,
    intent: str,
    body: str,
    points: list[str],
) -> str:
    if field == "title":
        return title
    if field in {"subtitle", "eyebrow"}:
        return intent
    if field == "body":
        return body
    if points:
        idx = abs(hash(field)) % len(points)
        return points[idx]
    return " "


def _select_template(
    catalog: list[dict[str, Any]], kind: str, item_count: int | None, preferred_family: str | None = None
) -> dict[str, Any] | None:
    family_map = {
        "single": ["cover", "divider", "content"],
        "list": ["content", "agenda", "sequence"],
        "grid": ["grid", "content"],
        "sequence": ["sequence", "content", "grid"],
        "comparison": ["comparison", "content"],
        "data": ["chart", "content"],
    }
    families = family_map.get(kind, ["content"])
    if preferred_family and preferred_family in {item["layout_family"] for item in catalog}:
        families = [preferred_family] + [family for family in families if family != preferred_family]
    candidates = [item for family in families for item in catalog if item["layout_family"] == family]
    if not candidates:
        candidates = catalog
    if item_count:
        candidates.sort(key=lambda item: abs((item.get("item_count") or item_count) - item_count))
    return candidates[0] if candidates else None


def _best_grid_source(
    catalog: list[dict[str, Any]], grid_extendable: list[int]
) -> dict[str, Any] | None:
    grids = [item for item in catalog if item["slide_index"] in grid_extendable]
    if not grids:
        return None
    grids.sort(key=lambda item: (item.get("item_count") or 0, -item["confidence"]), reverse=True)
    return grids[0]
