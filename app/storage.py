import os
from pathlib import Path

import anyio
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))


def path_for(stored_name: str) -> Path:
    return UPLOAD_DIR / stored_name


async def save(stored_name: str, data: bytes) -> None:
    await anyio.Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    await anyio.Path(path_for(stored_name)).write_bytes(data)


async def exists(stored_name: str) -> bool:
    return await anyio.Path(path_for(stored_name)).exists()


async def delete(stored_name: str) -> None:
    await anyio.Path(path_for(stored_name)).unlink(missing_ok=True)
