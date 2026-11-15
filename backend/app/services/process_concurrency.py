"""Process Concurrency and Resource Semaphores.
Prevents server overload from concurrent LibreOffice PDF conversions and Playwright headless runs.
Enforces strict timeouts and bounded concurrency:
- LibreOffice: max 3 concurrent processes, 30s timeout.
- Playwright / Headless Browser: max 2 concurrent sessions, 60s timeout.
"""

import asyncio
import threading
from contextlib import asynccontextmanager, contextmanager
import logging

logger = logging.getLogger(__name__)

# Asynchronous Semaphores
_ASYNC_LIBREOFFICE_SEM = asyncio.Semaphore(3)
_ASYNC_PLAYWRIGHT_SEM = asyncio.Semaphore(2)

# Thread-safe Synchronous Semaphores (for sync execution paths)
_SYNC_LIBREOFFICE_SEM = threading.Semaphore(3)
_SYNC_PLAYWRIGHT_SEM = threading.Semaphore(2)


@asynccontextmanager
async def libreoffice_async_limit(timeout: float = 30.0):
    """Limits concurrent async LibreOffice executions to 3 with a timeout."""
    try:
        await asyncio.wait_for(_ASYNC_LIBREOFFICE_SEM.acquire(), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Timed out after {timeout}s waiting for LibreOffice concurrency permit.")
        raise TimeoutError(f"Server busy: LibreOffice rendering queue timed out after {timeout}s.")
    try:
        yield
    finally:
        _ASYNC_LIBREOFFICE_SEM.release()


@contextmanager
def libreoffice_sync_limit(timeout: float = 30.0):
    """Limits concurrent synchronous LibreOffice executions to 3 with a timeout."""
    acquired = _SYNC_LIBREOFFICE_SEM.acquire(timeout=timeout)
    if not acquired:
        logger.error(f"Timed out after {timeout}s waiting for synchronous LibreOffice concurrency permit.")
        raise TimeoutError(f"Server busy: LibreOffice rendering queue timed out after {timeout}s.")
    try:
        yield
    finally:
        _SYNC_LIBREOFFICE_SEM.release()


@asynccontextmanager
async def playwright_async_limit(timeout: float = 60.0):
    """Limits concurrent async Playwright browser instances to 2 with a timeout."""
    try:
        await asyncio.wait_for(_ASYNC_PLAYWRIGHT_SEM.acquire(), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Timed out after {timeout}s waiting for Playwright concurrency permit.")
        raise TimeoutError(f"Server busy: Playwright rendering queue timed out after {timeout}s.")
    try:
        yield
    finally:
        _ASYNC_PLAYWRIGHT_SEM.release()
