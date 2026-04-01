from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models.content import GeneratedContent
from backend.services.ai_service import generate_content as _generate
from backend.storage.temp_store import get_store

router = APIRouter(prefix="/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    media_id: str
    user_context: str = ""


@router.post("/generate", response_model=GeneratedContent)
async def generate_content(req: AnalysisRequest) -> GeneratedContent:
    """
    Analyze uploaded media and generate marketing content using GPT-4o.

    - For images: sends 1 image to GPT-4o.
    - For videos: extracts up to 8 frames and sends them as a multi-image message.

    Returns hook, caption, and hashtags.
    """
    store = get_store()
    entry = store.get(req.media_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="media_id לא נמצא. ייתכן שפג תוקפו.")

    try:
        return await _generate(
            file_path=entry.path,
            media_type=entry.media_type,
            user_context=req.user_context,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בייצור תוכן: {e}")
