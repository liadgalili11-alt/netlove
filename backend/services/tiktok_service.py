"""
TikTok video publishing via TikTok Content Posting API v2.

Three-step flow:
1. POST /v2/post/publish/video/init  -> get upload_url + publish_id
2. PUT  {upload_url}                 -> upload raw video bytes
3. POST /v2/post/publish/video/complete -> trigger publishing

Only supports video (MP4). Images are not supported by this API.
"""

import httpx
from backend.models.content import GeneratedContent
from backend.models.publish import PublishResult

TIKTOK_BASE = "https://open.tiktokapis.com"


async def publish(
    file_path: str,
    media_type: str,
    content: GeneratedContent,
) -> PublishResult:
    from backend.config import get_settings

    settings = get_settings()
    if not settings.tiktok_access_token:
        return PublishResult(platform="tiktok", success=False, error="TikTok access token not configured")

    if media_type != "video":
        return PublishResult(platform="tiktok", success=False, error="TikTok only supports video uploads")

    headers = {"Authorization": f"Bearer {settings.tiktok_access_token}"}
    caption = content.hook + "\n" + content.caption

    async with httpx.AsyncClient(timeout=120) as client:
        # Step 1: init
        r1 = await client.post(
            f"{TIKTOK_BASE}/v2/post/publish/video/init/",
            headers=headers,
            json={
                "post_info": {"title": caption[:150], "privacy_level": "PUBLIC_TO_EVERYONE"},
                "source_info": {"source": "FILE_UPLOAD"},
            },
        )
        if r1.is_error:
            return PublishResult(platform="tiktok", success=False, error=r1.text)

        data = r1.json().get("data", {})
        upload_url = data.get("upload_url", "")
        publish_id = data.get("publish_id", "")

        # Step 2: upload video
        with open(file_path, "rb") as f:
            video_bytes = f.read()
        r2 = await client.put(
            upload_url,
            content=video_bytes,
            headers={"Content-Type": "video/mp4", "Content-Length": str(len(video_bytes))},
        )
        if r2.is_error:
            return PublishResult(platform="tiktok", success=False, error=r2.text)

        # Step 3: complete
        r3 = await client.post(
            f"{TIKTOK_BASE}/v2/post/publish/video/complete/",
            headers=headers,
            json={"publish_id": publish_id},
        )
        if r3.is_error:
            return PublishResult(platform="tiktok", success=False, error=r3.text)

    return PublishResult(platform="tiktok", success=True, post_id=publish_id)
