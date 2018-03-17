import falcon
import os
from spotipy import oauth2, Spotify

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
CACHE_PATH = f".cache-{os.getenv('SPOTIPY_USERNAME')}"

SCOPE = (
    'user-read-currently-playing '
    'user-modify-playback-state '
    'user-read-playback-state '
)


def get_oauth(req):
    redirect_uri = f'{req.netloc}/callback'

    return oauth2.SpotifyOAuth(
        CLIENT_ID, CLIENT_SECRET, redirect_uri,
        scope=SCOPE, cache_path=CACHE_PATH
    )


def get_client(req):
    sp_oauth = get_oauth()
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        raise falcon.HTTPMovedPermanently(auth_url)
    else:
        req.client = Spotify(auth=token_info['access_token'])
