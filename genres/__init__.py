import json
import random
from pathlib import Path


MODULE_PATH = Path(__file__).parent
PLAYLISTS_FILE = MODULE_PATH / 'genre_playlists.json'

PLAYLIST_TAG = 'spotify:playlist:'

with open(PLAYLISTS_FILE, 'r') as f:
    PLAYLISTS = json.load(f)


class GenrePlaylist:

    def __init__(self, name, pl_type, uri):
        self.name = f'The {pl_type} of {name}'
        self.uri = f'{PLAYLIST_TAG}{uri}'
        self.link = f'https://open.spotify.com/playlist/{uri}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'


def random_genres(k=3):
    genre_names = random.sample(list(PLAYLISTS), 3)
    choices = {
        genre_name: random.choice(list(PLAYLISTS[genre_name].items()))
        for genre_name in genre_names
    }
    return [
        GenrePlaylist(name, pl_type, uri)
        for (name, (pl_type, uri)) in choices.items()
    ]


__all__ = [
    'random_genres',
    'GenrePlaylist',
]
