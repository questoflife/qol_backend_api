# app/sessions.py
import secrets
import time
import asyncio
import contextlib
from typing import Optional, TypedDict, Dict, Tuple
from src.settings import get_settings

class SessionData(TypedDict, total=False):
    discord_id: str
    token_meta: dict
    csrf: str

class InMemorySessionStore:
    def __init__(self):
        self.ttl = get_settings().SESSION_TTL_SECONDS
        # How often the janitor runs to clean up expired sessions
        self.janitor_interval_seconds = 60
        self._lock = asyncio.Lock()
        # sid -> (session_data, expires_at_epoch)
        self._data: Dict[str, Tuple[SessionData, float]] = {}
        self._janitor_task: Optional[asyncio.Task] = None

    async def start(self):
        # optional background janitor to purge expired sessions
        async def _janitor():
            try:
                while True:
                    await asyncio.sleep(self.janitor_interval_seconds)
                    now = time.time()
                    async with self._lock:
                        expired = [sid for sid, (_, exp) in self._data.items() if exp <= now]
                        for sid in expired:
                            self._data.pop(sid, None)
            except asyncio.CancelledError:
                pass
        self._janitor_task = asyncio.create_task(_janitor())

    async def stop(self):
        if self._janitor_task:
            self._janitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._janitor_task

    async def create(self, *, discord_id: str, token_meta: dict) -> str:
        sid = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        session_data: SessionData = {
            "discord_id": discord_id,
            "token_meta": token_meta,
            "csrf": csrf,
        }
        async with self._lock:
            self._data[sid] = (session_data, time.time() + self.ttl)
        return sid

    async def get(self, sid: str) -> Optional[SessionData]:
        now = time.time()
        async with self._lock:
            item = self._data.get(sid)
            if not item:
                return None
            session_data, exp = item
            if exp <= now:
                self._data.pop(sid, None)
                return None
            return session_data

    async def touch(self, sid: str) -> None:
        async with self._lock:
            if sid in self._data:
                session_data, _ = self._data[sid]
                self._data[sid] = (session_data, time.time() + self.ttl)

    async def destroy(self, sid: str) -> None:
        async with self._lock:
            self._data.pop(sid, None)