from dataclasses import dataclass

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "application/pdf": ".pdf",
}


@dataclass
class UploadedFile:
    """An upload that has already passed the checks in the api layer."""

    original_name: str
    content_type: str
    extension: str
    data: bytes
