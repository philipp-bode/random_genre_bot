import logging
import os
from functools import wraps

import telegram
from spotipy.client import SpotifyException
from telegram.ext import (
    CommandHandler,
    Filters,
    Updater,
    MessageHandler,
)

from authorization import get_client_or_auth_url
from genres import Playlist

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
                return func(client_or_url, bot, update, *args, **kwargs)
            except SpotifyException as e:
                bot.send_message(chat_id=chat_id, text=e.msg)

    return returnfunction


class RandomGenreBot:

    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TOKEN:
        raise RuntimeError('Please set TELEGRAM_TOKEN in your environment.')

    @classmethod
    def bot(cls):
        return telegram.Bot(cls.TOKEN)

    @staticmethod
    def force_authorization(bot, update):
        logger.info('Executing: force_authorization')
        chat_id = update.message.chat_id
        auth_url = get_client_or_auth_url(chat_id, force_reauth=True)
        bot.send_message(
            chat_id=chat_id, text=auth_url)

    @staticmethod
    @spotify_action
    def pause(client, bot, update):
        logger.info('Executing: pause')
        client.pause_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='I paused your playback.')

    @staticmethod
    @spotify_action
    def play(client, bot, update):
        logger.info('Executing: play')
        client.start_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='Playing again...')

    @staticmethod
    @spotify_action
    def genres(client, bot, update, chat_data):
        logger.info('Executing: genres')
        playlists = Playlist.fetch_random(client)
        chat_data['playlists'] = playlists
        response = 'Choose a genre:\n\n' + '\n'.join([
            f'({pos + 1}) {pl.name}' for pos, pl in
            enumerate(playlists)
        ])
        keyboard = telegram.ReplyKeyboardMarkup(
            [[str(pos)] for pos in range(1, len(playlists) + 1)]
        )
        bot.send_message(
            chat_id=update.message.chat_id,
            text=response,
            reply_markup=keyboard
        )

    @staticmethod
    @spotify_action
    def choose(client, bot, update, chat_data):
        logger.info('Executing: choose')
        choice = int(update.message.text) - 1
        if 'playlists' in chat_data:
            chosen_pl = chat_data['playlists'][choice]
            client.start_playback(
                context_uri=chosen_pl.context_uri)
            bot.send_message(
                chat_id=update.message.chat_id,
                text=f'Now listening to: {chosen_pl.name}'
            )

    @classmethod
    def handlers(cls):
        return (
            CommandHandler('authorize', cls.force_authorization),
            CommandHandler('start', cls.force_authorization),
            CommandHandler('pause', cls.pause),
            CommandHandler('play', cls.play),
            CommandHandler('genres', cls.genres, pass_chat_data=True),
            MessageHandler(Filters.text, cls.choose, pass_chat_data=True),
        )


if __name__ == '__main__':

    updater = Updater(token=RandomGenreBot.TOKEN)
    dispatcher = updater.dispatcher
    for handler in RandomGenreBot.handlers():
        dispatcher.add_handler(handler)
    updater.start_polling()
