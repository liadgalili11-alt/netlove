import base64


def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def base64_to_bytes(data: str) -> bytes:
    return base64.b64decode(data)
