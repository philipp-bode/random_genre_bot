import logging
import os
from functools import wraps
from typing import List

import telegram
from spotipy.client import Spotify, SpotifyException
from telegram.ext import CommandHandler

from authorization import get_clients_or_auth_url

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class SpotifyClientProxy:

    def __init__(self, clients: List[Spotify]):
        self._clients = clients

    @property
    def newest(self):
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
            return getattr(self.newest, name)


def _spotify_decorator(multi_client=False):

    def decorator(func):
        @wraps(func)
        def returnfunction(bot, update, *args, **kwargs):

            chat_id = update.message.chat_id
            clients, auth_url = get_clients_or_auth_url(
                chat_id)
            if clients is None:
                bot.send_message(
                    chat_id=chat_id, text="You'll have to log in first:")
                bot.send_message(
                    chat_id=chat_id, text=auth_url)
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


class SpotifyTelegramBot:

    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TOKEN:
        raise RuntimeError('Please set TELEGRAM_TOKEN in your environment.')

    @classmethod
    def bot(cls):
        return telegram.Bot(cls.TOKEN)

    @staticmethod
    def force_authorization(bot, update):
        chat_id = update.message.chat_id
        _, auth_url = get_clients_or_auth_url(
            chat_id, force_reauth=True)
        bot.send_message(
            chat_id=chat_id, text=auth_url)

    @staticmethod
    @spotify_multi_action
    def pause(client, bot, update):
        client.pause_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='I paused your playback.')

    @staticmethod
    @spotify_multi_action
    def play(client, bot, update):
        client.start_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='Playing again...')

    @classmethod
    def custom_handlers(cls):
        return []

    @classmethod
    def handlers(cls):
        return (
            CommandHandler('authorize', cls.force_authorization),
            CommandHandler('start', cls.force_authorization),
            CommandHandler('pause', cls.pause),
            CommandHandler('play', cls.play),
            *cls.custom_handlers(),
        )
