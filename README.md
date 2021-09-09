# TelegramCryptoBot

## About the proyect
This project goal is to have a telegram bot that gives updates, in real time, on Crypto and stock prices.

To do so I use Web Scraping to obtain the updated data. The source page is [Yahoo Finance](https://finance.yahoo.com/).

## Run the bot
Run the following command in your terminal to install de dependencies:
```bash
pip install -r requirements.txt
```
You'll have to rename *.env.example* to just *.env* and enter you bot token. 
> If you don't know how to get a TOKEN, [I have a video on the topic](https://youtu.be/h1QGky22b-k)

Finaly run *bot.py* with python.
```bash
python bot.py
```