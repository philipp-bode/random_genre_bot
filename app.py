import os
from flask import Flask, jsonify, g, redirect, request
from random import sample
from spotipy import oauth2, Spotify

import recast
from genres import GENRES, play, Playlist

app = Flask(__name__)

scope = (
    'user-read-currently-playing '
    'user-modify-playback-state '
    'user-read-playback-state '
)

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
CACHE_PATH = f".cache-{os.getenv('SPOTIPY_USERNAME')}"


def _get_oauth():
    redirect_uri = f'{request.host_url}callback'

    return oauth2.SpotifyOAuth(
        CLIENT_ID, CLIENT_SECRET, redirect_uri,
        scope=scope, cache_path=CACHE_PATH
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
            g.top_intent = state['nlp']['intents'][0]['slug']
        except (IndexError, KeyError):
            g.top_intent = ''


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


def _get_choice(memory):
    selection = g.memory['user_choice']
    choices = g.memory['choices']
    index = (
        selection.get('scalar') or
        selection.get('rank'))
    return choices[index - 1 if index > 0 else index]


@app.route('/recast/play', methods=['POST'])
def play_command():
    try:
        choice = Playlist(**_get_choice(index))
        response = play(g.client, choice)
    except (IndexError, KeyError):
        response = {'replies': [{
            'type': 'text',
            'content': 'That was not a valid choice!',
        }]}
    return jsonify(
        status=200,
        **response
    )


@app.route('/recast/genres', methods=['POST'])
def genres_command():
    playlists = Playlist.fetch_random(g.client)
    return jsonify(
        status=200,
        replies=recast.buttons_for(playlists),
        conversation={
          'memory': {
            'choices': [{
                'p_id': pl.id,
                'url': pl.url,
            } for pl in playlists]
          }
        }
    )


@app.route('/recast/pause', methods=['POST'])
def pause_command():
    g.client.pause_playback()
    return jsonify(status=200)


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
