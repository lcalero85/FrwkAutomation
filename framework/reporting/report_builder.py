from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from framework.reporting.models import ExecutionSummary
from framework.reporting.html_report import HtmlReportGenerator
from framework.reporting.excel_report import ExcelReportGenerator
from framework.reporting.pdf_report import PdfReportGenerator


@dataclass
class GeneratedReports:
    html: str = ""
    excel: str = ""
    pdf: str = ""


class ReportBuilder:
    def generate(self, summary: ExecutionSummary, formats: Iterable[str] | None = None) -> GeneratedReports:
        selected = {fmt.strip().lower() for fmt in (formats or ["html"])}
        reports = GeneratedReports()
        if "html" in selected:
            reports.html = str(HtmlReportGenerator().generate(summary))
        if "excel" in selected or "xlsx" in selected:
            reports.excel = str(ExcelReportGenerator().generate(summary))
        if "pdf" in selected:
            reports.pdf = str(PdfReportGenerator().generate(summary))
        summary.report_paths = {k: v for k, v in reports.__dict__.items() if v}
        return reports
