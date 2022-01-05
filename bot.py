# -*- coding: UTF8 -*-
# Crypro bot
import os
import requests
import schedule
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
from webServer import keep_alive


# BotHandler class, interacts with the telegram api
class BotHandler:
    def __init__(self, token):
        self.__token = token
        # url = "https://api.telegram.org/bot<token>/"
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


# I'm using yahoo finance to get my information
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

# Function that gets executed when schedule calls it and searches the users asset


def respondSchedule(asset, ID):
    print(f"{asset.upper()} reminder")
    crypto_bot.send_message(ID, get_price(asset))


def main():
    # Keep_alive cals the webServer,py file and mantains the script alive
    keep_alive()
    new_offset, new_reminder, canceling_reminder, userState = 0, False, False, {}
    print('Bot now runing...')

    while True:
        schedule.run_pending()
        # Gets list of all the updates
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
                    userID = current_update['message']['chat']['id']
                    # User name of the user
                    first_chat_name = current_update['message']['from']['first_name']

                    # We add all users to the userState dictionary
                    if userID not in userState.keys():
                        userState[userID] = {"state": "normal", "asset": "", "reminders": []}

                    # We need to cheek if the user is setting up a reminder
                    if userState[userID]["state"] == "newReminder":
                        # To set a reminder we need two values for our variables, the asset and the time

                        #If at any time the user types exit, the reminder is canceled
                        if first_chat_text.lower() == "exit":
                            crypto_bot.send_message(userID, "Reminder canceled")
                            userState[userID]["state"] = "normal"
                            userState[userID]["asset"] = ""

                        # We cheek we don't have a value for the asset and that it's value is valid
                        elif userState[userID]["asset"] == "" and get_price(first_chat_text) != "Asset does not exist.":
                            userState[userID]["asset"] = first_chat_text.upper()
                            crypto_bot.send_message(userID, 'At what time should I remind you? (24h format "XX:XX")')

                        # Once we have the asset we get the time
                        elif userState[userID]["asset"] != "":
                            # I use try except to see if the user is giving an invalid time
                            # I give the message as an argument to the schedule library
                            # If it returns an error I tell the user it's an invalid input
                            try:
                                reminder = schedule.every().day.at(first_chat_text).do(respondSchedule, asset=userState[userID]["asset"], ID=userID)
                            except:
                                crypto_bot.send_message(userID, "Invalid input. Try Again! (exit to cancel)")
                            else:
                                print(userState[userID]['asset']+" reminder at "+first_chat_text)
                                # Add the schedule object to the reminders for that user
                                userState[userID]["reminders"].append([reminder, userState[userID]['asset']+" reminder at "+first_chat_text])
                                print(userState[userID]["reminders"])
                                crypto_bot.send_message(userID, "Reminder set! I'll give you "+userState[userID]["asset"]+"'s price every day at "+first_chat_text)
                                # Print new reminder on server terminal
                                print(f"{'_'*10}\nNew reminder:\nAsset: {userState[userID]['asset']}\nTime: {first_chat_text}")
                                # Reset variables
                                userState[userID]["state"] = "normal"
                                userState[userID]["asset"] = ""
                        else:
                            crypto_bot.send_message(userID, "Invalid input. Try Again! (exit to cancel)")

                    elif userState[userID]["state"] == "delReminder":
                        if first_chat_text.lower() != "exit":
                            try:
                                option = int(first_chat_text)
                                if option <= 0 or option > len(userState[userID]["reminders"]):
                                    raise ValueError('ERROR')
                            except:
                                crypto_bot.send_message(userID, "Invalid input. Try Again! (exit to cancel)")
                            else:
                                # The job the user selects gets canceled
                                schedule.cancel_job(userState[userID]["reminders"][option-1][0])
                                # Item gets deleted form the dictionary
                                userState[userID]["reminders"].pop(option-1)
                                crypto_bot.send_message(userID, "Reminder canceled.")
                                userState[userID]["state"] = "normal"
                        else:
                            crypto_bot.send_message(userID, "Ok, no reminder was canceled.")
                            userState[userID]["state"] = "normal"
                    elif '/cancel_reminder' in first_chat_text:
                        if len(userState[userID]["reminders"]) != 0:
                            # https://stackoverflow.com/questions/10967819/python-when-can-i-unpack-a-generator
                            # Sends a message with all the reminders that user has
                            [*text]=("Send the number of the reminder you what to cancel.\nYour reminders:"+("\n\t"+str(i+1)+". " + userState[userID]["reminders"][i][1]) for i in range(len(userState[userID]["reminders"])))
                            crypto_bot.send_message(userID, text)
                            userState[userID]["state"]="delReminder"
                        else:
                            crypto_bot.send_message(userID, "You don't have any reminders created.")
                    # We need to cheek for the /set_reminder so that it dosen't get looked up like an asset
                    elif '/set_reminder' in first_chat_text:
                        crypto_bot.send_message(userID, "What asset should I send you updates on?(No need to add /)")
                        userState[userID]["state"]="newReminder"
                   # If the message has a / in front we cheeck it as an asset price. Except for /help and /start
                    elif '/' in first_chat_text and first_chat_text != '/help' and first_chat_text != '/start':
                        crypto_bot.send_message(userID, get_price(first_chat_text.lstrip("/")))
                        print("_"*10)
                        print(first_chat_text.upper().lstrip("/"))
                # After every update has been procesed we can move on to the next one
                new_offset = first_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
