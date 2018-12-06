from flask import (
    Blueprint,
    jsonify,
    g,
    request,
)

import recast
from authorization import get_client_or_auth_url
from genres import Playlist

recast_routes = Blueprint('recast_routes', __name__)


@recast_routes.before_request
def get_client():
    if request.method == 'POST' or request.endpoint == 'test':
        client_or_url = get_client_or_auth_url('RECAST')
        if not isinstance(client_or_url, str):
            g.client = client_or_url
        else:
            return jsonify(
                status=200,
                replies=recast.reply.spotify_login(client_or_url)
            )


@recast_routes.before_request
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


def _get_choice():
    selection = g.memory['user_choice']
    choices = g.memory['choices']
    index = (
        selection.get('scalar') or
        selection.get('rank'))
    return choices[index - 1 if index > 0 else index]


@recast_routes.route('/recast/play', methods=['POST'])
def play_command():
    try:
        choice = Playlist(**_get_choice())
        g.client.start_playback(context_uri=choice.context_uri)
        response = recast.reply.playing(choice, g.memory)
    except (IndexError, KeyError):
        response = {'replies': [{
            'type': 'text',
            'content': 'That was not a valid choice!',
        }]}
    return jsonify(
        status=200,
        **response
    )


@recast_routes.route('/recast/genres', methods=['POST'])
def genres_command():
    playlists = Playlist.fetch_random(g.client)
    return jsonify(
        status=200,
        replies=recast.reply.buttons_for(playlists),
        conversation={
          'memory': {
            'choices': [{**pl} for pl in playlists]
          }
        }
    )


@recast_routes.route('/recast/pause', methods=['POST'])
def pause_command():
    g.client.pause_playback()
    return jsonify(status=200)


@recast_routes.route('/errors', methods=['POST'])
def errors():
    print(request.get_json())
    return jsonify(status=200)
