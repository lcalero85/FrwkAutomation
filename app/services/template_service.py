from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import Environment, Project, RecordedCase, RecordedStep, Template, TestSuite
from app.schemas.template_schema import TemplateApplyRequest, TemplateCreate, TemplateUpdate


def _template_to_dict(template: Template) -> dict[str, Any]:
    return {
        "id": template.id,
        "name": template.name,
        "template_type": template.template_type,
        "category": template.category,
        "description": template.description,
        "priority": template.priority,
        "tags": template.tags,
        "payload": json.loads(template.payload_json or "{}"),
        "is_system": template.is_system,
    }


class TemplateService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_templates(self, template_type: str | None = None, category: str | None = None) -> list[dict[str, Any]]:
        query = self.db.query(Template)
        if template_type:
            query = query.filter(Template.template_type == template_type.upper())
        if category:
            query = query.filter(Template.category == category)
        return [_template_to_dict(item) for item in query.order_by(Template.template_type, Template.category, Template.name).all()]

    def get_template(self, template_id: int) -> dict[str, Any] | None:
        item = self.db.query(Template).filter(Template.id == template_id).first()
        return _template_to_dict(item) if item else None

    def create_template(self, data: TemplateCreate) -> dict[str, Any]:
        template = Template(
            name=data.name,
            template_type=data.template_type.upper(),
            category=data.category,
            description=data.description,
            priority=data.priority.upper(),
            tags=data.tags,
            payload_json=json.dumps(data.payload, ensure_ascii=False, indent=2),
            is_system=data.is_system,
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return _template_to_dict(template)

    def update_template(self, template_id: int, data: TemplateUpdate) -> dict[str, Any] | None:
        template = self.db.query(Template).filter(Template.id == template_id).first()
        if not template:
            return None
        values = data.model_dump(exclude_unset=True)
        for key, value in values.items():
            if key == "payload" and value is not None:
                template.payload_json = json.dumps(value, ensure_ascii=False, indent=2)
            elif key == "template_type" and value is not None:
                template.template_type = str(value).upper()
            elif key == "priority" and value is not None:
                template.priority = str(value).upper()
            else:
                setattr(template, key, value)
        self.db.commit()
        self.db.refresh(template)
        return _template_to_dict(template)

    def delete_template(self, template_id: int) -> bool:
        template = self.db.query(Template).filter(Template.id == template_id).first()
        if not template:
            return False
        if template.is_system:
            raise ValueError("Las plantillas del sistema no pueden eliminarse.")
        self.db.delete(template)
        self.db.commit()
        return True

    def apply_template(self, template_id: int, data: TemplateApplyRequest) -> dict[str, Any] | None:
        template = self.db.query(Template).filter(Template.id == template_id).first()
        if not template:
            return None
        payload = json.loads(template.payload_json or "{}")
        created: list[str] = []
        project_id = data.project_id
        suite_id = None
        recorded_case_id = None

        if template.template_type == "PROJECT":
            project = self._create_project_from_payload(payload, data)
            created.append(f"Proyecto: {project.name}")
            project_id = project.id
            for suite_payload in payload.get("suites", []):
                suite = self._create_suite(project.id, suite_payload)
                created.append(f"Suite: {suite.name}")
                for case_payload in suite_payload.get("cases", []):
                    recorded_case = self._create_recorded_case(project.id, suite.id, case_payload, data.base_url or project.base_url)
                    created.append(f"Caso grabado: {recorded_case.name}")
                    recorded_case_id = recorded_case.id

        elif template.template_type == "SUITE":
            project = self._resolve_or_create_project(data, payload)
            project_id = project.id
            suite = self._create_suite(project.id, payload)
            suite_id = suite.id
            created.append(f"Suite: {suite.name}")
            for case_payload in payload.get("cases", []):
                recorded_case = self._create_recorded_case(project.id, suite.id, case_payload, data.base_url or project.base_url)
                created.append(f"Caso grabado: {recorded_case.name}")
                recorded_case_id = recorded_case.id

        else:
            project = self._resolve_or_create_project(data, payload)
            project_id = project.id
            suite = self._resolve_or_create_suite(project.id, data, payload)
            suite_id = suite.id
            recorded_case = self._create_recorded_case(project.id, suite.id, payload, data.base_url or project.base_url)
            recorded_case_id = recorded_case.id
            created.append(f"Caso grabado: {recorded_case.name}")

        self.db.commit()
        return {
            "message": "Plantilla aplicada correctamente.",
            "project_id": project_id,
            "suite_id": suite_id,
            "recorded_case_id": recorded_case_id,
            "created_items": created,
        }

    def _resolve_or_create_project(self, data: TemplateApplyRequest, payload: dict[str, Any]) -> Project:
        if data.project_id:
            project = self.db.query(Project).filter(Project.id == data.project_id).first()
            if project:
                return project
        name = data.project_name or payload.get("project_name") or "Proyecto desde plantilla"
        existing = self.db.query(Project).filter(Project.name == name).first()
        if existing:
            return existing
        return self._create_project_from_payload({"name": name, "description": payload.get("description")}, data)

    def _resolve_or_create_suite(self, project_id: int, data: TemplateApplyRequest, payload: dict[str, Any]) -> TestSuite:
        name = data.suite_name or payload.get("suite_name") or "Suite desde plantilla"
        suite = self.db.query(TestSuite).filter(TestSuite.project_id == project_id, TestSuite.name == name).first()
        if suite:
            return suite
        return self._create_suite(project_id, {"name": name, "description": "Suite creada desde plantilla", "priority": payload.get("priority", "MEDIUM")})

    def _create_project_from_payload(self, payload: dict[str, Any], data: TemplateApplyRequest) -> Project:
        env = self.db.query(Environment).filter(Environment.name == "demo").first()
        name = data.project_name or payload.get("name") or payload.get("project_name") or "Proyecto desde plantilla"
        project = Project(
            name=name,
            description=payload.get("description", "Proyecto creado desde plantilla profesional."),
            base_url=data.base_url or payload.get("base_url"),
            environment_id=env.id if env else None,
            default_browser=data.default_browser or payload.get("default_browser", "chrome"),
            status="ACTIVE",
        )
        self.db.add(project)
        self.db.flush()
        return project

    def _create_suite(self, project_id: int, payload: dict[str, Any]) -> TestSuite:
        suite = TestSuite(
            project_id=project_id,
            name=payload.get("name") or payload.get("suite_name") or "Suite desde plantilla",
            description=payload.get("description", "Suite creada desde plantilla."),
            priority=payload.get("priority", "MEDIUM"),
            status="ACTIVE",
        )
        self.db.add(suite)
        self.db.flush()
        return suite

    def _create_recorded_case(self, project_id: int, suite_id: int, payload: dict[str, Any], base_url: str | None = None) -> RecordedCase:
        case = RecordedCase(
            name=payload.get("name") or payload.get("case_name") or "Caso desde plantilla",
            description=payload.get("description", "Caso grabado creado desde plantilla."),
            project_id=project_id,
            suite_id=suite_id,
            base_url=base_url or payload.get("base_url"),
            browser=payload.get("browser", "chrome"),
            status="READY",
        )
        self.db.add(case)
        self.db.flush()
        for index, step in enumerate(payload.get("steps", []), start=1):
            self.db.add(RecordedStep(
                recorded_case_id=case.id,
                step_order=step.get("step_order", index),
                action_type=step.get("action_type", "click"),
                selector_type=step.get("selector_type"),
                selector_value=step.get("selector_value"),
                alternative_selector=step.get("alternative_selector"),
                input_value=step.get("input_value"),
                expected_result=step.get("expected_result"),
                url=step.get("url"),
                notes=step.get("notes"),
            ))
        return case


def seed_default_templates(db: Session) -> None:
    if db.query(Template).count() > 0:
        return

    templates: list[TemplateCreate] = [
        TemplateCreate(
            name="Proyecto QA Web Smoke + Regression",
            template_type="PROJECT",
            category="Web QA",
            description="Crea un proyecto con suites iniciales de Smoke y Regression y casos listos para completar.",
            priority="HIGH",
            tags="web,smoke,regression,selenium,page-object",
            is_system=True,
            payload={
                "name": "Proyecto Web desde Plantilla",
                "description": "Proyecto base para automatización web con Selenium.",
                "default_browser": "chrome",
                "suites": [
                    {
                        "name": "Smoke Suite",
                        "description": "Validaciones críticas de disponibilidad y acceso.",
                        "priority": "HIGH",
                        "cases": [
                            {
                                "name": "validar_login_exitoso",
                                "description": "Verifica acceso exitoso con credenciales válidas.",
                                "browser": "chrome",
                                "steps": [
                                    {"action_type": "open", "url": "{{BASE_URL}}", "expected_result": "Abrir pantalla inicial"},
                                    {"action_type": "type", "selector_type": "css", "selector_value": "#username", "input_value": "{{USER}}", "expected_result": "Usuario ingresado"},
                                    {"action_type": "type", "selector_type": "css", "selector_value": "#password", "input_value": "{{PASSWORD}}", "expected_result": "Contraseña ingresada"},
                                    {"action_type": "click", "selector_type": "css", "selector_value": "button[type=submit]", "expected_result": "Enviar formulario"},
                                    {"action_type": "assert_visible", "selector_type": "css", "selector_value": ".flash.success", "expected_result": "Mensaje de éxito visible"}
                                ],
                            }
                        ],
                    },
                    {
                        "name": "Regression Suite",
                        "description": "Pruebas funcionales principales del sistema.",
                        "priority": "MEDIUM",
                        "cases": []
                    },
                ],
            },
        ),
        TemplateCreate(
            name="Suite de Login y Seguridad",
            template_type="SUITE",
            category="Autenticación",
            description="Suite lista para cubrir login exitoso, credenciales inválidas y cierre de sesión.",
            priority="HIGH",
            tags="login,security,authentication",
            is_system=True,
            payload={
                "name": "Login y Seguridad",
                "description": "Suite para validar flujos de autenticación.",
                "priority": "HIGH",
                "cases": [
                    {
                        "name": "login_con_credenciales_validas",
                        "description": "Valida inicio de sesión exitoso.",
                        "steps": [
                            {"action_type": "open", "url": "{{BASE_URL}}"},
                            {"action_type": "type", "selector_type": "css", "selector_value": "#username", "input_value": "{{USER}}"},
                            {"action_type": "type", "selector_type": "css", "selector_value": "#password", "input_value": "{{PASSWORD}}"},
                            {"action_type": "click", "selector_type": "css", "selector_value": "button[type=submit]"},
                            {"action_type": "assert_visible", "selector_type": "css", "selector_value": ".flash.success"}
                        ],
                    },
                    {
                        "name": "login_con_credenciales_invalidas",
                        "description": "Valida mensaje de error con credenciales inválidas.",
                        "steps": [
                            {"action_type": "open", "url": "{{BASE_URL}}"},
                            {"action_type": "type", "selector_type": "css", "selector_value": "#username", "input_value": "invalid"},
                            {"action_type": "type", "selector_type": "css", "selector_value": "#password", "input_value": "invalid"},
                            {"action_type": "click", "selector_type": "css", "selector_value": "button[type=submit]"},
                            {"action_type": "assert_visible", "selector_type": "css", "selector_value": ".flash.error"}
                        ],
                    },
                ],
            },
        ),
        TemplateCreate(
            name="Caso CRUD básico",
            template_type="CASE",
            category="Funcional",
            description="Plantilla genérica para crear, validar, editar y eliminar un registro.",
            priority="MEDIUM",
            tags="crud,functional,forms",
            is_system=True,
            payload={
                "name": "crud_basico",
                "description": "Caso base para validar alta, consulta, edición y eliminación de un registro.",
                "suite_name": "CRUD Suite",
                "steps": [
                    {"action_type": "open", "url": "{{BASE_URL}}", "expected_result": "Abrir módulo"},
                    {"action_type": "click", "selector_type": "css", "selector_value": "{{NEW_BUTTON_SELECTOR}}", "expected_result": "Abrir formulario"},
                    {"action_type": "type", "selector_type": "css", "selector_value": "{{NAME_FIELD_SELECTOR}}", "input_value": "Registro QA", "expected_result": "Ingresar nombre"},
                    {"action_type": "click", "selector_type": "css", "selector_value": "{{SAVE_BUTTON_SELECTOR}}", "expected_result": "Guardar registro"},
                    {"action_type": "assert_visible", "selector_type": "css", "selector_value": "{{SUCCESS_MESSAGE_SELECTOR}}", "expected_result": "Confirmar guardado"}
                ],
            },
        ),
        TemplateCreate(
            name="Caso formulario con validaciones obligatorias",
            template_type="CASE",
            category="Validaciones",
            description="Plantilla para validar campos requeridos, mensajes y flujo negativo.",
            priority="HIGH",
            tags="negative,validation,forms",
            is_system=True,
            payload={
                "name": "validar_campos_obligatorios",
                "description": "Verifica que el formulario muestre validaciones cuando faltan datos requeridos.",
                "suite_name": "Validaciones de formularios",
                "steps": [
                    {"action_type": "open", "url": "{{BASE_URL}}"},
                    {"action_type": "click", "selector_type": "css", "selector_value": "{{SUBMIT_BUTTON_SELECTOR}}", "expected_result": "Intentar enviar sin datos"},
                    {"action_type": "assert_visible", "selector_type": "css", "selector_value": "{{VALIDATION_MESSAGE_SELECTOR}}", "expected_result": "Validación visible"}
                ],
            },
        ),
    ]

    service = TemplateService(db)
    for item in templates:
        service.create_template(item)
