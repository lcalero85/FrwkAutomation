from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any
import uuid


@dataclass
class StepResult:
    order: int
    name: str
    action: str
    selector: str = ""
    status: str = "PASSED"
    message: str = ""
    screenshot_path: str = ""
    duration_seconds: float = 0.0
    error_detail: str = ""
    started_at: str = ""
    finished_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionSummary:
    execution_id: str
    project_name: str
    suite_name: str
    test_name: str
    browser: str
    environment: str
    base_url: str
    status: str
    started_at: str
    finished_at: str
    duration_seconds: float
    total_steps: int
    passed_steps: int
    failed_steps: int
    skipped_steps: int
    success_percentage: float
    recommendations: list[str] = field(default_factory=list)
    steps: list[StepResult] = field(default_factory=list)
    report_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["steps"] = [step.to_dict() for step in self.steps]
        return data


class ExecutionContext:
    """In-memory execution context used by actions, assertions and report builders."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.execution_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
        self.project_name = "AutoTest Pro Framework"
        self.suite_name = "Demo Suite"
        self.test_name = "login_demo"
        self.browser = "chrome"
        self.environment = "demo"
        self.base_url = ""
        self.status = "RUNNING"
        self.started_at = datetime.now()
        self.finished_at: datetime | None = None
        self._step_counter = 0
        self.steps: list[StepResult] = []

    def configure(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)

    def record_step(self, *, name: str, action: str, selector: str = "", status: str = "PASSED",
                    message: str = "", screenshot_path: str = "", duration_seconds: float = 0.0,
                    error_detail: str = "") -> StepResult:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._step_counter += 1
        step = StepResult(
            order=self._step_counter,
            name=name,
            action=action,
            selector=selector,
            status=status,
            message=message,
            screenshot_path=screenshot_path,
            duration_seconds=round(duration_seconds, 3),
            error_detail=error_detail,
            started_at=now,
            finished_at=now,
        )
        self.steps.append(step)
        return step

    def finalize(self, status: str) -> ExecutionSummary:
        self.status = status
        self.finished_at = datetime.now()
        duration = round((self.finished_at - self.started_at).total_seconds(), 2)
        total = len(self.steps)
        passed = len([s for s in self.steps if s.status == "PASSED"])
        failed = len([s for s in self.steps if s.status == "FAILED"])
        skipped = len([s for s in self.steps if s.status == "SKIPPED"])
        success = round((passed / total) * 100, 2) if total else (100.0 if status == "PASSED" else 0.0)
        recommendations = []
        if failed:
            recommendations.append("Revisar los pasos fallidos y validar los screenshots asociados.")
            recommendations.append("Verificar selectores, tiempos de espera y estabilidad del ambiente bajo prueba.")
        else:
            recommendations.append("La ejecución finalizó correctamente. Mantener este caso como prueba de humo base.")
            recommendations.append("Considerar agregar más validaciones funcionales y datos externos para ampliar cobertura.")
        return ExecutionSummary(
            execution_id=self.execution_id,
            project_name=self.project_name,
            suite_name=self.suite_name,
            test_name=self.test_name,
            browser=self.browser,
            environment=self.environment,
            base_url=self.base_url,
            status=status,
            started_at=self.started_at.strftime("%Y-%m-%d %H:%M:%S"),
            finished_at=self.finished_at.strftime("%Y-%m-%d %H:%M:%S"),
            duration_seconds=duration,
            total_steps=total,
            passed_steps=passed,
            failed_steps=failed,
            skipped_steps=skipped,
            success_percentage=success,
            recommendations=recommendations,
            steps=self.steps.copy(),
        )


execution_context = ExecutionContext()
