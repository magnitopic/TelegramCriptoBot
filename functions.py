import requests
from bs4 import BeautifulSoup


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


# I'm using yahoo finance to get my information
def web_scraping(url):
    url = requests.get('https://finance.yahoo.com/quote/'+url.upper())
    soup = BeautifulSoup(url.content, 'html.parser')
    result = soup.find(
        "fin-streamer", {'class': "Fw(b) Fz(36px) Mb(-4px) D(ib)"})
    return result


# Function that gets executed when schedule calls it and searches the users asset
def respondSchedule(asset, ID, crypto_bot):
    print(f"{asset.upper()} reminder")
    crypto_bot.send_message(ID, get_price(asset))


# Functions on userState
def newReminder(first_chat_text, crypto_bot, userState, userID, schedule):
    if first_chat_text.lower() == "exit":
        crypto_bot.send_message(userID, "Reminder canceled")
        userState[userID]["state"] = "normal"
        userState[userID]["asset"] = ""

    # We cheek we don't have a value for the asset and that it's value is valid
    elif userState[userID]["asset"] == "" and get_price(first_chat_text) != "Asset does not exist.":
        userState[userID]["asset"] = first_chat_text.upper()
        crypto_bot.send_message(
            userID, 'At what time should I remind you? (24h format "XX:XX")')

    # Once we have the asset we get the time
    elif userState[userID]["asset"] != "":
        # I use try except to see if the user is giving an invalid time
        # I give the message as an argument to the schedule library
        # If it returns an error I tell the user it's an invalid input
        try:
            reminder = schedule.every().day.at(first_chat_text).do(
                respondSchedule, asset=userState[userID]["asset"], ID=userID)
        except:
            crypto_bot.send_message(
                userID, "Invalid input. Try Again! (exit to cancel)")
        else:
            print(userState[userID]['asset'] +
                  " reminder at "+first_chat_text)
            # Add the schedule object to the reminders for that user
            userState[userID]["reminders"].append(
                [reminder, userState[userID]['asset']+" reminder at "+first_chat_text])
            print(userState[userID]["reminders"])
            crypto_bot.send_message(
                userID, "Reminder set! I'll give you "+userState[userID]["asset"]+"'s price every day at "+first_chat_text)
            # Print new reminder on server terminal
            print(
                f"{'_'*10}\nNew reminder:\nAsset: {userState[userID]['asset']}\nTime: {first_chat_text}")
            # Reset variables
            userState[userID]["state"] = "normal"
            userState[userID]["asset"] = ""
    else:
        crypto_bot.send_message(
            userID, "Invalid input. Try Again! (exit to cancel)")


def delReminder(first_chat_text, userID, userState, crypto_bot):
    if first_chat_text.lower() != "exit":
        try:
            option = int(first_chat_text)
            if option <= 0 or option > len(userState[userID]["reminders"]):
                raise ValueError('ERROR')
        except:
            crypto_bot.send_message(
                userID, "Invalid input. Try Again! (exit to cancel)")
        else:
            # The job the user selects gets canceled
            schedule.cancel_job(
                userState[userID]["reminders"][option-1][0])
            # Item gets deleted form the dictionary
            userState[userID]["reminders"].pop(option-1)
            crypto_bot.send_message(
                userID, "Reminder canceled.")
            userState[userID]["state"] = "normal"
    else:
        crypto_bot.send_message(
            userID, "Ok, no reminder was canceled.")
        userState[userID]["state"] = "normal"


def cancelReminder(userState, userID, crypto_bot):
    if len(userState[userID]["reminders"]) != 0:
        # https://stackoverflow.com/questions/10967819/python-when-can-i-unpack-a-generator
        # Sends a message with all the reminders that user has
        [*text] = ("Send the number of the reminder you what to cancel.\nYour reminders:"+("\n\t"+str(
            i+1)+". " + userState[userID]["reminders"][i][1]) for i in range(len(userState[userID]["reminders"])))
        crypto_bot.send_message(userID, text)
        userState[userID]["state"] = "delReminder"
    else:
        crypto_bot.send_message(
            userID, "You don't have any reminders created.")
