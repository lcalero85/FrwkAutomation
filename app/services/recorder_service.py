from __future__ import annotations

from textwrap import indent

from sqlalchemy.orm import Session, selectinload

from app.database.models import RecordedCase, RecordedStep
from app.schemas.recorder_schema import (
    RecordedCaseCreate,
    RecordedCaseUpdate,
    RecordedStepCreate,
    RecordedStepUpdate,
    SelectorSuggestionRequest,
    SelectorSuggestionOut,
    BrowserRecordedEventIn,
)


class RecorderService:
    def __init__(self, db: Session):
        self.db = db

    def list_cases(self) -> list[RecordedCase]:
        return (
            self.db.query(RecordedCase)
            .options(selectinload(RecordedCase.steps))
            .order_by(RecordedCase.created_at.desc())
            .all()
        )

    def get_case(self, case_id: int) -> RecordedCase | None:
        return (
            self.db.query(RecordedCase)
            .options(selectinload(RecordedCase.steps))
            .filter(RecordedCase.id == case_id)
            .first()
        )

    def create_case(self, data: RecordedCaseCreate) -> RecordedCase:
        case = RecordedCase(**data.model_dump())
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return self.get_case(case.id) or case

    def update_case(self, case_id: int, data: RecordedCaseUpdate) -> RecordedCase | None:
        case = self.get_case(case_id)
        if not case:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(case, key, value)
        self.db.commit()
        self.db.refresh(case)
        return self.get_case(case.id)

    def delete_case(self, case_id: int) -> bool:
        case = self.get_case(case_id)
        if not case:
            return False
        self.db.delete(case)
        self.db.commit()
        return True

    def add_step(self, case_id: int, data: RecordedStepCreate) -> RecordedStep | None:
        case = self.get_case(case_id)
        if not case:
            return None
        step = RecordedStep(recorded_case_id=case_id, **data.model_dump())
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step

    def update_step(self, step_id: int, data: RecordedStepUpdate) -> RecordedStep | None:
        step = self.db.query(RecordedStep).filter(RecordedStep.id == step_id).first()
        if not step:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(step, key, value)
        self.db.commit()
        self.db.refresh(step)
        return step

    def delete_step(self, step_id: int) -> bool:
        step = self.db.query(RecordedStep).filter(RecordedStep.id == step_id).first()
        if not step:
            return False
        self.db.delete(step)
        self.db.commit()
        return True

    def reorder_steps(self, case_id: int) -> RecordedCase | None:
        case = self.get_case(case_id)
        if not case:
            return None
        for idx, step in enumerate(sorted(case.steps, key=lambda s: s.step_order), start=1):
            step.step_order = idx
        self.db.commit()
        return self.get_case(case_id)

    def suggest_selectors(self, data: SelectorSuggestionRequest) -> list[SelectorSuggestionOut]:
        suggestions: list[SelectorSuggestionOut] = []
        if data.element_id:
            suggestions.append(SelectorSuggestionOut(selector_type="css", selector_value=f"#{data.element_id}", priority=1, reason="ID del elemento"))
        if data.name:
            suggestions.append(SelectorSuggestionOut(selector_type="css", selector_value=f"[name='{data.name}']", priority=2, reason="Atributo name"))
        if data.data_testid:
            suggestions.append(SelectorSuggestionOut(selector_type="css", selector_value=f"[data-testid='{data.data_testid}']", priority=3, reason="Atributo data-testid"))
        if data.aria_label:
            suggestions.append(SelectorSuggestionOut(selector_type="css", selector_value=f"[aria-label='{data.aria_label}']", priority=4, reason="Atributo aria-label"))
        if data.css:
            suggestions.append(SelectorSuggestionOut(selector_type="css", selector_value=data.css, priority=5, reason="Selector CSS proporcionado"))
        if data.xpath:
            suggestions.append(SelectorSuggestionOut(selector_type="xpath", selector_value=data.xpath, priority=6, reason="XPath proporcionado"))
        if data.tag and data.text:
            xpath_text = data.text.replace("'", "")
            suggestions.append(SelectorSuggestionOut(selector_type="xpath", selector_value=f"//{data.tag}[contains(normalize-space(), '{xpath_text}')]", priority=7, reason="XPath relativo basado en texto"))
        return sorted(suggestions, key=lambda item: item.priority)



    def add_browser_event(self, case_id: int, data: BrowserRecordedEventIn) -> RecordedStep | None:
        """Convert a browser-extension event into a reusable recorded step."""
        case = self.get_case(case_id)
        if not case:
            return None

        action_type = self._normalize_browser_event_action(data)
        selector_type = data.selector_type or "css"
        selector_value = data.selector_value
        input_value = data.input_value

        if action_type == "open":
            selector_type = None
            selector_value = None
            input_value = data.url or data.input_value

        if input_value == "__AUTOTEST_MASKED_PASSWORD__":
            input_value = "***MASKED***"

        current_steps = sorted(case.steps or [], key=lambda step: step.step_order)
        last_step = current_steps[-1] if current_steps else None

        if last_step and self._is_duplicate_browser_step(last_step, action_type, selector_value, input_value, data.url):
            last_step.notes = self._build_browser_event_notes(data, deduplicated=True)
            self.db.commit()
            self.db.refresh(last_step)
            return last_step

        step = RecordedStep(
            recorded_case_id=case_id,
            step_order=len(current_steps) + 1,
            action_type=action_type,
            selector_type=selector_type,
            selector_value=selector_value,
            alternative_selector=data.alternative_selector,
            input_value=input_value,
            expected_result=data.expected_result,
            url=data.url,
            notes=self._build_browser_event_notes(data),
        )
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step

    def _normalize_browser_event_action(self, data: BrowserRecordedEventIn) -> str:
        event_type = (data.event_type or "").lower().strip()
        action_type = (data.action_type or "").lower().strip()
        if action_type:
            return action_type
        if event_type in {"navigation", "page_load", "url_change"}:
            return "open"
        if event_type in {"dblclick", "double_click"}:
            return "double_click"
        if event_type in {"contextmenu", "right_click"}:
            return "right_click"
        if event_type in {"input", "change", "select"}:
            return "type"
        if event_type == "scroll":
            return "scroll"
        return "click" if event_type == "click" else event_type

    def _is_duplicate_browser_step(self, last_step: RecordedStep, action_type: str, selector_value: str | None, input_value: str | None, url: str | None) -> bool:
        if last_step.action_type != action_type:
            return False
        if action_type == "open":
            return bool(url and last_step.url == url)
        if action_type == "type":
            return last_step.selector_value == selector_value
        return last_step.selector_value == selector_value and last_step.input_value == input_value

    def _build_browser_event_notes(self, data: BrowserRecordedEventIn, deduplicated: bool = False) -> str:
        parts = ["Captured by AutoTest browser recorder"]
        if deduplicated:
            parts.append("deduplicated")
        if data.title:
            parts.append(f"title={data.title}")
        if data.tag:
            parts.append(f"tag={data.tag}")
        if data.text:
            clean_text = data.text.strip().replace("\n", " ")[:120]
            if clean_text:
                parts.append(f"text={clean_text}")
        if data.timestamp:
            parts.append(f"timestamp={data.timestamp}")
        if data.notes:
            parts.append(data.notes)
        return " | ".join(parts)


    def get_browser_recorder_status(self, case_id: int) -> dict | None:
        """Return a small, friendly status summary for the automatic recorder UI."""
        case = self.get_case(case_id)
        if not case:
            return None
        steps = sorted(case.steps or [], key=lambda step: step.step_order)
        last_step = steps[-1] if steps else None
        last_summary = None
        last_event_type = None
        last_event_at = None
        if last_step:
            last_event_type = last_step.action_type
            last_event_at = last_step.created_at
            selector = last_step.selector_value or last_step.url or last_step.input_value or "sin selector"
            last_summary = f"{last_step.step_order}. {last_step.action_type} -> {selector}"
        return {
            "recorded_case_id": case_id,
            "total_steps": len(steps),
            "last_event_type": last_event_type,
            "last_event_at": last_event_at,
            "last_step_summary": last_summary,
            "message": "Grabador conectado. Ya puedes interactuar con el sitio bajo prueba." if steps else "Aún no hay pasos capturados para este caso.",
        }

    def clear_steps(self, case_id: int) -> dict | None:
        """Remove all steps from a recorded case."""
        case = self.get_case(case_id)
        if not case:
            return None
        before = len(case.steps or [])
        for step in list(case.steps or []):
            self.db.delete(step)
        self.db.commit()
        return {
            "recorded_case_id": case_id,
            "before_steps": before,
            "after_steps": 0,
            "removed_steps": before,
            "message": "Todos los pasos del caso fueron eliminados.",
        }

    def cleanup_steps(self, case_id: int) -> dict | None:
        """Clean noisy browser-recorder steps and renumber the case steps.

        Rules:
        - Remove extension connection-test wait events.
        - Remove empty click/type events without selector.
        - Collapse consecutive open events with the same URL.
        - Collapse consecutive type events for the same selector, keeping the latest value.
        - Collapse consecutive clicks on the same selector.
        """
        case = self.get_case(case_id)
        if not case:
            return None

        original_steps = sorted(case.steps or [], key=lambda step: (step.step_order, step.id))
        before = len(original_steps)
        cleaned = []

        for step in original_steps:
            action = (step.action_type or "").lower().strip()
            notes = (step.notes or "").lower()
            selector = step.selector_value or ""
            value = step.input_value or ""
            url = step.url or value

            if action == "wait" and "extension connection test" in notes:
                self.db.delete(step)
                continue
            if action in {"click", "type", "double_click", "right_click"} and not selector:
                self.db.delete(step)
                continue

            previous = cleaned[-1] if cleaned else None
            if previous:
                prev_action = (previous.action_type or "").lower().strip()
                prev_selector = previous.selector_value or ""
                prev_value = previous.input_value or ""
                prev_url = previous.url or prev_value

                if action == "open" and prev_action == "open" and url and url == prev_url:
                    self.db.delete(step)
                    continue
                if action == "type" and prev_action == "type" and selector and selector == prev_selector:
                    previous.input_value = value
                    previous.url = step.url or previous.url
                    previous.notes = step.notes or previous.notes
                    self.db.delete(step)
                    continue
                if action in {"click", "double_click", "right_click"} and action == prev_action and selector and selector == prev_selector:
                    self.db.delete(step)
                    continue

            cleaned.append(step)

        for index, step in enumerate(cleaned, start=1):
            step.step_order = index

        self.db.commit()
        after = len(cleaned)
        return {
            "recorded_case_id": case_id,
            "before_steps": before,
            "after_steps": after,
            "removed_steps": before - after,
            "message": "Limpieza completada. Se eliminaron eventos duplicados o ruido del grabador.",
        }

    def generate_python_code(self, case_id: int) -> str | None:
        case = self.get_case(case_id)
        if not case:
            return None
        body_lines = []
        if case.base_url:
            body_lines.append(f"self.open('{case.base_url}')")
        for step in sorted(case.steps, key=lambda s: s.step_order):
            selector = step.selector_value or ""
            value = step.input_value or ""
            action = step.action_type.lower()
            if action in {"open", "navigate", "go_to"}:
                target = step.url or step.input_value or case.base_url or "https://example.com"
                body_lines.append(f"self.open('{target}')")
            elif action in {"click", "double_click", "right_click"}:
                method = "click" if action == "click" else action
                body_lines.append(f"self.{method}('{selector}')")
            elif action in {"type", "write", "input", "send_keys"}:
                body_lines.append(f"self.type('{selector}', '{value}')")
            elif action in {"assert_visible", "visible"}:
                body_lines.append(f"self.assert_visible('{selector}')")
            elif action in {"assert_text", "text_contains"}:
                body_lines.append(f"self.assert_text_contains('{selector}', '{value}')")
            elif action == "wait":
                body_lines.append("# wait: implementar espera personalizada si aplica")
            elif action == "scroll":
                body_lines.append(f"self.scroll_to('{selector}')")
            else:
                body_lines.append(f"# Paso no implementado automáticamente: {step.action_type} -> {selector}")
        if not body_lines:
            body_lines.append("pass")
        class_name = "Recorded" + "".join(part.capitalize() for part in case.name.replace('-', ' ').replace('_', ' ').split()) + "Page"
        method_body = indent("\n".join(body_lines), "        ")
        return f"""from framework.core.base_page import BasePage\n\n\nclass {class_name}(BasePage):\n    def run_recorded_case(self):\n{method_body}\n"""
