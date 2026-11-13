"""Rate limits for chat (per user) and auth (per IP).

Uses Redis when RATE_LIMIT_REDIS_URL is set; otherwise an in-memory fixed window
(local / single-process only). Non-local environments require Redis and fail closed.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from core.config import settings
from core.deps import CurrentUserDep

logger = logging.getLogger(__name__)

_redis = None
_memory_lock = threading.Lock()
_memory_buckets: dict[str, tuple[int, float]] = {}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _redis_required() -> bool:
    return settings.RATE_LIMIT_ENABLED and settings.APP_ENV != "local"


def _redis_client():
    global _redis
    if not settings.RATE_LIMIT_ENABLED:
        return None
    url = settings.RATE_LIMIT_REDIS_URL
    if not url:
        return None
    if _redis is None:
        try:
            import redis

            _redis = redis.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            _redis.ping()
        except Exception:
            logger.exception("Rate-limit Redis client init failed")
            _redis = None
            return None
    return _redis


def _raise_limited() -> None:
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded. Please try again shortly.",
        headers={"Retry-After": "60"},
    )


def _check_memory(key: str, limit: int) -> None:
    now = time.time()
    with _memory_lock:
        count, window_start = _memory_buckets.get(key, (0, now))
        if now - window_start >= 60:
            count, window_start = 0, now
        count += 1
        _memory_buckets[key] = (count, window_start)
        if count > limit:
            _raise_limited()
        if len(_memory_buckets) > 2048:
            expired = [
                bucket_key
                for bucket_key, (_, start) in _memory_buckets.items()
                if now - start >= 60
            ]
            for bucket_key in expired:
                _memory_buckets.pop(bucket_key, None)


def _check_redis(key: str, limit: int) -> bool:
    """Return True if handled by Redis. False = fall back (local only)."""
    client = _redis_client()
    if client is None:
        return False
    try:
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        count, _ = pipe.execute()
        if int(count) > limit:
            _raise_limited()
        return True
    except HTTPException:
        raise
    except Exception:
        logger.exception("Rate limit Redis check failed for key %s", key)
        return False


def _check(key: str, limit: int) -> None:
    if not settings.RATE_LIMIT_ENABLED or limit <= 0:
        return
    if _check_redis(key, limit):
        return
    if _redis_required():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiting is temporarily unavailable. Please try again shortly.",
        )
    _check_memory(key, limit)


def rate_limit_chat(user: CurrentUserDep) -> None:
    _check(f"rl:chat:{user.id}", settings.RATE_LIMIT_CHAT_PER_MINUTE)


def rate_limit_auth(request: Request) -> None:
    ip = _client_ip(request)
    _check(f"rl:auth:{ip}", settings.RATE_LIMIT_AUTH_PER_MINUTE)


ChatRateLimitDep = Annotated[None, Depends(rate_limit_chat)]
AuthRateLimitDep = Annotated[None, Depends(rate_limit_auth)]
