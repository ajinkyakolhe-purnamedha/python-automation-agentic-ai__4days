"""Reusable decorators (Day 2, Module 5 — built at point of use).

These get reused on every later day:
- Day 2: `@retry` wraps the HTTP `APIClient`
- Day 3: tests verify both decorators behave under failure
- Day 4: `@tool` (in agent.py) is built from the same registration pattern
"""

import functools
import logging
import time

logger = logging.getLogger(__name__)


def log_calls(func):
    """Log every call: the function name, then its return value."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("call %s", func.__name__)
        result = func(*args, **kwargs)
        logger.info("%s returned %r", func.__name__, result)
        return result

    return wrapper


def retry(times=3, delay=0.1, exceptions=(Exception,)):
    """Retry the wrapped function up to `times`, sleeping `delay`s between attempts."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    logger.warning(
                        "%s attempt %d/%d failed: %s",
                        func.__name__, attempt, times, exc,
                    )
                    if attempt == times:
                        raise          # last attempt — give up
                    time.sleep(delay)

        return wrapper

    return decorator
