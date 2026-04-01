"""
Facebook Page publishing via Meta Graph API.

- Images  -> POST /{page_id}/photos
- Videos  -> POST /{page_id}/videos
- Text    -> POST /{page_id}/feed

Docs: https://developers.facebook.com/docs/graph-api/reference/page/photos/
"""

import httpx
from backend.models.content import GeneratedContent
from backend.models.publish import PublishResult


async def publish(
    file_path: str,
    media_type: str,
    content: GeneratedContent,
) -> PublishResult:
    from backend.config import get_settings

    settings = get_settings()
    base = f"{settings.meta_graph_base_url}{settings.meta_graph_api_version}/{settings.meta_page_id}"

    if media_type == "image":
        return await _publish_image(file_path, content, base, settings.meta_page_access_token)
    else:
        return await _publish_video(file_path, content, base, settings.meta_page_access_token)


async def _publish_image(
    file_path: str,
    content: GeneratedContent,
    base_url: str,
    token: str,
) -> PublishResult:
    message = _build_message(content)
    async with httpx.AsyncClient(timeout=60) as client:
        with open(file_path, "rb") as f:
            resp = await client.post(
                f"{base_url}/photos",
                data={"message": message, "access_token": token},
                files={"source": ("photo.jpg", f, "image/jpeg")},
            )
    if resp.is_error:
        return PublishResult(platform="facebook", success=False, error=resp.text)
    post_id = resp.json().get("post_id") or resp.json().get("id", "")
    return PublishResult(platform="facebook", success=True, post_id=post_id)


async def _publish_video(
    file_path: str,
    content: GeneratedContent,
    base_url: str,
    token: str,
) -> PublishResult:
    description = _build_message(content)
    async with httpx.AsyncClient(timeout=120) as client:
        with open(file_path, "rb") as f:
            resp = await client.post(
                f"{base_url}/videos",
                data={"description": description, "access_token": token},
                files={"source": ("video.mp4", f, "video/mp4")},
            )
    if resp.is_error:
        return PublishResult(platform="facebook", success=False, error=resp.text)
    post_id = resp.json().get("id", "")
    return PublishResult(platform="facebook", success=True, post_id=post_id)


def _build_message(content: GeneratedContent) -> str:
    parts = [content.hook, "", content.caption]
    if content.hashtags:
        parts.append("")
        parts.append(" ".join(f"#{h.lstrip('#')}" for h in content.hashtags))
    return "\n".join(parts)
