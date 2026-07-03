import html
import json
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = ROOT_DIR / "results"
REPORTS_DIR = ROOT_DIR / "reports"


def load_latest_benchmark() -> tuple[Path | None, dict | None]:
    print("[ReportGenerator] Loading latest benchmark...")
    if not RESULTS_DIR.exists():
        print("[ReportGenerator] benchmark/results folder does not exist.")
        return None, None

    candidates = sorted(
        RESULTS_DIR.glob("benchmark_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        print("[ReportGenerator] No benchmark_*.json files found.")
        return None, None

    latest = candidates[0]
    with latest.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return latest, data


def generate_reports() -> dict | None:
    benchmark_path, benchmark = load_latest_benchmark()
    if benchmark is None:
        return None

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    markdown_path = REPORTS_DIR / f"report_{timestamp}.md"
    html_path = REPORTS_DIR / f"report_{timestamp}.html"

    print("[ReportGenerator] Generating markdown report...")
    markdown = build_markdown_report(benchmark_path, benchmark)
    markdown_path.write_text(markdown, encoding="utf-8")

    print("[ReportGenerator] Generating html report...")
    html_report = build_html_report(benchmark_path, benchmark)
    html_path.write_text(html_report, encoding="utf-8")

    print(f"[ReportGenerator] Report saved: {markdown_path}")
    print(f"[ReportGenerator] Report saved: {html_path}")
    return {
        "benchmark_path": str(benchmark_path),
        "markdown_path": str(markdown_path),
        "html_path": str(html_path),
    }


def build_markdown_report(benchmark_path: Path, benchmark: dict) -> str:
    summary = summarize(benchmark)
    results = benchmark.get("results") or []
    best_run = summary["best_run"]
    failed_runs = [result for result in results if not result.get("success")]

    lines = [
        "# Benchmark Report",
        "",
        f"Source benchmark: `{benchmark_path}`",
        "",
        "## Summary",
        "",
        f"- total runs: {summary['total']}",
        f"- successful runs: {summary['successful']}",
        f"- failed runs: {summary['failed']}",
        f"- average best_score: {summary['average_best_score']:.3f}",
        f"- retry rate: {summary['retry_rate']:.2%}",
        f"- best run id: {summary['best_run_id']}",
        f"- worst run id: {summary['worst_run_id']}",
        "",
        "## Results Table",
        "",
        "| id | user_prompt | provider | success | best_score | retry_needed | image_path | debug_report_path | prompt_preview_path |",
        "|---|---|---|---|---:|---|---|---|---|",
    ]

    for result in results:
        lines.append(
            "| {id} | {prompt} | {provider} | {success} | {score:.3f} | {retry} | {image} | {debug} | {preview} |".format(
                id=_md(result.get("id")),
                prompt=_md(result.get("user_prompt")),
                provider=_md(result.get("provider")),
                success=_md(result.get("success")),
                score=_score(result),
                retry=_md(result.get("retry_needed")),
                image=_md(result.get("image_path")),
                debug=_md(result.get("debug_report_path")),
                preview=_md(result.get("prompt_preview_path")),
            )
        )

    lines.extend(["", "## Best Run", ""])
    if best_run:
        lines.extend(_run_summary(best_run))
    else:
        lines.append("No successful run found.")

    lines.extend(["", "## Failed Runs", ""])
    if failed_runs:
        for failed in failed_runs:
            lines.append(f"- `{failed.get('id')}`: {failed.get('error')}")
    else:
        lines.append("No failed runs.")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- CLIP score represents prompt-image semantic similarity and is not the same as absolute image quality.",
            "- Debug report and prompt preview should be checked together when diagnosing a run.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_html_report(benchmark_path: Path, benchmark: dict) -> str:
    summary = summarize(benchmark)
    results = benchmark.get("results") or []
    rows = "\n".join(_html_row(result, result is summary["best_run"]) for result in results)
    best = summary["best_run"]
    best_html = (
        f"<p><strong>{html.escape(str(best.get('id')))}</strong> with best_score {_score(best):.3f}</p>"
        if best
        else "<p>No successful run found.</p>"
    )
    failed = [result for result in results if not result.get("success")]
    failed_html = (
        "<ul>"
        + "".join(
            f"<li>{html.escape(str(item.get('id')))}: {html.escape(str(item.get('error')))}</li>"
            for item in failed
        )
        + "</ul>"
        if failed
        else "<p>No failed runs.</p>"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Benchmark Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
    .cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0; }}
    .card {{ border: 1px solid #ccc; padding: 12px; border-radius: 6px; min-width: 140px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f3f3f3; }}
    tr.best {{ background: #fff8d9; }}
    code {{ background: #f5f5f5; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>Benchmark Report</h1>
  <p>Source benchmark: <code>{html.escape(str(benchmark_path))}</code></p>
  <h2>Summary</h2>
  <div class="cards">
    <div class="card"><strong>Total</strong><br>{summary['total']}</div>
    <div class="card"><strong>Successful</strong><br>{summary['successful']}</div>
    <div class="card"><strong>Failed</strong><br>{summary['failed']}</div>
    <div class="card"><strong>Average best_score</strong><br>{summary['average_best_score']:.3f}</div>
    <div class="card"><strong>Retry rate</strong><br>{summary['retry_rate']:.2%}</div>
  </div>
  <h2>Results</h2>
  <table>
    <thead>
      <tr>
        <th>id</th><th>user_prompt</th><th>provider</th><th>success</th>
        <th>best_score</th><th>retry_needed</th><th>image_path</th>
        <th>debug_report_path</th><th>prompt_preview_path</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  <h2>Best Run</h2>
  {best_html}
  <h2>Failed Runs</h2>
  {failed_html}
  <h2>Notes</h2>
  <ul>
    <li>CLIP score represents prompt-image semantic similarity and is not the same as absolute image quality.</li>
    <li>Debug report and prompt preview should be checked together when diagnosing a run.</li>
  </ul>
</body>
</html>
"""


def summarize(benchmark: dict) -> dict:
    results = benchmark.get("results") or []
    total = len(results)
    successful = [result for result in results if result.get("success")]
    failed = total - len(successful)
    retry_count = sum(1 for result in results if result.get("retry_needed"))
    average_best_score = (
        sum(_score(result) for result in successful) / len(successful)
        if successful
        else 0.0
    )
    best_run = max(successful, key=_score, default=None)
    worst_run = min(successful, key=_score, default=None)
    return {
        "total": total,
        "successful": len(successful),
        "failed": failed,
        "average_best_score": average_best_score,
        "retry_rate": retry_count / total if total else 0.0,
        "best_run": best_run,
        "worst_run": worst_run,
        "best_run_id": best_run.get("id") if best_run else "N/A",
        "worst_run_id": worst_run.get("id") if worst_run else "N/A",
    }


def _run_summary(result: dict) -> list[str]:
    return [
        f"- id: `{result.get('id')}`",
        f"- user_prompt: {result.get('user_prompt')}",
        f"- provider: {result.get('provider')}",
        f"- best_score: {_score(result):.3f}",
        f"- retry_needed: {result.get('retry_needed')}",
        f"- debug_report_path: `{result.get('debug_report_path')}`",
        f"- prompt_preview_path: `{result.get('prompt_preview_path')}`",
    ]


def _html_row(result: dict, is_best: bool) -> str:
    css_class = ' class="best"' if is_best else ""
    return (
        f"<tr{css_class}>"
        f"<td>{html.escape(str(result.get('id')))}</td>"
        f"<td>{html.escape(str(result.get('user_prompt')))}</td>"
        f"<td>{html.escape(str(result.get('provider')))}</td>"
        f"<td>{html.escape(str(result.get('success')))}</td>"
        f"<td>{_score(result):.3f}</td>"
        f"<td>{html.escape(str(result.get('retry_needed')))}</td>"
        f"<td>{html.escape(str(result.get('image_path') or ''))}</td>"
        f"<td>{html.escape(str(result.get('debug_report_path') or ''))}</td>"
        f"<td>{html.escape(str(result.get('prompt_preview_path') or ''))}</td>"
        "</tr>"
    )


def _score(result: dict) -> float:
    value = result.get("best_score")
    if value is None:
        value = result.get("score", 0)
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _md(value) -> str:
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\n", " ")


def main():
    generate_reports()


if __name__ == "__main__":
    main()
