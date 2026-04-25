from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class SettingItem(BaseModel):
    setting_key: str
    setting_value: Optional[str] = None
    setting_type: str = "string"
    description: Optional[str] = None


class SettingsPayload(BaseModel):
    app_name: str = Field(default="AutoTest Pro Framework", max_length=120)
    company_name: str = Field(default="AutoTest Pro", max_length=120)
    support_email: str = Field(default="support@autotestpro.local", max_length=160)
    website_url: str = Field(default="https://autotestpro.local", max_length=240)
    logo_text: str = Field(default="AT", max_length=4)
    tagline: str = Field(default="Plataforma de Automatización QA", max_length=160)
    primary_color: str = Field(default="#2463eb", max_length=20)
    secondary_color: str = Field(default="#0e1930", max_length=20)
    theme: str = Field(default="Corporate Light", max_length=80)
    language: str = Field(default="es", max_length=10)
    timezone: str = Field(default="America/El_Salvador", max_length=80)
    reports_path: str = Field(default="reports", max_length=240)
    logs_path: str = Field(default="logs", max_length=240)
    screenshots_path: str = Field(default="screenshots", max_length=240)
    videos_path: str = Field(default="videos", max_length=240)
    default_browser: str = Field(default="chrome", max_length=40)
    default_environment: str = Field(default="demo", max_length=80)
    execution_timeout: str = Field(default="60", max_length=20)
    screenshot_on_failure: str = Field(default="true", max_length=10)
    screenshot_each_step: str = Field(default="false", max_length=10)
    smtp_server: str = Field(default="", max_length=160)
    smtp_port: str = Field(default="587", max_length=10)
    smtp_user: str = Field(default="", max_length=160)
    smtp_password: str = Field(default="", max_length=500)
    smtp_sender: str = Field(default="", max_length=160)
    smtp_use_tls: str = Field(default="true", max_length=10)
    smtp_use_ssl: str = Field(default="false", max_length=10)
    smtp_default_recipients: str = Field(default="", max_length=500)


class SettingsResponse(SettingsPayload):
    pass
