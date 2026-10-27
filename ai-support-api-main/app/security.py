import hmac
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import Settings, get_settings
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)
async def verify_api_key(
    provided_api_key: str | None = Depends(api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    if not provided_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required.",
        )
    if not hmac.compare_digest(
        provided_api_key,
        settings.app_api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return provided_api_key