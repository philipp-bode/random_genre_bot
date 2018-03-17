import os

import falcon
from wsgiref.simple_server import make_server

from resources import LoginResource, CallbackResource
from middlewares.client import SpotifyClientMiddleware

class SpotifyApp:

    def __init__(self, server_address='0.0.0.0', server_port='8080',
                 middleware=[], db_config={}):
        self.server_address = server_address
        self.server_port = server_port

    def create(self):
        app = falcon.API(middleware=[SpotifyClientMiddleware(
            client_id=os.getenv('SPOTIPY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
            scope=(
                'user-read-currently-playing '
                'user-modify-playback-state '
                'user-read-playback-state '
            )
        )])
        app.add_route('/login', LoginResource())
        app.add_route('/callback', CallbackResource())
        app.add_route('/playback', PlaybackResource())
        app.add_route('/genres', GenresResource())

        return app

    def start(self):  # pragma: no cover
        app = self.create()
        httpd = make_server(self.server_address, self.server_port, app)
        httpd.serve_forever()


@app.before_request


@app.before_request



@app.route('/recast/play', methods=['POST'])
def play_command():



@app.route('/recast/genres', methods=['POST'])
def genres_command():


@app.route('/recast/pause', methods=['POST'])
def pause_command():
    g.client.pause_playback()
    return jsonify(status=200)



if __name__ == '__main__':
    app.run(debug=True)
