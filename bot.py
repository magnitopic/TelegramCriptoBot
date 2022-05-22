# -*- coding: UTF8 -*-
# Crypro bot
import os
import schedule
from dotenv import load_dotenv, find_dotenv
from botHandler import BotHandler
from webServer import keep_alive
from botHandler import BotHandler
from functions import get_price, respondSchedule, newReminder, delReminder, cancelReminder


# We load the dotenv library
load_dotenv(find_dotenv())
# When using .env file use:
# os.getenv('TOKEN')
token = os.environ['TOKEN']  # Your bot's TOKEN
crypto_bot = BotHandler(token)


def main():
    # Keep_alive cals the webServer.py file and mantains the script alive
    keep_alive()
    # Define vars
    new_offset, userState = 0, {}

    print('Bot now runing...')

    while True:
        schedule.run_pending()
        # Gets list of all the updates
        all_messages = crypto_bot.get_updates(new_offset)

        # If there are any new updates
        if len(all_messages) > 0:
            for current_message in all_messages:
                first_update_id = current_message['update_id']

                # If the there is a message and text in the current update the code runs
                if 'message' in current_message and 'text' in current_message['message']:
                    # The message they sent
                    first_chat_text = current_message['message']['text']
                    # The id of the user that sent the message
                    userID = current_message['message']['chat']['id']

                    # We add all users to the userState dictionary
                    if userID not in userState.keys():
                        userState[userID] = {
                            "state": "normal",
                            "asset": "",
                            "reminders": []
                        }

                    # We need to cheek if the user is setting up a reminder
                    if userState[userID]["state"] == "newReminder":
                        newReminder(first_chat_text, crypto_bot,
                                    userState, userID, schedule)

                    elif userState[userID]["state"] == "delReminder":
                        delReminder(first_chat_text, userID,
                                    userState, crypto_bot)

                    elif '/cancel_reminder' in first_chat_text:
                        cancelReminder(userState, userID, crypto_bot)

                    # We need to cheek for the /set_reminder so that it dosen't get looked up like an asset
                    elif '/set_reminder' in first_chat_text:
                        crypto_bot.send_message(
                            userID, "What asset should I send you updates on?(No need to add /)")
                        userState[userID]["state"] = "newReminder"
                   # If the message has a / in front we cheeck it as an asset price. Except for /help and /start
                    elif '/' in first_chat_text and first_chat_text != '/help' and first_chat_text != '/start':
                        crypto_bot.send_message(
                            userID, get_price(first_chat_text.lstrip("/")))
                        print("_"*10)
                        print(first_chat_text.upper().lstrip("/"))
                # After every update has been procesed we can move on to the next one
                new_offset = first_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
