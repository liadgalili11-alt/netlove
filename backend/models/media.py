from pydantic import BaseModel


class MediaUploadResponse(BaseModel):
    media_id: str
    media_type: str
    filename: str
    size_bytes: int
