import ujson

import recast
from genres import Playlist


class PlayResource:

    def on_post(self, req, resp):
        print(req.media)

        memory = req.media['conversation']['memory']

        try:
            choice = Playlist(**self._get_choice(memory))
            req.client.start_playback(context_uri=choice.context_uri)
            response = recast.playing(choice, memory)
        except (IndexError, KeyError):
            resp.body = ujson.dumps({'replies': [{
                'type': 'text',
                'content': 'That was not a valid choice!',
            }]})
        else:
            resp.status = 200
            resp.body = ujson.dumps(response)

    @staticmethod
    def _get_choice(memory):
        selection = memory['user_choice']
        choices = memory['choices']
        index = (
            selection.get('scalar') or
            selection.get('rank'))
        return choices[index - 1 if index > 0 else index]


class GenresResources:
    def on_post(self, req, resp):
        playlists = Playlist.fetch_random(req.client)
        resp.status = 200
        resp.body = ujson.dumps({
            'replies': recast.buttons_for(playlists),
            'conversation': {
              'memory': {
                'choices': [{**pl} for pl in playlists]
              }
            }
        })


class StopResource:
    def on_post(self, req, resp):
        req.client.pause_playback()
        resp.status = 200
