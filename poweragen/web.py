from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from .agent import PowerAgen

app = FastAPI(title="PowerAgen")
ROOT = Path.cwd()
RUNS_DIR = ROOT / "runs"


class RunRequest(BaseModel):
    prompt: str
    template_path: str = "test/courseplan_test.pptx"
    slide_count: int = 8
    language: str = "zh-CN"
    audience: str = "academic"
    strictness: str = "adaptive"


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return USER_HTML


@app.get("/developer", response_class=HTMLResponse)
def developer() -> str:
    return DEVELOPER_HTML


@app.post("/api/runs")
def create_run(payload: RunRequest) -> JSONResponse:
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt is required")
    template = (ROOT / payload.template_path).resolve()
    if not template.exists():
        raise HTTPException(status_code=404, detail=f"template not found: {template}")
    result = PowerAgen().run(
        template_path=template,
        prompt=payload.prompt,
        slide_count=payload.slide_count,
        language=payload.language,
        audience=payload.audience,
        visual_strictness=payload.strictness,
    )
    return JSONResponse(result)


@app.get("/api/runs")
def list_runs() -> JSONResponse:
    runs: list[dict[str, Any]] = []
    if RUNS_DIR.exists():
        for run_dir in sorted(RUNS_DIR.iterdir(), key=lambda path: path.stat().st_mtime, reverse=True):
            if not run_dir.is_dir():
                continue
            result_path = run_dir / "run_result.json"
            validation_path = run_dir / "validation_report.json"
            data = {"run_id": run_dir.name, "run_dir": str(run_dir), "status": "unknown"}
            if result_path.exists():
                data.update(json.loads(result_path.read_text(encoding="utf-8")))
            elif validation_path.exists():
                data["status"] = json.loads(validation_path.read_text(encoding="utf-8")).get("status", "unknown")
            runs.append(data)
    return JSONResponse({"runs": runs})


@app.get("/api/runs/{run_id}/artifact/{artifact_name}")
def read_artifact(run_id: str, artifact_name: str):
    run_dir = _run_dir(run_id)
    artifact = run_dir / Path(artifact_name).name
    if not artifact.exists():
        raise HTTPException(status_code=404, detail="artifact not found")
    if artifact.suffix == ".json":
        return JSONResponse(json.loads(artifact.read_text(encoding="utf-8")))
    if artifact.suffix == ".pptx":
        return FileResponse(artifact)
    return PlainTextResponse(artifact.read_text(encoding="utf-8", errors="ignore"))


@app.get("/api/runs/{run_id}/download")
def download_output(run_id: str):
    run_dir = _run_dir(run_id)
    output = run_dir / "output.pptx"
    if not output.exists():
        raise HTTPException(status_code=404, detail="output not found")
    return FileResponse(output, filename=f"{run_id}.pptx")


def _run_dir(run_id: str) -> Path:
    candidate = (RUNS_DIR / Path(run_id).name).resolve()
    if not str(candidate).startswith(str(RUNS_DIR.resolve())) or not candidate.exists():
        raise HTTPException(status_code=404, detail="run not found")
    return candidate


BASE_CSS = """
<style>
  :root {
    color-scheme: light;
    --ink: #17202a;
    --muted: #5b6776;
    --line: #d8dee8;
    --panel: #ffffff;
    --soft: #f5f7fa;
    --accent: #0f766e;
    --accent-strong: #0b5d56;
    --warn: #9a3412;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: Inter, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
    color: var(--ink);
    background: var(--soft);
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 58px;
    padding: 0 24px;
    border-bottom: 1px solid var(--line);
    background: var(--panel);
  }
  a { color: var(--accent); text-decoration: none; }
  main {
    display: grid;
    grid-template-columns: minmax(360px, 1.1fr) minmax(320px, 0.9fr);
    gap: 1px;
    min-height: calc(100vh - 58px);
    background: var(--line);
  }
  section {
    background: var(--panel);
    padding: 24px;
    min-width: 0;
  }
  h1, h2 { margin: 0; letter-spacing: 0; }
  h1 { font-size: 18px; }
  h2 { font-size: 16px; margin-bottom: 16px; }
  label { display: block; margin: 14px 0 7px; color: var(--muted); font-size: 13px; }
  textarea, input, select {
    width: 100%;
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 10px 12px;
    font: inherit;
    background: #fff;
  }
  textarea { min-height: 190px; resize: vertical; line-height: 1.5; }
  button {
    margin-top: 18px;
    border: 0;
    border-radius: 6px;
    background: var(--accent);
    color: white;
    font-weight: 700;
    padding: 11px 16px;
    cursor: pointer;
  }
  button:disabled { opacity: .55; cursor: wait; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .chat {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 18px;
  }
  .bubble {
    max-width: 86%;
    border-radius: 8px;
    padding: 10px 12px;
    line-height: 1.45;
    white-space: pre-wrap;
  }
  .assistant { background: #eef7f5; border: 1px solid #c9e6e0; }
  .user { align-self: flex-end; background: #f1f5f9; border: 1px solid var(--line); }
  pre {
    overflow: auto;
    max-height: 58vh;
    padding: 14px;
    background: #101828;
    color: #e5edf6;
    border-radius: 6px;
    line-height: 1.45;
  }
  .artifact-list { display: grid; gap: 8px; }
  .artifact-list button {
    margin: 0;
    background: transparent;
    color: var(--ink);
    border: 1px solid var(--line);
    text-align: left;
    font-weight: 500;
  }
  .status { color: var(--accent-strong); font-weight: 700; }
  .warn { color: var(--warn); }
  @media (max-width: 860px) {
    main { grid-template-columns: 1fr; }
    .row { grid-template-columns: 1fr; }
  }
</style>
"""


