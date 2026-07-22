from src.connectors.redis_manager import RedisManager
from src.config import settings

redis_manager = RedisManager(settings.REDIS_URL)
