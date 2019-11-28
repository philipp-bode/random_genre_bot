import json
import jwt
import os
from datetime import (
    datetime,
    timedelta,
)

from spotipy import oauth2, Spotify
from spotipy.oauth2 import is_token_expired
from spotigram.token_cache import RedisTokenCache

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

CACHE = RedisTokenCache(os.getenv('REDIS_URL', 'localhost'))

API_LOCATION = os.getenv('API_LOCATION', 'http://localhost:5000')
REDIRECT_URI = f'{API_LOCATION}/callback'

SECRET_KEY = os.getenv('SECRET_KEY')

SCOPE = (
    'user-read-currently-playing '
    'user-modify-playback-state '
    'user-read-playback-state '
)


def _decode_jwt(token):
    claims = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return claims['chat_id']


def _encode_jwt(chat_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
        'iat': datetime.utcnow(),
        'chat_id': chat_id,
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    ).decode('utf-8')


def _no_cache_oauth():
    return oauth2.SpotifyOAuth(
        CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
        scope=SCOPE, cache_path=None
    )


def _cache_token_info(chat_id, token_info):
    client = Spotify(auth=token_info['access_token'])
    user_id = client.current_user()['id']

    CACHE.set(chat_id, user_id, token_info)

    return user_id


def retrieve_token_info(state, code):

    chat_id = _decode_jwt(state)
    sp_oauth = _no_cache_oauth()
    token_info = sp_oauth.get_access_token(code)

    user_id = _cache_token_info(chat_id, token_info)
    return token_info, {'chat_id': chat_id, 'user_id': user_id}


def get_clients_or_auth_url(
    chat_id: str,
    force_reauth: bool = False
):

    token_infos = [
        json.loads(t)
        for t in CACHE.get_tokens(chat_id)
    ]

    if not token_infos or force_reauth:
        if token_infos:
            CACHE.clear(chat_id)

        sp_oauth = _no_cache_oauth()
        state = _encode_jwt(chat_id)
        auth_url = f'{sp_oauth.get_authorize_url()}&state={state}'
        return None, auth_url
    else:
        non_expired_tokens = []
        for token_info in token_infos:
            if is_token_expired(token_info):
                sp_oauth = _no_cache_oauth()
                non_expired = sp_oauth.refresh_access_token(
                    token_info['refresh_token'])
                _cache_token_info(chat_id, non_expired)
            else:
                non_expired = token_info

            non_expired_tokens.append(non_expired)

        clients = [
            Spotify(auth=token_info['access_token'])
            for token_info in non_expired_tokens
        ]
        return clients, None
