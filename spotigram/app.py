import multiprocessing

import telegram
from flask import (
    abort,
    Flask,
    jsonify,
    redirect,
    request,
)

from spotigram.authorization import retrieve_token_info


def user_link(user):
    return f'[{user}](https://open.spotify.com/user/{user})'


def _build_app_and_bot_for(bot_cls):
    app = Flask(__name__)

    bot = bot_cls.bot()
    update_queue = multiprocessing.Queue()

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
        if not token_info:
            abort(400, 'Request not valid. Try getting a new login link.')
        bot.send_message(
            chat_id=context['chat_id'],
            text=f"User {user_link(context['user_id'])} logged in.",
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return redirect("https://telegram.me/random_genre_bot", code=302)

    @app.route('/hook/' + bot_cls.TOKEN, methods=['POST'])
    def webhook():
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        update_queue.put(update)
        return "OK"

    return app, bot, update_queue
