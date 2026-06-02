from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ボリューム検討チャット Clone"
    liff_id: str = Field(default="", alias="LIFF_ID")
    note_id_allowlist: str = Field(
        default="demo-note-001,demo-note-002,member-test", alias="NOTE_ID_ALLOWLIST"
    )
    note_auth_mode: str = Field(default="allowlist", alias="NOTE_AUTH_MODE")
    app_data_dir: Path = Field(default=Path("data"), alias="APP_DATA_DIR")
    ocr_engine: str = Field(default="fallback", alias="OCR_ENGINE")
    target_drive_folder_id: str = Field(
        default="11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD", alias="TARGET_DRIVE_FOLDER_ID"
    )

    @property
    def db_path(self) -> Path:
        return self.app_data_dir / "app.sqlite3"

    @property
    def upload_dir(self) -> Path:
        return self.app_data_dir / "uploads"

    @property
    def output_dir(self) -> Path:
        return self.app_data_dir / "outputs"

    @property
    def allowlist(self) -> set[str]:
        return {item.strip() for item in self.note_id_allowlist.split(",") if item.strip()}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.app_data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    return settings
