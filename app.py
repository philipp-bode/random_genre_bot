import multiprocessing
import os
import time

import telegram
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
)

from authorization import retrieve_token_info
from bots import RandomGenreBot


app = Flask(__name__)


PORT = os.environ.get('PORT', 5000)
API_LOCATION = os.environ.get('API_LOCATION')

BOT_CLASS = RandomGenreBot

bot = BOT_CLASS.bot()
update_queue = multiprocessing.Queue()
dispatcher = telegram.ext.Dispatcher(bot, update_queue)
for handler in BOT_CLASS.handlers():
    dispatcher.add_handler(handler)


@app.route('/', methods=['POST'])
def index():
    return jsonify(status=200)


@app.route('/', methods=['GET'])
def redirect_to_bot():
    return redirect("https://telegram.me/random_genre_bot", code=302)


@app.route('/callback', methods=['GET'])
def callback():
    token_info, context = retrieve_token_info(
        request.args.get('state'),
        request.args.get('code')
    )
    bot.send_message(
        chat_id=context['chat_id'],
        text=f"User '{context['user_id']}' synced."
    )
    return redirect("https://telegram.me/random_genre_bot", code=302)


@app.route('/hook/' + BOT_CLASS.TOKEN, methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    update_queue.put(update)
    return "OK"


if __name__ == '__main__':

    if API_LOCATION:
        dispatcher_process = multiprocessing.Process(target=dispatcher.start)
        dispatcher_process.start()
        s = bot.set_webhook(
            f'{API_LOCATION}/hook/{BOT_CLASS.TOKEN}')
        time.sleep(5)
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=not bool(API_LOCATION),
    )
