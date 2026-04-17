from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
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
