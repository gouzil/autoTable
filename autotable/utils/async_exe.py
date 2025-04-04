from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from typing import Any


def async_run(coro: Coroutine[Any, Any, Any]) -> Any:
    """
    如果有 loop, 则新建一个线程池, 在其中执行协程
    否则使用 asyncio.run() 执行协程
    """
    try:
        _ = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: _await_future(coro))
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)
    except Exception as e:
        raise e


def _await_future(future):
    return asyncio.run(future)
