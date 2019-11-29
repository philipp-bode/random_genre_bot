import json
import random
from pathlib import Path


MODULE_PATH = Path(__file__).parent
PLAYLISTS_FILE = MODULE_PATH / 'genre_playlists.json'

PLAYLIST_TAG = 'spotify:playlist:'

with open(PLAYLISTS_FILE, 'r') as f:
    PLAYLISTS = json.load(f)

PLAYLISTS_BY_URI = {
    uri: (pl_type, genre)
    for genre, outer_v in PLAYLISTS.items()
    for pl_type, uri in outer_v.items()
}


class GenrePlaylist:

    def __init__(self, uri, genre=None, pl_type=None):
        self._uri = uri

        if not genre or not pl_type:
            self.pl_type, self.genre = PLAYLISTS_BY_URI[uri]
        else:
            self.genre = genre
            self.pl_type = pl_type

    @property
    def name(self):
        return f'The {self.pl_type} of {self.genre}'

    @property
    def uri(self):
        return f'{PLAYLIST_TAG}{self._uri}'

    @property
    def link(self):
        return f'https://open.spotify.com/playlist/{self._uri}'

    def to_dict(self):
        return {
            'genre': self.genre,
            'uri': self._uri,
            'pl_type': self.pl_type,
        }

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'


def random_genres(k=3):
    genres = random.sample(list(PLAYLISTS), 3)
    choices = {
        genre: random.choice(list(PLAYLISTS[genre].items()))
        for genre in genres
    }
    return [
        GenrePlaylist(uri, genre, pl_type)
        for (genre, (pl_type, uri)) in choices.items()
    ]


__all__ = [
    'random_genres',
    'GenrePlaylist',
]
