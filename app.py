import json
import os
from flask import Flask, jsonify, g, redirect, request
from random import sample
from spotipy import oauth2, Spotify

import recast
from genres import GENRES, play

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


@app.before_request
def get_client():
    if request.method == 'POST' or request.endpoint == 'test':
        sp_oauth = _get_oauth()
        token_info = sp_oauth.get_cached_token()
        if not token_info:
            return jsonify(
                status=200,
                replies=recast.spotify_login(sp_oauth.get_authorize_url())
            )
        else:
            g.client = Spotify(auth=token_info['access_token'])


@app.before_request
def attach_nlp():
    if request.method == 'POST':
        state = request.get_json()
        print(state)
        g.skill = state['conversation']['skill']
        g.memory = state['conversation']['memory']
        try:
            g.top_intent = g.memory['nlp']['intents'][0]['slug']
        except (IndexError, KeyError):
            g.top_intent = ''


def _no_match_response():
    return jsonify(
        status=200,
        replies=[{
            'type': 'text',
            'content': (
                f"I don't know what to say. :("
                f"You want {g.top_intent} while we're in {g.skill}?"
            ),
        }]
    )


@app.route('/genres', methods=['GET'])
def test():
    genres = {str(i + 1): v for i, v in enumerate(sample(GENRES, 3))}

    return jsonify(
        status=200,
        replies=[recast.list_for(g.client, genres)],
        conversation={
          'memory': {
            'choices': genres
          }
        }
    )


@app.route('/recast/play', methods=['POST'])
def play_command():
    if (
        g.top_intent == 'select' or
        g.skill == 'get_genre_response'
    ):
        user_choice = g.memory['user_choice']['raw']
        genre = g.memory['choices'][user_choice]
        replies = play(g.client, genre)

        return jsonify(
            status=200,
            replies=replies,
        )

    return _no_match_response()


@app.route('/recast/genres', methods=['POST'])
def genres_command():
    if (
        g.top_intent == 'play_random' or
        g.skill == 'display_genres'
    ):
        genres = {str(i + 1): v for i, v in enumerate(sample(GENRES, 3))}
        return jsonify(
            status=200,
            replies=[recast.list_for(g.client, genres)],
            conversation={
              'memory': {
                'choices': genres
              }
            }
        )

    return _no_match_response()


@app.route('/', methods=['POST'])
def index():
    return jsonify(status=200)


@app.route('/errors', methods=['POST'])
def errors():
    print(request.get_json())
    return jsonify(status=200)


@app.route('/login', methods=['GET'])
def login():
    sp_oauth = _get_oauth()
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    else:
        return jsonify(status=200, token_expires=token_info['expires_at'])


@app.route('/callback', methods=['GET'])
def callback():
    sp_oauth = _get_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return jsonify(status=200, token_expires=token_info['expires_at'])


if __name__ == '__main__':
    app.run(debug=True)
