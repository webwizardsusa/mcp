"""Rate limits for chat (per authenticated user).

Uses Redis when RATE_LIMIT_REDIS_URL is set; otherwise an in-memory fixed window.
Fails open if Redis is unavailable.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Annotated

from fastapi import Depends, HTTPException, status

from core.config import settings
from core.deps import CurrentUserDep

logger = logging.getLogger(__name__)

_redis = None
_memory_lock = threading.Lock()
_memory_buckets: dict[str, tuple[int, float]] = {}


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
        except Exception:
            logger.exception("Rate-limit Redis client init failed")
            return None
    return _redis


def _check_memory(key: str, limit: int) -> None:
    now = time.time()
    with _memory_lock:
        count, window_start = _memory_buckets.get(key, (0, now))
        if now - window_start >= 60:
            count, window_start = 0, now
        count += 1
        _memory_buckets[key] = (count, window_start)
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again shortly.",
            )


def _check_redis(key: str, limit: int) -> bool:
    """Return True if handled by Redis (success or 429). False = fall back."""
    client = _redis_client()
    if client is None:
        return False
    try:
        count = int(client.incr(key))
        if count == 1:
            client.expire(key, 60)
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again shortly.",
            )
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
    _check_memory(key, limit)


def rate_limit_chat(user: CurrentUserDep) -> None:
    _check(f"rl:chat:{user.id}", settings.RATE_LIMIT_CHAT_PER_MINUTE)


ChatRateLimitDep = Annotated[None, Depends(rate_limit_chat)]
