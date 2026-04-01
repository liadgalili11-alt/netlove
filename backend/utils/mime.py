_CONTENT_TYPE_MAP = {
    "image/jpeg": "image",
    "image/png": "image",
    "video/mp4": "video",
}

_ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "mp4", "mov", "m4v"}


def get_media_type(content_type: str) -> str | None:
    """Returns 'image' or 'video', or None if not allowed."""
    return _CONTENT_TYPE_MAP.get(content_type)


def is_allowed_extension(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in _ALLOWED_EXTENSIONS
