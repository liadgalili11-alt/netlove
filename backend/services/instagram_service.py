"""
Instagram publishing via Meta Graph API (two-step container pattern).

Step 1: Create a media container (image or reel).
Step 2: Publish the container.

Docs: https://developers.facebook.com/docs/instagram-api/guides/content-publishing
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
    base = f"{settings.meta_graph_base_url}{settings.meta_graph_api_version}/{settings.meta_ig_user_id}"

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
    caption = _build_caption(content)
    async with httpx.AsyncClient(timeout=60) as client:
        with open(file_path, "rb") as f:
            # Step 1: create container
            r1 = await client.post(
                f"{base_url}/media",
                data={"caption": caption, "access_token": token},
                files={"image": ("image.jpg", f, "image/jpeg")},
            )
        if r1.is_error:
            return PublishResult(platform="instagram", success=False, error=r1.text)
        creation_id = r1.json().get("id", "")
        # Step 2: publish
        r2 = await client.post(
            f"{base_url}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
        )
    if r2.is_error:
        return PublishResult(platform="instagram", success=False, error=r2.text)
    return PublishResult(platform="instagram", success=True, post_id=r2.json().get("id", ""))


async def _publish_video(
    file_path: str,
    content: GeneratedContent,
    base_url: str,
    token: str,
) -> PublishResult:
    caption = _build_caption(content)
    async with httpx.AsyncClient(timeout=120) as client:
        with open(file_path, "rb") as f:
            # Step 1: create reel container
            r1 = await client.post(
                f"{base_url}/media",
                data={
                    "media_type": "REELS",
                    "caption": caption,
                    "access_token": token,
                },
                files={"video": ("video.mp4", f, "video/mp4")},
            )
        if r1.is_error:
            return PublishResult(platform="instagram", success=False, error=r1.text)
        creation_id = r1.json().get("id", "")
        # Step 2: publish
        r2 = await client.post(
            f"{base_url}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
        )
    if r2.is_error:
        return PublishResult(platform="instagram", success=False, error=r2.text)
    return PublishResult(platform="instagram", success=True, post_id=r2.json().get("id", ""))


def _build_caption(content: GeneratedContent) -> str:
    parts = [content.hook, "", content.caption]
    if content.hashtags:
        parts.append("")
        parts.append(" ".join(f"#{h.lstrip('#')}" for h in content.hashtags))
    return "\n".join(parts)
