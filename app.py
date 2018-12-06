# import queue
import os
# import threading
import time

import telegram
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
)

from authorization import _get_oauth
from telegram_app import RandomGenreBot


app = Flask(__name__)


PORT = os.environ.get('PORT', 5000)

bot = RandomGenreBot.bot()
# update_queue = queue.Queue()
dispatcher = telegram.ext.Dispatcher(bot, None, workers=0)
for handler in RandomGenreBot.handlers():
    dispatcher.add_handler(handler)


@app.route('/', methods=['POST'])
def index():
    return jsonify(status=200)


@app.route('/', methods=['GET'])
def redirect_to_bot():
    return redirect("https://telegram.me/random_genre_bot", code=302)


@app.route('/callback', methods=['GET'])
def callback():
    user = request.args.get('state')
    sp_oauth = _get_oauth(user)

    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return jsonify(status=200, token_expires=token_info['expires_at'])


@app.route('/hook/' + RandomGenreBot.TOKEN, methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    # update_queue.put(update)
    dispatcher.process_update(update)
    return "OK"


if __name__ == '__main__':

    # dispatcher_thread = threading.Thread(target=dispatcher.start)
    # dispatcher_thread.start()
    s = bot.set_webhook(
        "https://random-genre.herokuapp.com/hook/" + RandomGenreBot.TOKEN)
    if s:
        print("webhook setup ok")
    else:
        print("webhook setup failed")
    time.sleep(5)
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=True,
    )
