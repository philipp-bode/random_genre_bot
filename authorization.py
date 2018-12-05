import os

from spotipy import oauth2, Spotify

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
CACHE_PATH = ".cache-{user}"

API_LOCATION = os.getenv('API_LOCATION', 'http://localhost:5000')

SCOPE = (
    'user-read-currently-playing '
    'user-modify-playback-state '
    'user-read-playback-state '
)


def _get_oauth(user):
    cache_path = CACHE_PATH.format(user=user)
    redirect_uri = f'{API_LOCATION}/callback'

    return oauth2.SpotifyOAuth(
        CLIENT_ID, CLIENT_SECRET, redirect_uri,
        scope=SCOPE, cache_path=cache_path
    )


def get_client_or_auth_url(user, force_reauth=False):
    sp_oauth = _get_oauth(user)
    token_info = sp_oauth.get_cached_token()
    if not token_info or force_reauth:
        return f'{sp_oauth.get_authorize_url()}&state={user}'
    else:
        return Spotify(auth=token_info['access_token'])
