from __future__ import annotations

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from framework.reporting.models import ExecutionSummary


class PdfReportGenerator:
    def __init__(self, output_dir: str | Path = "reports/pdf") -> None:
        self.root_path = Path(__file__).resolve().parents[2]
        self.output_dir = self.root_path / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, summary: ExecutionSummary) -> Path:
        output_path = self.output_dir / f"execution_report_{summary.execution_id}.pdf"
        doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleBlue", parent=styles["Title"], textColor=colors.HexColor("#1F4E78"), fontSize=20)
        subtitle_style = ParagraphStyle("Subtitle", parent=styles["Heading2"], textColor=colors.HexColor("#404040"))
        normal = styles["BodyText"]
        story = []
        story.append(Paragraph("AutoTest Pro Framework", title_style))
        story.append(Paragraph("Reporte Ejecutivo de Ejecución", subtitle_style))
        story.append(Spacer(1, 0.25 * inch))
        for line in [
            f"Execution ID: {summary.execution_id}", f"Estado general: {summary.status}",
            f"Proyecto: {summary.project_name}", f"Suite: {summary.suite_name}", f"Caso: {summary.test_name}",
        ]:
            story.append(Paragraph(line, normal))
        story.append(Spacer(1, 0.3 * inch))
        metrics_data = [
            ["Métrica", "Valor"], ["Ambiente", summary.environment], ["Navegador", summary.browser],
            ["Inicio", summary.started_at], ["Fin", summary.finished_at], ["Duración", f"{summary.duration_seconds} segundos"],
            ["Total pasos", str(summary.total_steps)], ["Exitosos", str(summary.passed_steps)],
            ["Fallidos", str(summary.failed_steps)], ["Omitidos", str(summary.skipped_steps)],
            ["Porcentaje éxito", f"{summary.success_percentage}%"],
        ]
        story.append(self._table(metrics_data, widths=[2.2 * inch, 4.5 * inch]))
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph("Recomendaciones", subtitle_style))
        for rec in summary.recommendations:
            story.append(Paragraph(f"- {rec}", normal))
        story.append(PageBreak())
        story.append(Paragraph("Detalle de pasos ejecutados", subtitle_style))
        step_rows = [["#", "Acción", "Selector", "Estado", "Duración"]]
        for step in summary.steps:
            selector = step.selector if len(step.selector) < 38 else step.selector[:35] + "..."
            step_rows.append([str(step.order), step.action, selector, step.status, f"{step.duration_seconds}s"])
        story.append(self._table(step_rows, widths=[0.35 * inch, 1.3 * inch, 2.8 * inch, 1.0 * inch, 0.9 * inch]))
        failed = [s for s in summary.steps if s.status == "FAILED"]
        if failed:
            story.append(PageBreak())
            story.append(Paragraph("Errores encontrados", subtitle_style))
            for step in failed:
                story.append(Paragraph(f"Paso {step.order}: {step.name}", styles["Heading3"]))
                story.append(Paragraph(f"Error: {step.error_detail}", normal))
                if step.screenshot_path:
                    story.append(Paragraph(f"Evidencia: {step.screenshot_path}", normal))
                story.append(Spacer(1, 0.15 * inch))
        doc.build(story)
        return output_path

    def _table(self, data, widths):
        table = Table(data, colWidths=widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BFBFBF")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FA")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return table
