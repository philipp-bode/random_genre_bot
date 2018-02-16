import json
import os
from flask import Flask, jsonify, redirect, request
from random import sample
from spotipy import oauth2

import recast
from genres import GENRES

app = Flask(__name__)

scope = (
    'user-read-currently-playing '
    'user-modify-playback-state '
    'user-read-playback-state '
)


def _get_oauth():
    client_id = os.getenv('SPOTIPY_CLIENT_ID')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    # redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
    redirect_uri = f'{request.host_url}callback'
    username = os.getenv('SPOTIPY_USERNAME')

    cache_path = f'.cache-{username}'
    return oauth2.SpotifyOAuth(
        client_id, client_secret, redirect_uri,
        scope=scope, cache_path=cache_path
    )


@app.route('/genres', methods=['GET'])
def test():
    genres = {f'choice{i + 1}': v for i, v in enumerate(sample(GENRES, 3))}
    return jsonify(
        status=200,
        replies=[recast.buttons_for(genres)],
        conversation={
          'memory': {
            'choices': genres
          }
        }
    )


@app.route('/', methods=['POST'])
def index():
    state = request.get_json()
    print(state)
    skill = state['conversation']['skill']
    if skill == 'display_genres':
        genres = {f'choice{i + 1}': v for i, v in enumerate(sample(GENRES, 3))}
        return jsonify(
            status=200,
            replies=[recast.buttons_for(genres)],
            conversation={
              'memory': {
                'choices': genres
              }
            }
        )


@app.route('/errors', methods=['POST'])
def errors():
    print(json.loads(request.get_data()))
    return jsonify(status=200)


@app.route('/login', methods=['GET'])
def login():
    sp_oauth = _get_oauth()
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)


@app.route('/callback', methods=['GET'])
def callback():
    sp_oauth = _get_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return jsonify(status=200, token_expires=token_info['expires_at'])


if __name__ == '__main__':
    app.run(use_reloader=True)
