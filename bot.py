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
    # It first cheks if it's a crypto. Yahoo finance places -USD at the end of the URL for cryptos
    price = web_scraping(asset+'-usd')
    if price != None:
        format_result = 'Current '+asset.upper() + ' price is '+price.text+" USD"
        return format_result

    # If it isen't a crypto
    price = web_scraping(asset)
    if price != None:
        format_result = 'Current ' + asset.upper() + ' price is ' + price.text + " USD"
        return format_result

    else:
        return "Asset does not exist."


def respondSchedule(asset, ID):
    print(f"{asset.upper()} reminder")
    crypto_bot.send_message(ID, get_price(asset))


def main():
    keep_alive()
    new_offset, new_reminder, canceling_reminder = 0, False, False
    print('Bot now runing...')
    reminders = {}

    while True:
        schedule.run_pending()
        all_updates = crypto_bot.get_updates(new_offset)

        # If there are any new updates
        if len(all_updates) > 0:
            for current_update in all_updates:
                first_update_id = current_update['update_id']

                # If the there is a message and text in the current update the code runs
                if 'message' in current_update and 'text' in current_update['message']:
                    # The message they sent
                    first_chat_text = current_update['message']['text']
                    # The id of the user that sent the message
                    first_chat_id = current_update['message']['chat']['id']
                    # User name of the user
                    first_chat_name = current_update['message']['from']['first_name']

                    # We need to add all users to the reminders dictionary or we'll get an error later
                    if first_chat_id not in reminders.keys():
                        reminders[first_chat_id] = []

                    # We need a boolean to cheek if the incoming messages are meant for the /set_reminder command
                    if new_reminder:
                        # To set a reminder we need two values for our variables, the asset and the time
                        if first_chat_text.lower() == "exit":
                            new_reminder = False
                            crypto_bot.send_message(
                                first_chat_id, "Reminder canceled")
                        elif asset == None:
                            if get_price(first_chat_text) != "Asset does not exist.":
                                asset = first_chat_text.upper()
                                crypto_bot.send_message(
                                    first_chat_id, 'At what time should I remind you? (24h format "XX:XX")')
                            else:
                                crypto_bot.send_message(
                                    first_chat_id, 'Invalid asset. Try again.(exit to cancel)')
                        elif time == None and asset != None:
                            # I use try except to see if the user is giving an invalid time
                            # I give the message as an argument to the schedule library
                            # If it returns an error I tell the user it's an invalid input
                            try:
                                #reminder = schedule.every().day.at(first_chat_text).do(respondSchedule, asset=asset, ID=first_chat_id)
                                reminder = schedule.every().minute.do(
                                    respondSchedule, asset=asset, ID=first_chat_id)
                            except:
                                crypto_bot.send_message(
                                    first_chat_id, "Invalid format. Try Again! (exit to cancel)")
                            else:
                                # If the user is not in the list he gets added
                                reminders[first_chat_id].append(
                                    [reminder, f"{asset} reminder at {first_chat_text}"])
                                new_reminder = False
                                crypto_bot.send_message(
                                    first_chat_id, "Reminder set! I'll give you "+asset+"'s price every day at "+first_chat_text)
                                print("_"*10)
                                print(
                                    f"New reminder:\nAsset: {asset}\nTime: {first_chat_text}")
                    elif canceling_reminder:
                        if first_chat_text.lower() != "exit":
                            try:
                                option = int(first_chat_text)
                                if option <= 0 or option > len(reminders[first_chat_id]):
                                    raise ValueError('ERROR')
                            except:
                                crypto_bot.send_message(
                                    first_chat_id, "Invalid format. Try Again! (exit to cancel)")
                            else:
                                # The job the user selects gets canceled
                                schedule.cancel_job(
                                    reminders[first_chat_id][option-1][0])
                                # Item gets deleted form the dictionary
                                reminders[first_chat_id].pop(option-1)
                                crypto_bot.send_message(
                                    first_chat_id, "Reminder canceled.")
                                canceling_reminder = False
                        else:
                            crypto_bot.send_message(
                                first_chat_id, "Ok, no reminder was canceled.")
                            canceling_reminder = False

                    elif '/cancel_reminder' in first_chat_text:
                        if len(reminders[first_chat_id]) != 0:
                            text = "Send the number of the reminder you what to cancel.\nYour reminders:"
                            for i in range(len(reminders[first_chat_id])):
                                text += f"\n\t {i+1}. " + \
                                    reminders[first_chat_id][i][1]
                            crypto_bot.send_message(first_chat_id, text)
                            canceling_reminder = True
                        else:
                            crypto_bot.send_message(
                                first_chat_id, "You don't have any reminders created.")
                    # We need to cheek for the /set_reminder so that it dosen't get looked up like an asset
                    elif '/set_reminder' in first_chat_text:
                        crypto_bot.send_message(
                            first_chat_id, "What asset should I send you updates on?(No need to add /)")
                        new_reminder = True
                        asset = None
                        time = None
                   # If the message has a / in front we cheeck it as an asset price. Except for /help and /start
                    elif '/' in first_chat_text and first_chat_text != '/help' and first_chat_text != '/start':
                        crypto_bot.send_message(
                            first_chat_id, get_price(first_chat_text.lstrip("/")))
                        print("_"*10)
                        print(first_chat_text.upper().lstrip("/"))
                # After every update has been procesed we can pass on to the next one
                new_offset = first_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
