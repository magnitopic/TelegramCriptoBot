import schedule
from bot import get_price

def update():
	print(get_price("BTC"))

schedule.every().day.at("11:38").do(update)

while True:
	schedule.run_pending()