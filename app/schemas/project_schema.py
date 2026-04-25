from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    base_url: str | None = None
    environment_id: int | None = None
    default_browser: str = "chrome"
    status: str = "ACTIVE"


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    base_url: str | None = None
    environment_id: int | None = None
    default_browser: str | None = None
    status: str | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    base_url: str | None = None
    default_browser: str
    status: str
