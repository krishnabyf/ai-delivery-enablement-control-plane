import secrets

from fastapi import Header, HTTPException, status

from app.config import get_settings


def require_api_key(x_api_key: str = Header(default="")) -> None:
    expected = get_settings().api_key
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-API-Key header is required.",
        )
