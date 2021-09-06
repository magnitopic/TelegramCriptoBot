# TelegramCryptoBot

## About the proyect
This proyect goal is to have a telegram bot that gives updates, in real time, on Cypto and stock prices.

To do so I use Web Scarping to obtain the updated data. The source page is [Yahoo Finance](https://finance.yahoo.com/).

## Run the bot
Run the folowing command in your terminal to install de dependancies:
```bash
pip install -r requirements.txt
```
You'll have to rename *.env.example* to just *.env* and enter you bot token. 
>If you don't know how, [I have a video on the topic](https://youtu.be/h1QGky22b-k)

Finaly run *bot.py* with python
```bash
python bot.py
```