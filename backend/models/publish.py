from typing import Literal
from pydantic import BaseModel
from backend.models.content import GeneratedContent


class PublishRequest(BaseModel):
    media_id: str
    content: GeneratedContent
    platforms: list[Literal["instagram", "facebook", "tiktok"]]


class PublishResult(BaseModel):
    platform: str
    success: bool
    post_id: str = ""
    url: str = ""
    error: str = ""
