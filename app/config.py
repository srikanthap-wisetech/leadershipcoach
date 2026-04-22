from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_environment: str = os.getenv("APP_ENVIRONMENT", "development")
    app_base_url: str = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
    leadwise_data_dir: str = os.getenv("LEADWISE_DATA_DIR", "")
    database_url: str = os.getenv("DATABASE_URL", "")
    bootstrap_json_to_database: bool = os.getenv("BOOTSTRAP_JSON_TO_DATABASE", "true").lower() in {"1", "true", "yes"}
    web_concurrency: int = int(os.getenv("WEB_CONCURRENCY", "2"))
    microsoft_app_id: str = os.getenv("MICROSOFT_APP_ID", "")
    microsoft_app_password: str = os.getenv("MICROSOFT_APP_PASSWORD", "")
    microsoft_app_type: str = os.getenv("MICROSOFT_APP_TYPE", "MultiTenant")
    microsoft_app_tenant_id: str = os.getenv("MICROSOFT_APP_TENANT_ID", "")

    @property
    def bot_auth_config(self) -> dict[str, str]:
        return {
            "MicrosoftAppId": self.microsoft_app_id,
            "MicrosoftAppPassword": self.microsoft_app_password,
            "MicrosoftAppType": self.microsoft_app_type,
            "MicrosoftAppTenantId": self.microsoft_app_tenant_id,
        }


settings = Settings()
