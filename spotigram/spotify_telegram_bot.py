import os
import multiprocessing
import time
from random import random

import telegram
from telegram.ext import (
    CommandHandler,
    Updater,
)

from spotigram import spotify_multi_action
from spotigram.app import _build_app_and_bot_for, user_link
from spotigram.authorization import (
    CACHE,
    get_clients_or_auth_url,
)

API_LOCATION = os.environ.get('API_LOCATION')


class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class SpotigramBot:

    _TOKEN = None

    @classproperty
    def TOKEN(cls):
        if not cls._TOKEN:
            try:
                cls._TOKEN = os.environ['TELEGRAM_TOKEN']
            except KeyError:
                raise RuntimeError(
                    f'Please define _TOKEN for {cls.__name__} '
                    ' or set TELEGRAM_TOKEN in your environment.'
                )
        return cls._TOKEN

    @classmethod
    def bot(cls):
        return telegram.Bot(cls.TOKEN)

    @classmethod
    def run(cls):
        app, _, _ = _build_app_and_bot_for(cls)

        updater = Updater(token=cls.TOKEN)
        dispatcher = updater.dispatcher
        for handler in cls.handlers():
            dispatcher.add_handler(handler)

        process = multiprocessing.Process(
            target=app.run)
        process.start()
        updater.start_polling()

    @classmethod
    def create_app(cls):
        app, bot, update_queue = _build_app_and_bot_for(cls)
        dispatcher = telegram.ext.Dispatcher(bot, update_queue)

        for handler in cls.handlers():
            dispatcher.add_handler(handler)

        process = multiprocessing.Process(
            target=dispatcher.start)
        process.start()

        # To avoid concurrent calls when starting multiple workers,
        # retry with random jitter.
        webhook_set = False
        while not webhook_set:
            try:
                webhook_set = bot.set_webhook(
                    f'{API_LOCATION}/hook/{cls.TOKEN}')
            except telegram.error.RetryAfter as e:
                time.sleep(e.retry_after + random() * 5)

        return app

    @staticmethod
    def force_authorization(bot, update):
        chat_id = update.message.chat_id
        _, auth_url = get_clients_or_auth_url(
            chat_id, force_reauth=True)
        bot.send_message(
            chat_id=chat_id,
            text=f'[Log in with your Spotify account]({auth_url})',
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )

    @staticmethod
    def list_users(bot, update):
        chat_id = update.message.chat_id
        users_markdown = '\n'.join([
            user_link(user)
            for user in CACHE.keys_for(chat_id)
        ])
        bot.send_message(
            chat_id=chat_id,
            text=(
                f'Authenticated users:\n{users_markdown}'
                if users_markdown
                else 'No one logged in :('
            ),
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )

    @staticmethod
    def logout(bot, update, args):
        chat_id = update.message.chat_id
        try:
            user = args.pop(0)
            logged_out = CACHE.clear(chat_id, user)
            bot.send_message(
                chat_id=chat_id,
                text=(
                    f'User {user_link(user)} logged out.' if logged_out
                    else f'No user "{user}" logged in.'
                ),
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
        except IndexError:
            bot.send_message(
                chat_id=chat_id,
                text='Which user should I log out?',
            )

    @staticmethod
    def logout_all(bot, update):
        chat_id = update.message.chat_id
        CACHE.clear(chat_id)
        bot.send_message(chat_id=chat_id, text='Logged out all users.')

    @staticmethod
    @spotify_multi_action
    def pause(multi_client, bot, update):
        multi_client.pause_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='I paused your playback.')

    @staticmethod
    @spotify_multi_action
    def play(multi_client, bot, update):
        multi_client.start_playback()
        bot.send_message(
            chat_id=update.message.chat_id, text='Playing...')

    @staticmethod
    @spotify_multi_action
    def next_track(multi_client, bot, update):
        multi_client.next_track()
        bot.send_message(
            chat_id=update.message.chat_id, text='Next song...')

    @classmethod
    def custom_handlers(cls):
        return []

    @classmethod
    def handlers(cls):
        return (
            CommandHandler('login', cls.force_authorization),
            CommandHandler('users', cls.list_users),
            CommandHandler('logout', cls.logout, pass_args=True),
            CommandHandler('logout_all', cls.logout_all),
            CommandHandler('start', cls.force_authorization),
            CommandHandler('pause', cls.pause),
            CommandHandler('play', cls.play),
            CommandHandler('next', cls.next_track),
            *cls.custom_handlers(),
        )
