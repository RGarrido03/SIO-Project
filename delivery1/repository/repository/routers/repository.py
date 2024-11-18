from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat
from fastapi import APIRouter

from repository.config.settings import settings

router = APIRouter(prefix="/repository", tags=["Repository"])


@router.get("/public_key")
async def get_public_key() -> str:
    return settings.KEYS[1].public_bytes(Encoding.PEM, PublicFormat.PKCS1).decode()
