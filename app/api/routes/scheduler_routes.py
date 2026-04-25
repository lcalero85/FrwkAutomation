from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.security.auth_utils import require_permissions
from app.schemas.scheduler_schema import SchedulerJobCreate, SchedulerJobOut, SchedulerJobUpdate
from app.schemas.execution_schema import RunDemoRequest
from app.services.execution_service import ExecutionService
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["Scheduler"] )


@router.get("/jobs", response_model=list[SchedulerJobOut])
def list_jobs(db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["scheduler.manage"]))):
    return SchedulerService(db).list_jobs()


@router.post("/jobs", response_model=SchedulerJobOut)
def create_job(payload: SchedulerJobCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["scheduler.manage"]))):
    return SchedulerService(db).create_job(payload)


@router.get("/jobs/{job_id}", response_model=SchedulerJobOut)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["scheduler.manage"]))):
    job = SchedulerService(db).get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduler job not found")
    return job


@router.put("/jobs/{job_id}", response_model=SchedulerJobOut)
def update_job(job_id: int, payload: SchedulerJobUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["scheduler.manage"]))):
    job = SchedulerService(db).update_job(job_id, payload)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduler job not found")
    return job


@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["scheduler.manage"]))):
    deleted = SchedulerService(db).delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scheduler job not found")
    return {"deleted": True}


@router.post("/jobs/{job_id}/run-now")
def run_job_now(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["scheduler.manage"]))):
    scheduler = SchedulerService(db)
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduler job not found")

    if job.execution_type != "DEMO":
        raise HTTPException(status_code=400, detail="Only DEMO execution is available in this phase")

    execution = ExecutionService(db).run_demo(RunDemoRequest(
        browser=job.browser,
        headless=job.headless,
        environment=job.environment,
        test="login_demo",
        report=job.report,
    ))
    scheduler.mark_executed(job_id, execution.status)
    return {"job_id": job_id, "execution_id": execution.id, "status": execution.status}
