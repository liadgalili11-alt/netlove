import os
import uuid
from fastapi import APIRouter, UploadFile, HTTPException
from backend.config import get_settings
from backend.models.media import MediaUploadResponse
from backend.storage.temp_store import get_store

router = APIRouter(prefix="/media", tags=["media"])

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "mp4", "mov", "m4v"}
CONTENT_TYPE_TO_MEDIA = {
    "image/jpeg": "image",
    "image/png": "image",
    "video/mp4": "video",
    "video/quicktime": "video",
}


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(file: UploadFile) -> MediaUploadResponse:
    """
    Upload a JPG/PNG/MP4 file.
    Returns a media_id that is used in all subsequent API calls.
    """
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="סוג קובץ לא נתמך. יש להעלות JPG, PNG או MP4 בלבד.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="הקובץ גדול מדי. מקסימום 100MB.")

    # Determine media type
    ct = (file.content_type or "").lower()
    media_type = CONTENT_TYPE_TO_MEDIA.get(ct)
    if media_type is None:
        media_type = "video" if ext in {"mp4", "mov", "m4v"} else "image"

    settings = get_settings()
    os.makedirs(settings.temp_upload_dir, exist_ok=True)
    media_id = str(uuid.uuid4())
    dest = os.path.join(settings.temp_upload_dir, f"upload.{media_id}.{ext}")
    with open(dest, "wb") as f:
        f.write(content)

    store = get_store()
    store.register(
        media_id=media_id,
        path=dest,
        media_type=media_type,
        filename=file.filename or f"upload.{ext}",
        size_bytes=len(content),
    )

    return MediaUploadResponse(
        media_id=media_id,
        media_type=media_type,
        filename=file.filename or f"upload.{ext}",
        size_bytes=len(content),
    )
