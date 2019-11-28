import logging
import os
from functools import wraps
from typing import List

import telegram
from spotipy.client import Spotify, SpotifyException
from telegram.ext import CommandHandler

from spotigram.authorization import (
    CACHE,
    get_clients_or_auth_url,
)

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


def user_link(user):
    return f'[{user}](https://open.spotify.com/user/{user})'


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
            chat_id=chat_id,
            text=f'[Log in with your Spotify account]({auth_url})',
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )

    @staticmethod
    def list_users(bot, update):
        chat_id = update.message.chat_id
        users_markdown = '\n'.join([
            user_link(user)
            for user in CACHE.get_users(chat_id)
        ])
        bot.send_message(
            chat_id=chat_id,
            text=(
                f'Authenticated users:\n{users_markdown}'
                if users_markdown
                else 'No one logged in :('
            ),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )

    @staticmethod
    def logout(bot, update, args):
        chat_id = update.message.chat_id
        try:
            user = args.pop(0)
            logged_out = CACHE.clear(chat_id, user)
            bot.send_message(
                chat_id=chat_id,
                text=(
                    f'User {user_link(user)} logged out.' if logged_out
                    else f'No user "{user}" logged in.'
                ),
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
        except IndexError:
            bot.send_message(
                chat_id=chat_id,
                text='Which user should I log out?',
            )

    @staticmethod
    def logout_all(bot, update):
        chat_id = update.message.chat_id
        CACHE.clear(chat_id)
        bot.send_message(chat_id=chat_id, text='Logged out all users.')

    @staticmethod
    @spotify_multi_action
    def pause(multi_client, bot, update):
        multi_client.pause_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='I paused your playback.')

    @staticmethod
    @spotify_multi_action
    def play(multi_client, bot, update):
        multi_client.start_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='Playing...')

    @classmethod
    def custom_handlers(cls):
        return []

    @classmethod
    def handlers(cls):
        return (
            CommandHandler('login', cls.force_authorization),
            CommandHandler('users', cls.list_users),
            CommandHandler('logout', cls.logout, pass_args=True),
            CommandHandler('logout_all', cls.logout_all),
            CommandHandler('start', cls.force_authorization),
            CommandHandler('pause', cls.pause),
            CommandHandler('play', cls.play),
            *cls.custom_handlers(),
        )
