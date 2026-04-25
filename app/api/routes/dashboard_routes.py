from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.security.auth_utils import require_permissions
from app.schemas.dashboard_schema import DashboardMetrics
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["dashboard.view"]))):
    return DashboardService(db).get_metrics()
