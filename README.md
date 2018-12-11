# random\_genre\_bot

Bored of listening to your same ol' music?
Get some random genre playlist suggestions from [The Sounds of Spotify](https://open.spotify.com/user/thesoundsofspotify?si=TXC6adPHRuGV7zrnn4rGFw)'s collection.

The bot is deployed on Heroku and available at [@random\_genre\_bot](https://telegram.me/random_genre_bot). You may have to wait a few seconds on startup.

## Development

To start the bot locally, you will need to export your Spotify API credentials and your Telegram bot token to the environment.
Take a look at [env.sh.default](./env.sh.default) to see what you should source.

For development purposes, the bot can be started in polling mode with `python telegram_app.py`.
To receive authorization requests, start the Flask server with `python app.py` in parallel.

## Authorization
This bot serves as a proof of concept on how to link Spotify access tokens to telegram chats.
To authorize, the user is redirected to start the `client_credentials` flow.

Currently, the OAuth2 `state` is set to the Telegram chat id to reassociate the incoming token.
As this would allow someone to attach own tokens to arbitrary chats, the next step would be to handle this with a locally stored nonce.
