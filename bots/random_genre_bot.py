import telegram
from telegram.ext import (
    CommandHandler,
    Filters,
    MessageHandler,
)

from spotigram import (
    SpotigramBot,
    spotify_multi_action,
)
from spotigram.store import get_store_from_env_for
from genres import (
    GenrePlaylist,
    random_genres,
)

CHAT_DATA = get_store_from_env_for('chat')


class RandomGenreBot(SpotigramBot):

    @staticmethod
    def genres(bot, update, chat_data):
        chat_id = update.message.chat_id
        playlists = random_genres(3)

        CHAT_DATA.set(chat_id, 'playlists', [pl._uri for pl in playlists])

        response = 'Choose a genre:\n\n' + '\n'.join([
            f'({pos + 1}) {pl.name}' for pos, pl in
            enumerate(playlists)
        ])
        keyboard = telegram.ReplyKeyboardMarkup(
            [[str(pos)] for pos in range(1, len(playlists) + 1)]
        )
        bot.send_message(
            chat_id=chat_id,
            text=response,
            reply_markup=keyboard
        )

    @staticmethod
    @spotify_multi_action
    def choose(multi_client, bot, update, chat_data):
        try:
            choice = int(update.message.text)
        except ValueError:
            choice = None

        chat_id = update.message.chat_id
        playlist_uris = CHAT_DATA.get(chat_id, 'playlists')

        if choice and playlist_uris:
            pl = GenrePlaylist(playlist_uris[choice - 1])
            multi_client.start_playback(
                context_uri=pl.uri)

            bot.send_message(
                chat_id=chat_id,
                text=f'Now listening to: [{pl.name}]({pl.link})',
                reply_markup=telegram.ReplyKeyboardRemove(),
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

    @classmethod
    def custom_handlers(cls):
        return (
            CommandHandler('genres', cls.genres, pass_chat_data=True),
            MessageHandler(Filters.text, cls.choose, pass_chat_data=True),
        )


if __name__ == '__main__':
    RandomGenreBot.run()
