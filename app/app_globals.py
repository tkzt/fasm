from slowapi import Limiter
from settings import settings
from utils.redis_util import RedisUtil
from slowapi.util import get_remote_address


redis_util = RedisUtil(settings.REDIS_URI)
limiter = Limiter(key_func=get_remote_address)
