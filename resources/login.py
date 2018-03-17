import falcon
import ujson

from resources.helpers import get_oauth


class LoginResource:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = self.client_secret

    def on_get(self, req, resp):
        sp_oauth = get_oauth(req)
        token_info = sp_oauth.get_cached_token()

        if not token_info:
            auth_url = sp_oauth.get_authorize_url()
            raise falcon.HTTPMovedPermanently(auth_url)
        else:
            resp.status = 200
            resp.body = ujson.dumps({
                'token_expires': token_info['expires_at']
            })


class CallbackResource:

    def on_get(self, req, resp):
        sp_oauth = get_oauth(req)
        code = req.params.get('code')
        token_info = sp_oauth.get_access_token(code)
        resp.status = 200
        resp.body = ujson.dumps({
            'token_expires': token_info['expires_at']
        })
