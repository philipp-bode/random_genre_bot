import os
import multiprocessing

import telegram
from flask import Flask, jsonify, g, redirect, request
from spotipy import oauth2, Spotify

import recast
from telegram_app import RandomGenreBot
from genres import Playlist


app = Flask(__name__)

scope = (
    'user-read-currently-playing '
    'user-modify-playback-state '
    'user-read-playback-state '
)

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
CACHE_PATH = '.cache-{user}'

bot = RandomGenreBot.bot()
update_queue = multiprocessing.Queue()
dp = telegram.ext.Dispatcher(bot, update_queue)


def _get_oauth(user=None):
    cache_path = CACHE_PATH.format(user=user)
    redirect_uri = f'{request.host_url}callback'

    return oauth2.SpotifyOAuth(
        CLIENT_ID, CLIENT_SECRET, redirect_uri,
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
            g.top_intent = state['nlp']['intents'][0]['slug']
        except (IndexError, KeyError):
            g.top_intent = ''


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
        g.client.start_playback(context_uri=choice.context_uri)
        response = recast.playing(choice, g.memory)
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
            'choices': [{**pl} for pl in playlists]
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
    user = request.args.get('user')
    sp_oauth = _get_oauth(user)
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    else:
        return jsonify(status=200, token_expires=token_info['expires_at'])


@app.route('/callback', methods=['GET'])
def callback():
    user = request.args.get('state')
    sp_oauth = _get_oauth(user)

    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return jsonify(status=200, token_expires=token_info['expires_at'])
    # return jsonify(status=200)


@app.route('/hook/' + RandomGenreBot.TOKEN, methods=['GET', 'POST'])
def webhook():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True))

        dp.process_update(update)
        update_queue.put(update)
        return "OK"
    else:
        return redirect("https://telegram.me/random_genre_bot", code=302)


if __name__ == '__main__':

    dispatcher_process = multiprocessing.Process(target=dp.start)
    dispatcher_process.start()
    app.run(debug=True)

    s = bot.set_webhook(
        "https://random-genre.herokuapp.com/hook/" + RandomGenreBot.TOKEN)
    if s:
        print("webhook setup ok")
    else:
        print("webhook setup failed")