USER_HTML = f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PowerAgen</title>
  {BASE_CSS}
</head>
<body>
  <header>
    <h1>PowerAgen</h1>
    <nav><a href="/developer">Developer</a></nav>
  </header>
  <main>
    <section>
      <div class="chat" id="chat">
        <div class="bubble assistant">把主题或材料说明发给我，我会按模板生成一份可编辑 PPTX。</div>
      </div>
      <form id="run-form">
        <label for="prompt">内容</label>
        <textarea id="prompt" name="prompt">为研究生做一份关于 AI 辅助课程规划的 8 页汇报，内容包括背景、核心问题、关键发现、行动路径、执行节奏和下一步。</textarea>
        <div class="row">
          <div>
            <label for="template">模板路径</label>
            <input id="template" name="template" value="test/courseplan_test.pptx" />
          </div>
          <div>
            <label for="slides">页数</label>
            <input id="slides" name="slides" type="number" min="1" max="30" value="8" />
          </div>
        </div>
        <button id="run" type="submit">生成 PPTX</button>
      </form>
    </section>
    <section>
      <h2>输出</h2>
      <div id="result">等待运行。</div>
      <pre id="log" hidden></pre>
    </section>
  </main>
  <script>
    const form = document.querySelector("#run-form");
    const chat = document.querySelector("#chat");
    const result = document.querySelector("#result");
    const log = document.querySelector("#log");
    const button = document.querySelector("#run");
    form.addEventListener("submit", async (event) => {{
      event.preventDefault();
      const prompt = document.querySelector("#prompt").value;
      const template = document.querySelector("#template").value;
      const slides = Number(document.querySelector("#slides").value || 8);
      chat.insertAdjacentHTML("beforeend", `<div class="bubble user">${{prompt}}</div>`);
      button.disabled = true;
      result.innerHTML = '<span class="status">运行中</span>';
      log.hidden = true;
      const response = await fetch("/api/runs", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ prompt, template_path: template, slide_count: slides }})
      }});
      const data = await response.json();
      button.disabled = false;
      if (!response.ok) {{
        result.innerHTML = `<span class="warn">${{data.detail || "运行失败"}}</span>`;
        return;
      }}
      const runId = data.run_dir.split(/[\\\\/]/).pop();
      chat.insertAdjacentHTML("beforeend", `<div class="bubble assistant">已生成：${{data.output_path}}\\n状态：${{data.status}}</div>`);
      result.innerHTML = `
        <p>状态：<span class="status">${{data.status}}</span></p>
        <p><a href="/api/runs/${{runId}}/download">下载 output.pptx</a></p>
        <p><a href="/developer?run=${{runId}}">查看运行过程</a></p>
      `;
      const logText = await fetch(`/api/runs/${{runId}}/artifact/run.log`).then(r => r.text());
      log.hidden = false;
      log.textContent = logText;
    }});
  </script>
</body>
</html>
"""


DEVELOPER_HTML = f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PowerAgen Developer</title>
  {BASE_CSS}
</head>
<body>
  <header>
    <h1>PowerAgen Developer</h1>
    <nav><a href="/">User</a></nav>
  </header>
  <main>
    <section>
      <h2>Runs</h2>
      <div class="artifact-list" id="runs"></div>
    </section>
    <section>
      <h2 id="artifact-title">Artifacts</h2>
      <div class="artifact-list" id="artifacts"></div>
      <pre id="viewer">选择一个 run。</pre>
    </section>
  </main>
  <script>
    const runsEl = document.querySelector("#runs");
    const artifactsEl = document.querySelector("#artifacts");
    const viewer = document.querySelector("#viewer");
    const artifactTitle = document.querySelector("#artifact-title");
    const artifacts = [
      "agent_trace.json",
      "run.log",
      "user_intent.json",
      "template_schema.json",
      "deck_outline.json",
      "slide_layout_plan.json",
      "slide_specs.json",
      "validation_report.json",
      "evaluation_report.json"
    ];
    async function loadRuns() {{
      const data = await fetch("/api/runs").then(r => r.json());
      runsEl.innerHTML = "";
      data.runs.forEach(run => {{
        const id = run.run_dir.split(/[\\\\/]/).pop();
        const button = document.createElement("button");
        button.textContent = `${{id}} · ${{run.status}}`;
        button.onclick = () => selectRun(id);
        runsEl.appendChild(button);
      }});
      const params = new URLSearchParams(location.search);
      if (params.get("run")) selectRun(params.get("run"));
    }}
    function selectRun(id) {{
      artifactTitle.textContent = id;
      artifactsEl.innerHTML = "";
      artifacts.forEach(name => {{
        const button = document.createElement("button");
        button.textContent = name;
        button.onclick = async () => {{
          const response = await fetch(`/api/runs/${{id}}/artifact/${{name}}`);
          viewer.textContent = await response.text();
        }};
        artifactsEl.appendChild(button);
      }});
      fetch(`/api/runs/${{id}}/artifact/agent_trace.json`).then(r => r.text()).then(t => viewer.textContent = t);
    }}
    loadRuns();
  </script>
</body>
</html>
"""
