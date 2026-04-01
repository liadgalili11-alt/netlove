from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    meta_page_access_token: str = ""
    meta_page_id: str = ""
    meta_ig_user_id: str = ""
    meta_graph_api_version: str = "v19.0"
    tiktok_access_token: str = ""
    tiktok_open_id: str = ""
    temp_upload_dir: str = "/tmp/netlove_uploads"
    temp_file_ttl_seconds: int = 3600
    backend_port: int = 8000
    allowed_origins: str = "http://localhost:8501"

    @property
    def meta_graph_base_url(self) -> str:
        return "https://graph.facebook.com/"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
