"""Rate limiting utilities for API calls."""

import asyncio
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    calls_per_minute: int = 60
    calls_per_hour: int = 1000
    burst_size: int = 10  # Allow burst of requests


class RateLimiter:
    """Token bucket rate limiter for async functions."""

    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.minute_tokens = config.calls_per_minute
        self.hour_tokens = config.calls_per_hour
        self.last_minute_refill = time.time()
        self.last_hour_refill = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self, resource_name: str = "default") -> bool:
        """
        Acquire permission to make an API call.

        Args:
            resource_name: Name of the resource for logging

        Returns:
            True if call is allowed, raises exception if rate limit exceeded

        Raises:
            RuntimeError: If rate limit is exceeded
        """
        async with self.lock:
            current_time = time.time()

            # Refill minute bucket
            time_since_minute = current_time - self.last_minute_refill
            if time_since_minute >= 60:
                self.minute_tokens = self.config.calls_per_minute
                self.last_minute_refill = current_time
            elif time_since_minute > 0:
                # Gradual refill based on time elapsed
                refill_amount = (time_since_minute / 60) * self.config.calls_per_minute
                self.minute_tokens = min(
                    self.config.calls_per_minute, self.minute_tokens + refill_amount
                )

            # Refill hour bucket
            time_since_hour = current_time - self.last_hour_refill
            if time_since_hour >= 3600:
                self.hour_tokens = self.config.calls_per_hour
                self.last_hour_refill = current_time
            elif time_since_hour > 0:
                # Gradual refill based on time elapsed
                refill_amount = (time_since_hour / 3600) * self.config.calls_per_hour
                self.hour_tokens = min(
                    self.config.calls_per_hour, self.hour_tokens + refill_amount
                )

            # Check if we have tokens available
            if self.minute_tokens < 1:
                wait_time = 60 - time_since_minute
                logger.warning(
                    f"Rate limit exceeded for {resource_name}: "
                    f"per-minute limit reached. Wait {wait_time:.1f}s"
                )
                raise RuntimeError(
                    f"Rate limit exceeded: {self.config.calls_per_minute} calls/minute. "
                    f"Retry after {wait_time:.1f} seconds"
                )

            if self.hour_tokens < 1:
                wait_time = 3600 - time_since_hour
                logger.warning(
                    f"Rate limit exceeded for {resource_name}: "
                    f"per-hour limit reached. Wait {wait_time:.1f}s"
                )
                raise RuntimeError(
                    f"Rate limit exceeded: {self.config.calls_per_hour} calls/hour. "
                    f"Retry after {wait_time:.1f} seconds"
                )

            # Consume tokens
            self.minute_tokens -= 1
            self.hour_tokens -= 1

            logger.debug(
                f"Rate limiter for {resource_name}: "
                f"minute_tokens={self.minute_tokens:.1f}, "
                f"hour_tokens={self.hour_tokens:.1f}"
            )

            return True


class RateLimiterRegistry:
    """Registry for managing multiple rate limiters."""

    def __init__(self):
        """Initialize rate limiter registry."""
        self._limiters: Dict[str, RateLimiter] = {}
        self._configs: Dict[str, RateLimitConfig] = {}

    def register(self, name: str, config: RateLimitConfig):
        """
        Register a rate limiter.

        Args:
            name: Name of the rate limiter
            config: Rate limit configuration
        """
        self._limiters[name] = RateLimiter(config)
        self._configs[name] = config
        logger.info(
            f"Registered rate limiter '{name}': "
            f"{config.calls_per_minute} calls/min, {config.calls_per_hour} calls/hour"
        )

    def get(self, name: str) -> Optional[RateLimiter]:
        """
        Get a rate limiter by name.

        Args:
            name: Name of the rate limiter

        Returns:
            RateLimiter instance or None if not found
        """
        return self._limiters.get(name)

    def get_config(self, name: str) -> Optional[RateLimitConfig]:
        """
        Get rate limit configuration by name.

        Args:
            name: Name of the rate limiter

        Returns:
            RateLimitConfig or None if not found
        """
        return self._configs.get(name)


# Global registry
_registry = RateLimiterRegistry()


def get_rate_limiter_registry() -> RateLimiterRegistry:
    """Get the global rate limiter registry."""
    return _registry


def rate_limit(limiter_name: str):
    """
    Decorator for rate limiting async functions.

    Args:
        limiter_name: Name of the rate limiter to use

    Example:
        @rate_limit("openai_api")
        async def call_gpt4(prompt):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            registry = get_rate_limiter_registry()
            limiter = registry.get(limiter_name)

            if limiter is None:
                logger.warning(
                    f"Rate limiter '{limiter_name}' not registered, "
                    "proceeding without rate limiting"
                )
                return await func(*args, **kwargs)

            # Acquire permission
            await limiter.acquire(resource_name=limiter_name)

            # Call the function
            return await func(*args, **kwargs)

        return wrapper

    return decorator
