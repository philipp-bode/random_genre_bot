import logging
import os

import telegram
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


class RandomGenreBot:

    TOKEN = os.environ.get('TELEGRAM_TOKEN')

    @staticmethod
    def bot():
        return telegram.Bot(RandomGenreBot.TOKEN)

    @staticmethod
    def force_authorization(bot, update):
        logger.info('Executing: force_authorization')
        chat_id = update.message.chat_id
        auth_url = get_client_or_auth_url(chat_id, force_reauth=True)
        bot.send_message(
            chat_id=chat_id, text=auth_url)

    @staticmethod
    def _get_authorized_client(bot, update):
        logger.info('Executing: _get_authorized_client')
        chat_id = update.message.chat_id
        client_or_url = get_client_or_auth_url(chat_id)
        if not isinstance(client_or_url, str):
            return client_or_url
        else:
            bot.send_message(
                chat_id=chat_id, text="You'll have to log in first:")
            bot.send_message(
                chat_id=chat_id, text=client_or_url)

    @staticmethod
    def pause(bot, update):
        logger.info('Executing: pause')
        client = RandomGenreBot._get_authorized_client(bot, update)
        if client:
            client.pause_playback()
            bot.send_message(
                chat_id=update.message.chat_id, text="I paused your playback.")

    @staticmethod
    def play(bot, update):
        logger.info('Executing: play')
        client = RandomGenreBot._get_authorized_client(bot, update)
        if client:
            client.start_playback()
            bot.send_message(
                chat_id=update.message.chat_id, text="Playing again...")

    @staticmethod
    def genres(bot, update, chat_data):
        logger.info('Executing: genres')
        client = RandomGenreBot._get_authorized_client(bot, update)
        if client:
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
    def choose(bot, update, chat_data):
        logger.info('Executing: choose')
        client = RandomGenreBot._get_authorized_client(bot, update)
        choice = int(update.message.text) - 1
        if client and 'playlists' in chat_data:
            chosen_pl = chat_data['playlists'][choice]
            client.start_playback(
                context_uri=chosen_pl.context_uri)
            bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Now listening to: {chosen_pl.name}"
            )

    @staticmethod
    def handlers():
        return (
            CommandHandler('authorize', RandomGenreBot.force_authorization),
            CommandHandler('pause', RandomGenreBot.pause),
            CommandHandler('play', RandomGenreBot.play),
            CommandHandler(
                'genres', RandomGenreBot.genres, pass_chat_data=True),
            MessageHandler(
                Filters.text, RandomGenreBot.choose, pass_chat_data=True),
        )


if __name__ == '__main__':

    updater = Updater(token=RandomGenreBot.TOKEN)
    dispatcher = updater.dispatcher
    for handler in RandomGenreBot.handlers():
        dispatcher.add_handler(handler)
    updater.start_polling()
