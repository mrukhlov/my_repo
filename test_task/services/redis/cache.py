import asyncio
import functools
import json
from typing import Any, Callable, Optional

from redis.asyncio import Redis, RedisError

from test_task.settings import settings


class Cache:  # noqa: WPS338
    """Cache class."""

    def __init__(self, redis: Redis, prefix: str = settings.cache_prefix):
        self.redis = Redis(connection_pool=redis)
        self.prefix = prefix

    def _generate_cache_key(self, key: str) -> str:
        """
        Generate cache key.

        :param key: key.
        :return: cache key.
        """
        return f"{self.prefix}:{key}"

    async def _with_backoff(
        self,
        coro: Callable[..., Any],
        *args: Any,
        retries: int = 1,
        base_delay: float = 0.5,
        **kwargs: Any,
    ) -> Any:
        """
        Backoff function for cache reconnect.

        :param coro: coroutine.
        :param retries: retries.
        :param base_delay: base_delay.
        :param args: args.
        :param kwargs: kwargs.
        :raises RedisError: RedisError
        :return: coro result.
        """
        attempt = 0
        while attempt < retries:
            try:
                return await coro(*args, **kwargs)
            except RedisError:
                attempt += 1
                if attempt < retries:
                    await asyncio.sleep(base_delay * 2 ** (attempt - 1))
        raise RedisError(f"Operation failed after {retries} retries")

    async def get(self, key: str) -> Optional[Any]:
        """
        Cache get method.

        :param key: key.
        :return: cached data or nothing.
        """
        cache_key = self._generate_cache_key(key)
        try:
            return await self._with_backoff(self.redis.get, cache_key)
        except RedisError:
            return None

    async def set(  # noqa: WPS324
        self,
        key: str,
        value: Any,
        expire: int = settings.cache_ttl,
    ) -> None:
        """
        Cache set method.

        :param key: key.
        :param value: value.
        :param expire: expire.
        :return: nothing.
        """
        cache_key = self._generate_cache_key(key)
        try:
            await self._with_backoff(self.redis.set, cache_key, value, ex=expire)
        except RedisError:
            return None

    async def delete(self, key: str) -> None:  # noqa: WPS324
        """
        Cache delete method.

        :param key: key.
        :return: nothing.
        """
        cache_key = self._generate_cache_key(key)
        try:
            await self._with_backoff(self.redis.delete, cache_key)
        except RedisError:
            return None

    async def flush(self) -> None:  # noqa: WPS324
        """
        Cache flush method.

        :return: nothing.
        """
        try:
            await self._with_backoff(self.redis.flushdb)
        except RedisError:
            return None


def cacheable(  # noqa: C901
    key_prefix: str,
    dto_model: Any,
    expire: int = settings.cache_ttl,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Cache decorator which can be applied to router method.

    :param key_prefix: key_prefix.
    :param dto_model: dto_model.
    :param expire: expire.
    :return: inner function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            redis: Redis = kwargs.get("redis_pool")
            if not redis:
                raise ValueError(
                    "Redis instance must be provided as a keyword argument",
                )

            cache = Cache(redis)
            cache_key = f"{key_prefix}"

            kwargs_list = [
                value for key, value in kwargs.items() if key.endswith("_id")
            ]
            if kwargs_list:
                cache_key = f"{cache_key}_{kwargs_list[0]}"

            try:
                cached_data = await cache.get(cache_key)
                if cached_data:
                    cached_data = json.loads(cached_data)
                    if isinstance(cached_data, list):
                        cached_data = [
                            dto_model(**json.loads(obj)) for obj in cached_data  # type: ignore  # noqa: E501
                        ]
                    else:
                        cached_data = dto_model(**cached_data)  # type: ignore
                    return cached_data
            except RedisError:
                return None

            result = await func(*args, **kwargs)
            try:
                if isinstance(result, list):
                    result = json.dumps(
                        [dto_model.model_validate(obj).json() for obj in result],
                    )
                else:
                    result = dto_model.model_validate(result).json()
                await cache.set(cache_key, result, expire=expire)
                return result
            except RedisError:
                return None

        return wrapper

    return decorator
