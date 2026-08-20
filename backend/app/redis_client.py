import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._memory_queues: Dict[str, List[str]] = {}
        self._memory_kv: Dict[str, str] = {}

    async def connect(self):
        try:
            self.redis = aioredis.from_url(
                settings.REDIS_URL, 
                decode_responses=True,
                socket_timeout=5.0
            )
            await self.redis.ping()
            logger.info("Connected to Redis server successfully.")
        except Exception as e:
            logger.warning(f"Redis connection failed ({e}). Using in-memory queue fallback.")
            self.redis = None

    async def push_job(self, workstation_ip: str, job_payload: Dict[str, Any]) -> bool:
        queue_key = f"queue:autodesk:{workstation_ip}"
        data = json.dumps(job_payload)
        if self.redis:
            try:
                await self.redis.rpush(queue_key, data)
                return True
            except Exception as e:
                logger.error(f"Redis rpush error: {e}")
        
        # Fallback
        if queue_key not in self._memory_queues:
            self._memory_queues[queue_key] = []
        self._memory_queues[queue_key].append(data)
        return True

    async def pop_job(self, workstation_ip: str) -> Optional[Dict[str, Any]]:
        queue_key = f"queue:autodesk:{workstation_ip}"
        if self.redis:
            try:
                data = await self.redis.lpop(queue_key)
                if data:
                    return json.loads(data)
                return None
            except Exception as e:
                logger.error(f"Redis lpop error: {e}")
        
        # Fallback
        if queue_key in self._memory_queues and len(self._memory_queues[queue_key]) > 0:
            data = self._memory_queues[queue_key].pop(0)
            return json.loads(data)
        return None

    async def set_job_state(self, job_id: str, state_data: Dict[str, Any], expire_sec: int = 86400):
        key = f"job:state:{job_id}"
        data = json.dumps(state_data)
        if self.redis:
            try:
                await self.redis.set(key, data, ex=expire_sec)
                return
            except Exception as e:
                logger.error(f"Redis set state error: {e}")
        self._memory_kv[key] = data

    async def get_job_state(self, job_id: str) -> Optional[Dict[str, Any]]:
        key = f"job:state:{job_id}"
        if self.redis:
            try:
                data = await self.redis.get(key)
                if data:
                    return json.loads(data)
                return None
            except Exception as e:
                logger.error(f"Redis get state error: {e}")
        
        if key in self._memory_kv:
            return json.loads(self._memory_kv[key])
        return None

redis_manager = RedisManager()
