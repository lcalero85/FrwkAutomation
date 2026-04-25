from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database.connection import Base, engine, SessionLocal, PROJECT_ROOT
from app.database.models import Environment, Permission, Project, Role, RolePermission, SchedulerJob, Setting, TestCase, TestSuite, User, RecordedCase, RecordedStep
from app.security.password_utils import hash_password
from app.services.settings_service import ensure_default_settings
from app.services.template_service import seed_default_templates

load_dotenv()


def create_storage_folder() -> None:
    Path(PROJECT_ROOT / "storage").mkdir(parents=True, exist_ok=True)


def create_tables() -> None:
    create_storage_folder()
    Base.metadata.create_all(bind=engine)


def seed_defaults(db: Session) -> None:
    admin_role = db.query(Role).filter(Role.name == "Administrador").first()
    if not admin_role:
        admin_role = Role(name="Administrador", description="Acceso completo a la plataforma")
        db.add(admin_role)
        db.flush()

    qa_lead_role = db.query(Role).filter(Role.name == "QA Lead").first()
    if not qa_lead_role:
        db.add(Role(name="QA Lead", description="Puede gestionar proyectos, suites, ejecuciones y reportes"))

    qa_role = db.query(Role).filter(Role.name == "QA Automation").first()
    if not qa_role:
        db.add(Role(name="QA Automation", description="Puede crear y ejecutar pruebas automatizadas"))

    viewer_role = db.query(Role).filter(Role.name == "Viewer").first()
    if not viewer_role:
        viewer_role = Role(name="Viewer", description="Acceso de solo lectura a resultados y reportes")
        db.add(viewer_role)
        db.flush()

    permission_seed = [
        ("dashboard.view", "Ver dashboard", "Dashboard"),
        ("projects.view", "Ver proyectos", "Proyectos"),
        ("projects.manage", "Gestionar proyectos", "Proyectos"),
        ("executions.view", "Ver ejecuciones", "Ejecuciones"),
        ("executions.run", "Ejecutar pruebas", "Ejecuciones"),
        ("reports.view", "Ver reportes", "Reportes"),
        ("reports.email", "Enviar reportes por correo", "Reportes"),
        ("reports.download", "Descargar reportes y evidencias", "Reportes"),
        ("recorder.manage", "Gestionar grabador", "Grabador"),
        ("scheduler.manage", "Gestionar scheduler", "Scheduler"),
        ("users.manage", "Administrar usuarios", "Usuarios"),
        ("security.audit", "Ver auditoría", "Seguridad"),
        ("settings.manage", "Gestionar configuración", "Configuración"),
        ("templates.view", "Ver plantillas", "Plantillas"),
        ("templates.manage", "Gestionar plantillas", "Plantillas"),
        ("templates.apply", "Aplicar plantillas", "Plantillas"),
    ]
    permission_by_code = {}
    for code, name, module in permission_seed:
        perm = db.query(Permission).filter(Permission.code == code).first()
        if not perm:
            perm = Permission(code=code, name=name, module=module, description=name)
            db.add(perm)
            db.flush()
        permission_by_code[code] = perm

    role_permission_map = {
        "Administrador": [code for code, _, _ in permission_seed],
        "QA Lead": [
            "dashboard.view", "projects.view", "projects.manage", "executions.view",
            "executions.run", "reports.view", "reports.email", "reports.download",
            "recorder.manage", "scheduler.manage", "templates.view", "templates.apply",
        ],
        "QA Automation": [
            "dashboard.view", "projects.view", "executions.view", "executions.run",
            "reports.view", "reports.email", "reports.download", "recorder.manage", "templates.view", "templates.apply",
        ],
        "Viewer": ["dashboard.view", "projects.view", "executions.view", "reports.view", "reports.download", "templates.view"],
    }
    roles_by_name = {role.name: role for role in db.query(Role).all()}
    for role_name, codes in role_permission_map.items():
        role = roles_by_name.get(role_name)
        if not role:
            continue
        for code in codes:
            perm = permission_by_code.get(code)
            if not perm:
                continue
            exists = db.query(RolePermission).filter(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm.id,
            ).first()
            if not exists:
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))

    username = os.getenv("DEFAULT_ADMIN_USER", "admin")
    email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@autotestpro.local")
    password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin12345")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.add(User(
            full_name="System Administrator",
            email=email,
            username=username,
            password_hash=hash_password(password),
            role_id=admin_role.id,
            is_active=True,
        ))

    demo_env = db.query(Environment).filter(Environment.name == "demo").first()
    if not demo_env:
        demo_env = Environment(
            name="demo",
            base_url="https://the-internet.herokuapp.com/login",
            description="Ambiente demo para validar el framework",
        )
        db.add(demo_env)
        db.flush()

    project = db.query(Project).filter(Project.name == "AutoTest Pro Demo").first()
    if not project:
        project = Project(
            name="AutoTest Pro Demo",
            description="Proyecto demo inicial creado por seed de base de datos",
            base_url=demo_env.base_url,
            environment_id=demo_env.id,
            default_browser="chrome",
            status="ACTIVE",
        )
        db.add(project)
        db.flush()

    suite = db.query(TestSuite).filter(TestSuite.name == "Demo Suite", TestSuite.project_id == project.id).first()
    if not suite:
        suite = TestSuite(
            project_id=project.id,
            name="Demo Suite",
            description="Suite demo para login básico",
            priority="HIGH",
            status="ACTIVE",
        )
        db.add(suite)
        db.flush()

    case = db.query(TestCase).filter(TestCase.name == "login_demo", TestCase.suite_id == suite.id).first()
    if not case:
        db.add(TestCase(
            suite_id=suite.id,
            name="login_demo",
            description="Valida login exitoso en sitio demo",
            priority="HIGH",
            test_type="SMOKE",
            preconditions="Sitio demo disponible",
            expected_result="El usuario accede al área segura",
            status="ACTIVE",
        ))


    recorded_case = db.query(RecordedCase).filter(RecordedCase.name == "login_recorded_demo").first()
    if not recorded_case:
        recorded_case = RecordedCase(
            name="login_recorded_demo",
            description="Caso grabado demo que se ejecuta como prueba real de Selenium.",
            project_id=project.id,
            suite_id=suite.id,
            base_url=demo_env.base_url,
            browser="chrome",
            status="READY",
        )
        db.add(recorded_case)
        db.flush()
        demo_steps = [
            (1, "open", "css", None, None, demo_env.base_url, "Abrir pantalla de login"),
            (2, "type", "css", "#username", "tomsmith", None, "Ingresar usuario válido"),
            (3, "type", "css", "#password", "SuperSecretPassword!", None, "Ingresar contraseña válida"),
            (4, "click", "css", "button[type=\"submit\"]", None, None, "Enviar formulario"),
            (5, "assert_visible", "css", ".flash.success", None, None, "Validar mensaje de acceso"),
            (6, "assert_text", "css", ".flash.success", "You logged into a secure area!", None, "Validar texto de acceso exitoso"),
        ]
        for order, action, selector_type, selector, value, url, expected in demo_steps:
            db.add(RecordedStep(
                recorded_case_id=recorded_case.id,
                step_order=order,
                action_type=action,
                selector_type=selector_type,
                selector_value=selector,
                input_value=value,
                url=url,
                expected_result=expected,
            ))

    ensure_default_settings(db)
    seed_default_templates(db)

    demo_job = db.query(SchedulerJob).filter(SchedulerJob.name == "Smoke demo diario").first()
    if not demo_job:
        db.add(SchedulerJob(
            name="Smoke demo diario",
            description="Job demo creado automáticamente para validar el scheduler.",
            execution_type="DEMO",
            browser="chrome",
            environment="demo",
            report="html,excel,pdf",
            headless=True,
            schedule_type="DAILY",
            next_run="Pendiente de cálculo",
            is_active=False,
        ))

    db.commit()


def init_database() -> None:
    create_tables()
    db = SessionLocal()
    try:
        seed_defaults(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")
