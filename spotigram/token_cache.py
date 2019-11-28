import json
from abc import (
    ABC,
    abstractmethod,
)

import redis


class TokenCache(ABC):

    @abstractmethod
    def get_tokens(chat_id: str):
        pass

    @abstractmethod
    def get_users(chat_id: str):
        pass

    @abstractmethod
    def set(chat_id: str, user: str, token: dict):
        pass

    @abstractmethod
    def clear(chat_id: str, user: str = None):
        pass


class RedisTokenCache(TokenCache):

    def __init__(self, redis_or_url):
        if isinstance(redis_or_url, redis.Redis):
            self.redis = redis_or_url
        elif isinstance(redis_or_url, str):
            self.redis = redis.Redis.from_url(redis_or_url)
        else:
            raise RuntimeError(
                f'{self.__class__} must be initialized with '
                'str or redis client.')

    def get_tokens(self, chat_id: str):
        return self.redis.hvals(chat_id)

    def get_users(self, chat_id: str):
        return [key.decode('utf-8') for key in self.redis.hkeys(chat_id)]

    def set(self, chat_id: str, user_id: str, token: dict):
        return self.redis.hset(chat_id, user_id, json.dumps(token))

    def clear(self, chat_id: str, user: str = None):
        if user:
            return self.redis.hdel(chat_id, user)
        else:
            return self.redis.delete(chat_id)
