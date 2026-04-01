import asyncio
from fastapi import APIRouter, HTTPException
from backend.models.publish import PublishRequest, PublishResult
from backend.storage.temp_store import get_store
from backend.services import facebook_service, instagram_service, tiktok_service

router = APIRouter(prefix="/publish", tags=["publish"])

_SERVICES = {
    "facebook": facebook_service.publish,
    "instagram": instagram_service.publish,
    "tiktok": tiktok_service.publish,
}


@router.post("/all", response_model=list[PublishResult])
async def publish_all(req: PublishRequest) -> list[PublishResult]:
    """
    Publish to all requested platforms concurrently.
    One platform failing does NOT abort the others.
    """
    store = get_store()
    entry = store.get(req.media_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="media_id לא נמצא.")

    tasks = [
        _dispatch(platform, entry.path, entry.media_type, req.content)
        for platform in req.platforms
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = []
    for platform, result in zip(req.platforms, results):
        if isinstance(result, Exception):
            output.append(PublishResult(platform=platform, success=False, error=str(result)))
        else:
            output.append(result)
    return output


@router.post("/{platform}", response_model=PublishResult)
async def publish_single(platform: str, req: PublishRequest) -> PublishResult:
    """Publish to a single platform."""
    store = get_store()
    entry = store.get(req.media_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="media_id לא נמצא.")
    if platform not in _SERVICES:
        return await _unsupported_platform(platform)
    return await _dispatch(platform, entry.path, entry.media_type, req.content)


async def _dispatch(platform: str, path: str, media_type: str, content) -> PublishResult:
    svc = _SERVICES.get(platform)
    if svc is None:
        return await _unsupported_platform(platform)
    try:
        return await svc(file_path=path, media_type=media_type, content=content)
    except Exception as e:
        return PublishResult(platform=platform, success=False, error=str(e))


async def _unsupported_platform(platform: str) -> PublishResult:
    return PublishResult(platform=platform, success=False, error=f"פלטפורמה לא נתמכת: {platform}")
