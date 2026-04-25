from __future__ import annotations

import re
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from textwrap import indent

from sqlalchemy.orm import Session

from app.database.models import RecordedCase, RecordedStep
from app.services.recorder_service import RecorderService


@dataclass
class GeneratedExport:
    recorded_case_id: int
    case_name: str
    page_object_filename: str
    test_filename: str
    readme_filename: str
    page_object_code: str
    test_code: str
    readme: str


class CodeExportService:
    """Generate professional Python files from a recorded case.

    The generated files are intentionally independent from the web UI. They can
    be copied into a repository and versioned like any other automated test.
    """

    def __init__(self, db: Session):
        self.db = db
        self.project_root = Path(__file__).resolve().parents[2]
        self.export_root = self.project_root / "generated_tests" / "recorded_cases"

    def preview_export(self, case_id: int) -> GeneratedExport | None:
        case = RecorderService(self.db).get_case(case_id)
        if not case:
            return None
        safe_name = self._safe_name(case.name)
        class_name = self._class_name(case.name)
        return GeneratedExport(
            recorded_case_id=case.id,
            case_name=case.name,
            page_object_filename=f"pages/{safe_name}_page.py",
            test_filename=f"tests/test_{safe_name}.py",
            readme_filename="README_EXPORT.md",
            page_object_code=self._build_page_object(case, safe_name, class_name),
            test_code=self._build_test_file(case, safe_name, class_name),
            readme=self._build_readme(case, safe_name),
        )

    def create_export_zip(self, case_id: int) -> dict | None:
        generated = self.preview_export(case_id)
        if not generated:
            return None

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = self._safe_name(generated.case_name)
        target_dir = self.export_root / f"{safe_name}_{timestamp}"
        pages_dir = target_dir / "pages"
        tests_dir = target_dir / "tests"
        pages_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)

        files_to_write = {
            target_dir / generated.readme_filename: generated.readme,
            target_dir / "pages" / f"{safe_name}_page.py": generated.page_object_code,
            target_dir / "tests" / f"test_{safe_name}.py": generated.test_code,
            target_dir / "pages" / "__init__.py": "",
            target_dir / "tests" / "__init__.py": "",
        }
        for file_path, content in files_to_write.items():
            file_path.write_text(content, encoding="utf-8")

        zip_path = shutil.make_archive(str(target_dir), "zip", root_dir=target_dir)
        files = [str(path.relative_to(target_dir)).replace("\\", "/") for path in target_dir.rglob("*") if path.is_file()]
        return {
            "recorded_case_id": generated.recorded_case_id,
            "case_name": generated.case_name,
            "export_folder": str(target_dir),
            "zip_path": zip_path,
            "zip_filename": Path(zip_path).name,
            "files": files,
            "created_at": datetime.utcnow(),
            "message": "Exportación generada correctamente. Puedes descargar el ZIP y versionarlo en tu repositorio.",
        }

    def latest_zip_for_case(self, case_id: int) -> Path | None:
        case = RecorderService(self.db).get_case(case_id)
        if not case:
            return None
        safe_name = self._safe_name(case.name)
        candidates = sorted(self.export_root.glob(f"{safe_name}_*.zip"), key=lambda path: path.stat().st_mtime, reverse=True)
        return candidates[0] if candidates else None

    def _build_page_object(self, case: RecordedCase, safe_name: str, class_name: str) -> str:
        steps = sorted(case.steps or [], key=lambda step: step.step_order)
        constants: list[str] = []
        body_lines: list[str] = []
        selector_counter = 1

        for step in steps:
            action = (step.action_type or "").lower().strip()
            selector = self._normalize_selector(step.selector_value)
            value = self._py_string(step.input_value or "")
            url = self._py_string(step.url or step.input_value or case.base_url or "")
            expected = self._py_string(step.expected_result or step.input_value or "")

            if action in {"open", "navigate", "go_to"}:
                if step.url or step.input_value:
                    body_lines.append(f"self.open({url})")
                else:
                    body_lines.append("self.open_base()")
                continue

            constant_name = None
            if selector:
                constant_name = self._selector_constant_name(step, selector_counter)
                selector_counter += 1
                constants.append(f"    {constant_name} = {self._py_string(selector)}")

            if action == "click":
                body_lines.append(f"self.click(self.{constant_name})" if constant_name else "# click omitido: selector vacío")
            elif action == "double_click":
                body_lines.append(f"self.double_click(self.{constant_name})" if constant_name else "# double_click omitido: selector vacío")
            elif action == "right_click":
                body_lines.append(f"self.right_click(self.{constant_name})" if constant_name else "# right_click omitido: selector vacío")
            elif action in {"type", "write", "input", "send_keys"}:
                body_lines.append(f"self.type(self.{constant_name}, {value})" if constant_name else "# type omitido: selector vacío")
            elif action in {"assert_visible", "visible"}:
                body_lines.append(f"self.assert_visible(self.{constant_name})" if constant_name else "# assert_visible omitido: selector vacío")
            elif action in {"assert_text", "text_contains"}:
                body_lines.append(f"self.assert_text_contains(self.{constant_name}, {expected})" if constant_name else "# assert_text omitido: selector vacío")
            elif action in {"assert_url", "url_contains"}:
                body_lines.append(f"self.assert_url_contains({expected})")
            elif action == "scroll":
                body_lines.append(f"self.scroll_to(self.{constant_name})" if constant_name else "self.execute_js('window.scrollTo(0, document.body.scrollHeight);')")
            elif action == "hover":
                body_lines.append(f"self.hover(self.{constant_name})" if constant_name else "# hover omitido: selector vacío")
            elif action == "select":
                body_lines.append(f"self.select_by_visible_text(self.{constant_name}, {value})" if constant_name else "# select omitido: selector vacío")
            elif action == "upload":
                body_lines.append(f"self.upload_file(self.{constant_name}, {value})" if constant_name else "# upload omitido: selector vacío")
            elif action == "wait":
                body_lines.append("# Espera grabada: agrega una espera explícita si el flujo lo requiere")
            else:
                body_lines.append(f"# Acción no mapeada automáticamente: {action}")

        if not body_lines:
            body_lines.append("pass")

        constants_block = "\n".join(dict.fromkeys(constants)) or "    # Selectores generados desde el grabador"
        method_body = indent("\n".join(body_lines), "        ")
        return f'''from __future__ import annotations

from framework.core.base_page import BasePage


class {class_name}Page(BasePage):
    """Page Object generado desde el grabador de AutoTest Pro."""

{constants_block}

    def run_recorded_flow(self) -> None:
        """Ejecuta el flujo capturado para el caso: {case.name}."""
{method_body}
'''

    def _build_test_file(self, case: RecordedCase, safe_name: str, class_name: str) -> str:
        base_url = self._py_string(case.base_url or "")
        browser = self._py_string(case.browser or "chrome")
        return f'''from __future__ import annotations

from framework.core.driver_factory import DriverFactory
from pages.{safe_name}_page import {class_name}Page


def test_{safe_name}_recorded_flow():
    driver = DriverFactory().create_driver(browser={browser}, headless=False)
    try:
        page = {class_name}Page(driver, base_url={base_url})
        page.run_recorded_flow()
    finally:
        driver.quit()
'''

    def _build_readme(self, case: RecordedCase, safe_name: str) -> str:
        return f'''# Exportación de caso grabado

Caso: `{case.name}`  
ID: `{case.id}`  
Navegador sugerido: `{case.browser}`  
URL base: `{case.base_url or 'No definida'}`

## Archivos generados

- `pages/{safe_name}_page.py`: Page Object generado desde los pasos grabados.
- `tests/test_{safe_name}.py`: Prueba Pytest lista para ejecutar.

## Uso sugerido

Copia la carpeta exportada dentro de tu proyecto o repositorio de automatización.
Luego ajusta imports si decides mover los archivos a otra ruta.

## Ejecución

```bash
pytest tests/test_{safe_name}.py -v
```

## Recomendación

Revisa los selectores generados antes de versionar el test. Prioriza `id`, `name`, `data-testid` o selectores CSS estables.
'''

    def _safe_name(self, value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^a-zA-Z0-9_]+", "_", value)
        value = re.sub(r"_+", "_", value).strip("_")
        return value or "recorded_case"

    def _class_name(self, value: str) -> str:
        safe = self._safe_name(value)
        return "".join(part.capitalize() for part in safe.split("_")) or "RecordedCase"

    def _selector_constant_name(self, step: RecordedStep, index: int) -> str:
        action = re.sub(r"[^A-Z0-9]+", "_", (step.action_type or "STEP").upper()).strip("_")
        return f"{action}_SELECTOR_{index}"

    def _normalize_selector(self, selector: str | None) -> str:
        return (selector or "").strip()

    def _py_string(self, value: str) -> str:
        return repr(value or "")
