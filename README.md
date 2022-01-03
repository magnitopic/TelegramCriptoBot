# TelegramCryptoBot

## About the proyect

Codebase for a Telegram bot that gives price updates on stocks and cryptos. Can also set daily reminders on an assets price at an especific time.

To get the asset data I use Web Scraping. The source page is [Yahoo Finance](https://finance.yahoo.com/).

## Run the bot

Run the following command in your terminal to install de dependencies:

```bash
pip install -r requirements.txt
```

You'll have to rename _.env.example_ to just _.env_ and enter you bot token.

> If you don't know how to get a TOKEN, [I have a video on the topic](https://youtu.be/h1QGky22b-k)

Finaly run _bot.py_ with python.

```bash
python bot.py
```
