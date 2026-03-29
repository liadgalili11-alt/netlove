"""
Thin httpx wrapper around all Netlove backend endpoints.
All Streamlit page modules import from here — never call the backend directly.
"""

import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "https://netlove.onrender.com").rstrip("/")
TIMEOUT = 120.0  # seconds (AI generation can take a moment)


class NetloveAPIError(Exception):
    """Raised when the backend returns a non-2xx response."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{status_code}] {detail}")


def _raise_for(response: httpx.Response) -> None:
    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise NetloveAPIError(response.status_code, detail)


def upload_media(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """Upload media file. Returns MediaUploadResponse dict."""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/v1/media/upload",
            files={"file": (filename, file_bytes, content_type)},
        )
    _raise_for(resp)
    return resp.json()


def generate_content(media_id: str, user_context: str = "") -> dict:
    """Generate AI content. Returns GeneratedContent dict."""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/v1/analysis/generate",
            json={"media_id": media_id, "user_context": user_context},
        )
    _raise_for(resp)
    return resp.json()


def publish_all(media_id: str, content: dict, platforms: list[str]) -> list[dict]:
    """Publish to selected platforms. Returns list of PublishResult dicts."""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/v1/publish/all",
            json={
                "media_id": media_id,
                "content": content,
                "platforms": platforms,
            },
        )
    _raise_for(resp)
    return resp.json()


def check_health() -> bool:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{BACKEND_URL}/health")
        return resp.status_code == 200
    except Exception:
        return False
