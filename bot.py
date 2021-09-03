# -*- coding: UTF8 -*-
import requests
import schedule
from bs4 import BeautifulSoup


class BotHandler:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    #url = "https://api.telegram.org/bot<token>/"

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


token = ''  # Token of your bot
magnito_bot = BotHandler(token)  # Your bot's name


def btc_scraping():
    url = requests.get('https://awebanalysis.com/es/coin-details/bitcoin/')
    soup = BeautifulSoup(url.content, 'html.parser')
    result = soup.find('td', {'class': 'wbreak_word align-middle coin_price'})
    format_result = result.text

    return format_result

def eth_scraping():
    url = requests.get('https://awebanalysis.com/es/coin-details/ethereum/')
    soup = BeautifulSoup(url.content, 'html.parser')
    result = soup.find('td', {'class': 'wbreak_word align-middle coin_price'})
    format_result = result.text

    return format_result

def tesla_scraping():
    url = requests.get('https://finance.yahoo.com/quote/TSLA/')
    soup = BeautifulSoup(url.content, 'html.parser')
    result = soup.find('td', {'class': 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'})
    format_result = result

    return format_result


def main():
    new_offset = 0
    print('Bot now runing...')

    while True:
        all_updates = magnito_bot.get_updates(new_offset)

        if len(all_updates) > 0:
            for current_update in all_updates:
                print(current_update)
                first_update_id = current_update['update_id']

                # This line cheeks if the current_update doesn't have a message. If so it discards it
                if 'message' not in current_update:
                    new_offset = first_update_id + 1
                # Else, it awsers the message
                else:
                    first_chat_text = current_update['message']['text']
                    first_chat_id = current_update['message']['chat']['id']
                    first_chat_name = current_update['message']['from']['first_name']

                    if first_chat_text == '/BTC':
                        magnito_bot.send_message(
                            first_chat_id, btc_scraping())
                        new_offset = first_update_id + 1
                    if first_chat_text == '/ETH':
                        magnito_bot.send_message(
                            first_chat_id, eth_scraping())
                        new_offset = first_update_id + 1
                    if first_chat_text == 'tesla':
                        magnito_bot.send_message(
                            first_chat_id, tesla_scraping())
                        new_offset = first_update_id + 1
                    else:
                        magnito_bot.send_message(
                            first_chat_id, 'How are you doing '+first_chat_name)
                        new_offset = first_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
