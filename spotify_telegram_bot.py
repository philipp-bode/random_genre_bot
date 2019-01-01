import logging
import os
from functools import wraps

import telegram
from spotipy.client import SpotifyException
from telegram.ext import CommandHandler

from authorization import get_client_or_auth_url

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def spotify_action(func):

    @wraps(func)
    def returnfunction(bot, update, *args, **kwargs):

        chat_id = update.message.chat_id
        client_or_url = get_client_or_auth_url(chat_id)
        if isinstance(client_or_url, str):
            bot.send_message(
                chat_id=chat_id, text="You'll have to log in first:")
            bot.send_message(
                chat_id=chat_id, text=client_or_url)
        else:
            try:
                logger.info(f'Executing: {func.__name__}')
                return func(client_or_url, bot, update, *args, **kwargs)
            except SpotifyException as e:
                bot.send_message(chat_id=chat_id, text=e.msg)

    return returnfunction


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
        auth_url = get_client_or_auth_url(chat_id, force_reauth=True)
        bot.send_message(
            chat_id=chat_id, text=auth_url)

    @staticmethod
    @spotify_action
    def pause(client, bot, update):
        client.pause_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='I paused your playback.')

    @staticmethod
    @spotify_action
    def play(client, bot, update):
        client.start_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='Playing again...')

    @classmethod
    def handlers(cls):
        return (
            CommandHandler('authorize', cls.force_authorization),
            CommandHandler('start', cls.force_authorization),
            CommandHandler('pause', cls.pause),
            CommandHandler('play', cls.play),
        )
