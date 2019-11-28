import telegram
from telegram.ext import (
    CommandHandler,
    Filters,
    MessageHandler,
)

from spotigram import (
    SpotigramBot,
    spotify_action,
    spotify_multi_action,
)
from genres import random_genres


class RandomGenreBot(SpotigramBot):

    @staticmethod
    @spotify_action
    def genres(client, bot, update, chat_data):
        playlists = random_genres(3)
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
            pl = chat_data['playlists'][choice - 1]
            multi_client.start_playback(
                context_uri=pl.uri)

            bot.send_message(
                chat_id=update.message.chat_id,
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
