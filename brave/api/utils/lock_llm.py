import asyncio
from typing import Tuple, Dict

_locks: Dict[Tuple[str, str], asyncio.Lock] = {}
_locks_guard = asyncio.Lock()  # 保护 _locks

class BizProjectLock:
    def __init__(self, biz_id: str, project_id: str):
        self.key = (biz_id, project_id)
        self.lock: asyncio.Lock | None = None

    async def __aenter__(self):
        async with _locks_guard:
            if self.key not in _locks:
                _locks[self.key] = asyncio.Lock()
            self.lock = _locks[self.key]

        # 等待锁
        await self.lock.acquire()
        print(f"Acquired lock for biz_id={self.key[0]}, project_id={self.key[1]}")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # 释放锁
        self.lock.release()

        # 自动清理（必须重新获取 guard 才安全）
        async with _locks_guard:
            if not self.lock.locked():  # 全部释放完毕
                del _locks[self.key]
        print(f"Released lock for biz_id={self.key[0]}, project_id={self.key[1]}")