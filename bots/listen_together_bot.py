import re

from spotipy import SpotifyException
from telegram.ext import (
    Filters,
    MessageHandler,
)

from spotigram import (
    SpotigramBot,
    spotify_multi_action,
)

URL_REGEX = re.compile(r'https:\/\/open.spotify.com\/(\w+)\/')


class ListenTogetherBot(SpotigramBot):

    @staticmethod
    @spotify_multi_action
    def select(multi_client, bot, update):

        text = update.message.text
        url_match = URL_REGEX.match(text)
        uri_type = getattr(url_match, 'group', lambda x: None)(1)

        uri = None

        if uri_type in ['playlist', 'track', 'album', 'artist']:
            try:
                track = getattr(multi_client.single_client, uri_type)(text)
                uri = track['uri']
            except SpotifyException:
                uri = None
        elif text.startswith('spotify:'):
            uri = text

        if uri:
            multi_client.add_to_queue(uri)
            bot.send_message(
                chat_id=update.message.chat_id,
                text=f'Added to queue: {uri}'
            )

    @classmethod
    def custom_handlers(cls):
        return (
            MessageHandler(Filters.text, cls.select),
        )


if __name__ == '__main__':
    ListenTogetherBot.run()
