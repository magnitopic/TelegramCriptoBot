# -*- coding: UTF8 -*-
# Crypro bot
import os
import requests
import schedule
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
from webServer import keep_alive


class BotHandler:
    def __init__(self, token):
        self.__token = token
        #url = "https://api.telegram.org/bot<token>/"
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=0, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_first_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[0]
        else:
            last_update = None

        return last_update


# We load the dotenv library
load_dotenv(find_dotenv())


# When using .env file use:
# os.getenv('TOKEN')
token = os.environ['TOKEN']  # Your bot's TOKEN
crypto_bot = BotHandler(token)


def web_scraping(url):
    url = requests.get('https://finance.yahoo.com/quote/'+url.upper())
    soup = BeautifulSoup(url.content, 'html.parser')
    result = soup.find(
        "fin-streamer", {'class': "Fw(b) Fz(36px) Mb(-4px) D(ib)"})
    return result


# Gets the requested asset and looks it up
def get_price(asset):
    print(asset.upper())
    print("¨"*10)
    # It first cheks if it's a crypto. Yahoo finance places -USD at the end of the URL for cryptos
    price = web_scraping(asset+'-usd')
    if price != None:
        format_result = 'Current '+asset.upper() + \
            ' price is '+price.text+" USD"
        return format_result

    # If it isen't a crypto
    price = web_scraping(asset)
    if price != None:
        format_result = 'Current ' + asset.upper() + ' price is ' + price.text + " USD"
        return format_result

    else:
        return "Asset does not exist."


def respondSchedule(asset, ID):
    crypto_bot.send_message(ID, get_price(asset))


def main():
    keep_alive()
    new_offset, new_program_update = 0, False
    print('Bot now runing...')

    while True:
        schedule.run_pending()
        all_updates = crypto_bot.get_updates(new_offset)

        # If there are any new updates
        if len(all_updates) > 0:
            for current_update in all_updates:
                first_update_id = current_update['update_id']

                # This line cheeks if the current_update doesn't have a message or if the message dosen't have text. If so it discards it
                if 'message' not in current_update or 'text' not in current_update['message']:
                    new_offset = first_update_id + 1
                # Else, it awsers the message
                else:
                    first_chat_text = current_update['message']['text']
                    first_chat_id = current_update['message']['chat']['id']
                    first_chat_name = current_update['message']['from']['first_name']
                    # We need a boolean to cheek if the incoming messages are meant for the /set_reminder command
                    if new_program_update:
                        # To set a reminder we need two values for our variables, the asset and the time
                        if first_chat_text.lower() == "exit":
                            new_program_update = False
                            crypto_bot.send_message(
                                first_chat_id, "Reminder canceled")
                            new_offset = first_update_id + 1
                        elif asset == None:
                            if get_price(first_chat_text) != "Asset does not exist.":
                                asset = first_chat_text
                                new_offset = first_update_id + 1
                                crypto_bot.send_message(
                                    first_chat_id, 'At what time should I remind you? (24h format "XX:XX")')
                            else:
                                crypto_bot.send_message(
                                    first_chat_id, 'Invalid asset. Try again.(exit to cancel)')
                                new_offset = first_update_id + 1
                        elif time == None and asset != None:
                            # I use try except to see if the user is giving an invalid time
                            # I give the message as an argument to the schedule library
                            # If it returns an error I tell the user it's an invalid input
                            try:
                                schedule.every().day.at(first_chat_text).do(
                                    respondSchedule, asset=asset, ID=first_chat_id)
                            except:
                                crypto_bot.send_message(
                                    first_chat_id, "Invalid format. Try Again! (exit to cancel)")
                                new_offset = first_update_id + 1
                            else:
                                time = first_chat_text
                                new_offset = first_update_id + 1
                                new_program_update = False
                                crypto_bot.send_message(
                                    first_chat_id, "Reminder set! I'll give you "+asset+" price every day at "+time)
                                print("Asset: "+asset)
                                print("Time: "+time)
                    # We need to cheek for the /set_reminder so that it dosen't get looked up like an asset
                    elif '/set_reminder' in first_chat_text:
                        crypto_bot.send_message(
                            first_chat_id, "What asset should I send you updates on?(No need to add /)")
                        new_offset = first_update_id + 1
                        new_program_update = True
                        asset = None
                        time = None

                   # /help and /start are special commands the bot uses
                    elif '/' in first_chat_text and first_chat_text != '/help' and first_chat_text != '/start':
                        word = first_chat_text.split()
                        for i in range(len(word)):
                            if '/' in word[i]:
                                crypto_bot.send_message(
                                    first_chat_id, get_price(word[i].lstrip("/")))
                                new_offset = first_update_id + 1
                    # We ignore any messages that don't have a / in front
                    else:
                        new_offset = first_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
