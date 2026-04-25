from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from framework.reporting.models import ExecutionSummary


class HtmlReportGenerator:
    def __init__(self, output_dir: str | Path = "reports/html") -> None:
        self.root_path = Path(__file__).resolve().parents[2]
        self.output_dir = self.root_path / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir = Path(__file__).resolve().parent / "templates"

    def generate(self, summary: ExecutionSummary) -> Path:
        env = Environment(loader=FileSystemLoader(self.templates_dir), autoescape=select_autoescape(["html", "xml"]))
        template = env.get_template("execution_report.html")
        output_path = self.output_dir / f"execution_report_{summary.execution_id}.html"
        output_path.write_text(template.render(summary=summary), encoding="utf-8")
        return output_path
