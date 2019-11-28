import logging
from functools import wraps
from typing import List

import telegram
from spotipy.client import Spotify, SpotifyException

from spotigram.authorization import get_clients_or_auth_url


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class SpotifyClientProxy:

    def __init__(self, clients: List[Spotify]):
        self._clients = clients

    @property
    def single_client(self):
        return self._clients[-1]

    def __getattr__(self, name):
        if len(self._clients) > 1:
            def func(*args, **kwargs):
                return [
                    getattr(o, name)(*args, **kwargs)
                    for o in self._clients
                ]
            return func
        else:
            return getattr(self.single_client, name)


def _spotify_decorator(multi_client=False):

    def decorator(func):
        @wraps(func)
        def returnfunction(bot, update, *args, **kwargs):

            chat_id = update.message.chat_id
            clients, url = get_clients_or_auth_url(
                chat_id)
            if clients is None:
                bot.send_message(
                    chat_id=chat_id,
                    text=f"[First, log in with your Spotify account]({url})",
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
            else:
                client = (
                    SpotifyClientProxy(clients) if multi_client
                    else SpotifyClientProxy(clients[-1:])
                )
                try:
                    logger.info(f'Executing: {func.__name__}')
                    return func(client, bot, update, *args, **kwargs)
                except SpotifyException as e:
                    bot.send_message(chat_id=chat_id, text=e.msg)

        return returnfunction
    return decorator


spotify_action = _spotify_decorator(multi_client=False)
spotify_multi_action = _spotify_decorator(multi_client=True)
