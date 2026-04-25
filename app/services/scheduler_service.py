from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database.models import SchedulerJob
from app.schemas.scheduler_schema import SchedulerJobCreate, SchedulerJobUpdate


def _default_next_run(schedule_type: str) -> str:
    now = datetime.utcnow()
    value = (schedule_type or "DAILY").upper()
    if value == "HOURLY":
        return (now + timedelta(hours=1)).isoformat(timespec="seconds")
    if value == "WEEKLY":
        return (now + timedelta(days=7)).isoformat(timespec="seconds")
    if value == "MONTHLY":
        return (now + timedelta(days=30)).isoformat(timespec="seconds")
    return (now + timedelta(days=1)).isoformat(timespec="seconds")


class SchedulerService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_jobs(self) -> list[SchedulerJob]:
        return self.db.query(SchedulerJob).order_by(SchedulerJob.id.desc()).all()

    def get_job(self, job_id: int) -> SchedulerJob | None:
        return self.db.query(SchedulerJob).filter(SchedulerJob.id == job_id).first()

    def create_job(self, payload: SchedulerJobCreate) -> SchedulerJob:
        job = SchedulerJob(**payload.model_dump())
        if not job.next_run:
            job.next_run = _default_next_run(job.schedule_type)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_job(self, job_id: int, payload: SchedulerJobUpdate) -> SchedulerJob | None:
        job = self.get_job(job_id)
        if not job:
            return None
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(job, key, value)
        if "schedule_type" in data and not data.get("next_run"):
            job.next_run = _default_next_run(job.schedule_type)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, job_id: int) -> bool:
        job = self.get_job(job_id)
        if not job:
            return False
        self.db.delete(job)
        self.db.commit()
        return True

    def mark_executed(self, job_id: int, status: str) -> SchedulerJob | None:
        job = self.get_job(job_id)
        if not job:
            return None
        job.last_run = datetime.utcnow().isoformat(timespec="seconds")
        job.last_status = status
        job.next_run = _default_next_run(job.schedule_type)
        self.db.commit()
        self.db.refresh(job)
        return job
