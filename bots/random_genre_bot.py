import telegram
from telegram.ext import (
    CommandHandler,
    Filters,
    MessageHandler,
)

from genres import Playlist
from spotigram import (
    SpotigramBot,
    spotify_action,
    spotify_multi_action,
)


class RandomGenreBot(SpotigramBot):

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
    @spotify_multi_action
    def choose(multi_client, bot, update, chat_data):
        try:
            choice = int(update.message.text)
        except ValueError:
            choice = None

        if choice and 'playlists' in chat_data:
            chosen_pl = chat_data['playlists'][choice - 1]
            multi_client.start_playback(
                context_uri=chosen_pl.context_uri)
            reply_markup = telegram.ReplyKeyboardRemove()
            bot.send_message(
                chat_id=update.message.chat_id,
                text=f'Now listening to: {chosen_pl.name}',
                reply_markup=reply_markup,
            )

    @classmethod
    def custom_handlers(cls):
        return (
            CommandHandler('genres', cls.genres, pass_chat_data=True),
            MessageHandler(Filters.text, cls.choose, pass_chat_data=True),
        )


if __name__ == '__main__':
    RandomGenreBot.run()
