import telegram
from telegram.ext import (
    CommandHandler,
    Filters,
    Updater,
    MessageHandler,
)

from genres import Playlist
from spotify_telegram_bot import (
    SpotifyTelegramBot,
    spotify_action,
)


class RandomGenreBot(SpotifyTelegramBot):

    @staticmethod
    @spotify_action
    def genres(client, bot, update, chat_data):
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
        try:
            choice = int(update.message.text) - 1
        except ValueError:
            choice = None

        if choice and 'playlists' in chat_data:
            chosen_pl = chat_data['playlists'][choice]
            client.start_playback(
                context_uri=chosen_pl.context_uri)
            bot.send_message(
                chat_id=update.message.chat_id,
                text=f'Now listening to: {chosen_pl.name}'
            )

    @classmethod
    def handlers(cls):
        return super().handlers() + (
            CommandHandler('genres', cls.genres, pass_chat_data=True),
            MessageHandler(Filters.text, cls.choose, pass_chat_data=True),
        )


if __name__ == '__main__':

    updater = Updater(token=RandomGenreBot.TOKEN)
    dispatcher = updater.dispatcher
    for handler in RandomGenreBot.handlers():
        dispatcher.add_handler(handler)
    updater.start_polling()
