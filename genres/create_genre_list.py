import json
import re

from genres import PLAYLISTS_FILE, PLAYLIST_TAG

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable):
        return iterable

try:
    import iso3166
    alpha2_country_codes = tuple(
        f' {code}' for code in iso3166.countries_by_alpha2.keys())
except ImportError:
    alpha2_country_codes = tuple()


PLAYLIST_REGEX = re.compile('^The (Sound|Pulse|Edge) of ')

LIMIT = 50


def _fetch_playlist_batches(client, genres, user):
    playlists = client.user_playlists(user)
    previous_genre_name = ''
    for _ in tqdm(range(LIMIT, playlists['total'], LIMIT)):
        for playlist in playlists['items']:
            name = playlist['name']
            match = PLAYLIST_REGEX.match(name)
            if match:
                genre_name = re.sub(PLAYLIST_REGEX, '', name)

                # Skip city and country playlists from thesoundofspotify
                if (
                    previous_genre_name and
                    (previous_genre_name > genre_name)
                    and genre_name.endswith(alpha2_country_codes)
                ):
                    return

                playlist_type = match.group(1)
                genre_entry = genres.setdefault(genre_name, {})
                genre_entry[playlist_type] = playlist['uri'].replace(
                    PLAYLIST_TAG, '')

                previous_genre_name = genre_name

        playlists = client.next(playlists)


def create_genre_file(client):
    genres = {}

    for user in ('thesoundsofspotify', 'particledetector'):
        print(f'Fetching for {user}...')
        _fetch_playlist_batches(client, genres, user)

    with open(PLAYLISTS_FILE, 'w') as f:
        json.dump(genres, f, indent=2)
