# app/sessions.py
import json, secrets, time, asyncio
from typing import Optional, TypedDict, Dict, Tuple
from src.settings import get_settings

class SessionData(TypedDict, total=False):
    user_id: str
    discord_id: str
    token_meta: dict
    csrf: str

class InMemorySessionStore:
    def __init__(self):
        self.ttl = get_settings().SESSION_TTL_SECONDS
        self._lock = asyncio.Lock()
        # sid -> (json string, expires_at_epoch)
        self._data: Dict[str, Tuple[str, float]] = {}
        self._janitor_task: Optional[asyncio.Task] = None

    async def start(self):
        # optional background janitor to purge expired sessions
        async def _janitor():
            try:
                while True:
                    await asyncio.sleep(60)
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

    async def create(self, *, user_id: str, discord_id: str, token_meta: dict) -> str:
        sid = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        payload: SessionData = {
            "user_id": user_id,
            "discord_id": discord_id,
            "token_meta": token_meta,
            "csrf": csrf,
        }
        async with self._lock:
            self._data[sid] = (json.dumps(payload), time.time() + self.ttl)
        return sid

    async def get(self, sid: str) -> Optional[SessionData]:
        now = time.time()
        async with self._lock:
            item = self._data.get(sid)
            if not item:
                return None
            raw, exp = item
            if exp <= now:
                self._data.pop(sid, None)
                return None
        return json.loads(raw)

    async def touch(self, sid: str) -> None:
        async with self._lock:
            if sid in self._data:
                raw, _ = self._data[sid]
                self._data[sid] = (raw, time.time() + self.ttl)

    async def destroy(self, sid: str) -> None:
        async with self._lock:
            self._data.pop(sid, None)