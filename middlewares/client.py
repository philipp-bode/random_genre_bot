import falcon
from spotipy import oauth2, Spotify


class SpotifyClientMiddleware:

    def __init__(self, client_id, client_secret, scope):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self._oauth = None

    def process_request(self, req: falcon.Request, resp: falcon.Response):

        if not self._oauth:
            self._oauth = oauth2.SpotifyOAuth(
                self.client_id,
                self.client_secret,
                f'{req.netloc}/callback',
                scope=self.scope,
                cache_path='.token-cache'
            )

        token_info = self._oauth.get_cached_token()

        if not token_info:
            auth_url = self._oauth.get_authorize_url()
            raise falcon.HTTPMovedPermanently(auth_url)
        else:
            req.client = Spotify(auth=token_info['access_token'])
