from random import shuffle

from genres import ALL_GENRES


def _random_iter(iterable):
    indices = list(range(len(iterable)))
    shuffle(indices)
    for i in indices:
        yield iterable[i]


class PlaylistNotFoundError(RuntimeError):
    """An error to be raised when a playlist for a genre wasn't found."""

    def __init__(self, genre):
        super().__init__('Playlist for {genre} could not be found!')


class Playlist:

    def __init__(self, sp_id, name=None, url=None, image_url=None):
        if not sp_id:
            self.found = False
        else:
            self.sp_id = sp_id
            self.name = name
            self.url = url
            self.image_url = image_url
            self.found = True

    def keys(self):
        return ['sp_id', 'name', 'url', 'image_url']

    def __getitem__(self, key):
        return self.__dict__[key]

    @property
    def context_uri(self):
        return f'spotify:user:thesoundsofspotify:playlist:{self.sp_id}'

    @classmethod
    def from_genre(cls, sp, genre):
        result = sp.search(
            f'The Sound of {genre.title()}', limit=1, type='playlist')
        items = result.get('playlists', {}).get('items')
        if not items:
            raise PlaylistNotFoundError(genre)
        pl = cls.from_item(items[0])
        pl.genre = genre
        return pl

    @classmethod
    def from_item(cls, item):
        sp_id = item.get('id')
        try:
            pl_attributes = {
                'name': item['name'],
                'url': item['external_urls']['spotify'],
                'image_url': item['images'][0]['url'],
            }
        except (KeyError, AttributeError, IndexError):
            pl_attributes = {}
        return cls(sp_id, **pl_attributes)

    @classmethod
    def fetch_random(cls, sp, count=3):
        choices = []
        random_iter = _random_iter(ALL_GENRES)
        for genre in random_iter:
            try:
                choices.append(Playlist.from_genre(sp, genre))
            except PlaylistNotFoundError:
                pass

            if len(choices) == count:
                return choices

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __str__(self):
        return self.__repr__()
