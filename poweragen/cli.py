from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .agent import PowerAgen
from .evaluate import DEFAULT_EVAL_PROMPT, run_evaluation, run_evaluation_suite

app = typer.Typer(help="PowerAgen template-aware PPTX generation MVP.")
console = Console()


@app.command()
def generate(
    template: Path = typer.Option(..., "--template", "-t", help="Path to a PPTX template."),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Deck prompt or brief."),
    slides: int = typer.Option(8, "--slides", "-s", min=1, max=30, help="Slide count."),
    run_dir: Optional[Path] = typer.Option(None, "--run-dir", help="Directory for run artifacts."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output PPTX path."),
    context: list[Path] = typer.Option([], "--context", "-c", help="Optional TXT/MD context file."),
    language: str = typer.Option("zh-CN", "--language", help="BCP-47 language tag."),
    audience: str = typer.Option("academic", "--audience", help="Target audience."),
    strictness: str = typer.Option("adaptive", "--strictness", help="strict/adaptive/creative."),
) -> None:
    result = PowerAgen().run(
        template_path=template,
        prompt=prompt,
        slide_count=slides,
        run_dir=run_dir,
        output_path=output,
        context_paths=context,
        language=language,
        audience=audience,
        visual_strictness=strictness,
    )
    console.print(f"[green]Done[/green] status={result['status']}")
    console.print(f"Output: {result['output_path']}")
    console.print(f"Run dir: {result['run_dir']}")


@app.command(name="eval")
def eval_command(
    template: Path = typer.Option(Path("test/courseplan_test.pptx"), "--template", "-t"),
    run_dir: Path = typer.Option(Path("runs/eval-smoke"), "--run-dir"),
    prompt: str = typer.Option(DEFAULT_EVAL_PROMPT, "--prompt", "-p"),
    slides: int = typer.Option(8, "--slides", "-s"),
    require_strategy_b: bool = typer.Option(True, "--require-strategy-b/--no-require-strategy-b"),
) -> None:
    report = run_evaluation(template, run_dir, prompt, slides, require_strategy_b)
    table = Table(title=f"PowerAgen Evaluation: {report['status']}")
    table.add_column("Check")
    table.add_column("Result")
    table.add_column("Detail")
    for check in report["checks"]:
        table.add_row(check["name"], "pass" if check["passed"] else "fail", check["detail"])
    console.print(table)
    if report["status"] != "pass":
        raise typer.Exit(1)


@app.command(name="eval-suite")
def eval_suite_command(
    template: list[Path] = typer.Option(
        [Path("test/courseplan_test.pptx"), Path("test/presentation_test.pptx")],
        "--template",
        "-t",
    ),
    run_dir: Path = typer.Option(Path("runs/eval-suite"), "--run-dir"),
    prompt: str = typer.Option(DEFAULT_EVAL_PROMPT, "--prompt", "-p"),
    slides: int = typer.Option(8, "--slides", "-s"),
) -> None:
    report = run_evaluation_suite(template, run_dir, prompt, slides)
    table = Table(title=f"PowerAgen Evaluation Suite: {report['status']}")
    table.add_column("Check")
    table.add_column("Result")
    table.add_column("Detail")
    for check in report["checks"]:
        table.add_row(check["name"], "pass" if check["passed"] else "fail", check["detail"])
    console.print(table)
    if report["status"] != "pass":
        raise typer.Exit(1)


@app.command()
def web(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
) -> None:
    import uvicorn

    uvicorn.run("poweragen.web:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()
