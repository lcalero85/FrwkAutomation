from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Execution, Project, RecordedCase, Report, TestCase, TestSuite, User
from app.security.auth_utils import require_permissions
from app.schemas.project_schema import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["projects.view"]))):
    return ProjectService(db).list_projects()


@router.get("/{project_id}/details")
def get_project_details(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["projects.view"]))):
    project = ProjectService(db).get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    suites = db.query(TestSuite).filter(TestSuite.project_id == project_id).order_by(TestSuite.id.desc()).all()
    suite_ids = [suite.id for suite in suites]
    test_cases = db.query(TestCase).filter(TestCase.suite_id.in_(suite_ids)).order_by(TestCase.id.desc()).all() if suite_ids else []
    recorded_cases = db.query(RecordedCase).filter(RecordedCase.project_id == project_id).order_by(RecordedCase.id.desc()).all()
    executions = db.query(Execution).filter(Execution.project_name == project.name).order_by(Execution.id.desc()).limit(10).all()
    reports = []
    if executions:
        execution_ids = [item.id for item in executions]
        reports = db.query(Report).filter(Report.execution_id.in_(execution_ids)).order_by(Report.id.desc()).limit(10).all()

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "base_url": project.base_url,
            "default_browser": project.default_browser,
            "status": project.status,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        },
        "summary": {
            "total_suites": len(suites),
            "total_test_cases": len(test_cases),
            "total_recorded_cases": len(recorded_cases),
            "total_executions": len(executions),
            "total_reports": len(reports),
        },
        "suites": [
            {"id": item.id, "name": item.name, "description": item.description, "priority": item.priority, "status": item.status}
            for item in suites
        ],
        "test_cases": [
            {"id": item.id, "suite_id": item.suite_id, "name": item.name, "priority": item.priority, "test_type": item.test_type, "status": item.status}
            for item in test_cases
        ],
        "recorded_cases": [
            {"id": item.id, "name": item.name, "browser": item.browser, "status": item.status, "base_url": item.base_url}
            for item in recorded_cases
        ],
        "executions": [
            {"id": item.id, "test_name": item.test_name, "browser": item.browser, "environment": item.environment, "status": item.status, "duration_seconds": item.duration_seconds, "success_percentage": item.success_percentage}
            for item in executions
        ],
        "reports": [
            {"id": item.id, "execution_id": item.execution_id, "html_path": item.html_path, "excel_path": item.excel_path, "pdf_path": item.pdf_path}
            for item in reports
        ],
    }


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["projects.view"]))):
    project = ProjectService(db).get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["projects.manage"]))):
    return ProjectService(db).create_project(data)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["projects.manage"]))):
    project = ProjectService(db).update_project(project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["projects.manage"]))):
    deleted = ProjectService(db).delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}
