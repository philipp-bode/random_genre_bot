import json
import os
from abc import (
    ABC,
    abstractmethod,
)

import redis
import redislite


class Store(ABC):

    @abstractmethod
    def values_for(chat_id: str):
        pass

    @abstractmethod
    def keys_for(chat_id: str):
        pass

    @abstractmethod
    def set(chat_id: str, user: str, value: dict):
        pass

    @abstractmethod
    def get(chat_id: str, user: str):
        pass

    @abstractmethod
    def clear(chat_id: str, user: str = None):
        pass


class RedisStore(Store):

    def __init__(self, redis_or_url, prefix):
        if isinstance(redis_or_url, redis.Redis):
            self.redis = redis_or_url
        elif isinstance(redis_or_url, str):
            self.redis = redis.Redis.from_url(redis_or_url)
        else:
            raise RuntimeError(
                f'{self.__class__} must be initialized with '
                'str or redis client.')

        self.prefix = prefix

    def _key(self, chat_id):
        return f'{self.prefix}-{chat_id}'

    def values_for(self, chat_id: str):
        return [
            json.loads(t)
            for t in self.redis.hvals(self._key(chat_id))
        ]

    def keys_for(self, chat_id: str):
        return [
            key.decode('utf-8') for key
            in self.redis.hkeys(self._key(chat_id))
        ]

    def set(self, chat_id: str, user_id: str, value: dict):
        return self.redis.hset(self._key(chat_id), user_id, json.dumps(value))

    def get(self, chat_id: str, user_id: str):
        data = self.redis.hget(self._key(chat_id), user_id)
        return json.loads(data) if data else None

    def clear(self, chat_id: str, user: str = None):
        if user:
            return self.redis.hdel(self._key(chat_id), user)
        else:
            return self.redis.delete(self._key(chat_id))


def get_store_from_env_for(prefix):
    url = os.getenv('REDIS_URL', None)
    if url:
        return RedisStore(url, prefix=prefix)
    else:
        return RedisStore(redislite.Redis('/tmp/redis.db'), prefix=prefix)
