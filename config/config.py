import os


class Config:
    def __init__(self):
        self.env = os.getenv("ENV", "dev").lower()
        self.database_url = self._require_env("DATABASE_URL")
        self.app_name = "billing-system"

    def _require_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise EnvironmentError(f"Required environment variable '{key}' is not set.")
        return value
