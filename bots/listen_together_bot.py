from spotipy import SpotifyException
from telegram.ext import (
    Filters,
    MessageHandler,
)

from spotigram import (
    SpotigramBot,
    spotify_multi_action,
)


class ListenTogetherBot(SpotigramBot):

    @staticmethod
    @spotify_multi_action
    def select(multi_client, bot, update, chat_data):

        text = update.message.text

        if text.startswith('https://open.spotify.com/'):
            try:
                track = multi_client.single_client.track(text)
                uri = track['uri']
            except SpotifyException:
                uri = None
        elif text.startswith('spotify:'):
            uri = text
        else:
            uri = None

        multi_client.start_playback(uris=[uri])
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f'Now listening to: {uri}'
        )

    @classmethod
    def custom_handlers(cls):
        return (
            MessageHandler(Filters.text, cls.select, pass_chat_data=True),
        )


if __name__ == '__main__':
    ListenTogetherBot.run()
