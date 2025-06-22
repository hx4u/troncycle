import time
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from tradeogre import TradeOgre
# === Load API credentials from .env or environment ===
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
PAIR = "TRX-USDT"
THRESHOLD = 0.05  # 5%
TRX_AMOUNT = "100"
USDT_AMOUNT = "5"
# === Logging Setup ===
logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
# === Init API ===
client = TradeOgre(API_KEY, API_SECRET)
def get_price():
    try:
        ticker = client.ticker(PAIR)
        logging.debug(f"TICKER RAW: {ticker}")  # Add this line
        return float(ticker['price'])  # <-- Might need to change this
    except Exception as e:
        logging.error(f"Error fetching ticker: {e}")
        return None
def get_balance(currency):
    try:
        balances = client.get_balance()
        return float(balances.get(currency, 0.0))
    except Exception as e:
        logging.error(f"Failed to get balance: {e}")
        return 0.0
def sell_trx(price):
    trx_balance = get_balance("trx")
    if trx_balance < 0.1:
        logging.warning(f"Insufficient TRX to sell: {trx_balance}")
        return
    logging.info(f"Selling {trx_balance:.6f} TRX @ {price} USDT")
    result = client.sell(PAIR, qty=str(round(trx_balance, 6)), price=str(price))
    logging.info(f"Sell Result: {result}")
def buy_trx(price):
    usdt_balance = get_balance("usdt")
    if usdt_balance < 0.01:
        logging.warning(f"Insufficient USDT to buy: {usdt_balance}")
        return
    qty = round(usdt_balance / price, 6)
    logging.info(f"Buying {qty} TRX with {usdt_balance:.2f} USDT @ {price} USDT")
    result = client.buy(PAIR, qty=str(qty), price=str(price))
    logging.info(f"Buy Result: {result}")
def backtest():
    logging.info("[*] Starting BACKTEST mode")
    history = client.history(PAIR)
    # sort by timestamp (oldest to newest)
    history.sort(key=lambda x: int(x['date']))
    last_price = float(history[0]['price'])
    for trade in history[1:]:
        current_price = float(trade['price'])
        timestamp = datetime.utcfromtimestamp(int(trade['date'])).strftime('%Y-%m-%d %H:%M:%S')
        change = (current_price - last_price) / last_price
        if change >= THRESHOLD:
            logging.info(f"[Backtest] {timestamp} - Price ↑ {current_price:.4f} ({change*100:.2f}%) -> SELL TRX")
        elif change <= -THRESHOLD:
            logging.info(f"[Backtest] {timestamp} - Price ↓ {current_price:.4f} ({change*100:.2f}%) -> BUY TRX")
        else:
            logging.info(f"[Backtest] {timestamp} - Price {current_price:.4f} ({change*100:.2f}%) -> HOLD")
        last_price = current_price
def run_live():
    logging.info("[*] Starting LIVE trading mode")
    last_price = get_price()
    if last_price is None:
        logging.error("Initial price fetch failed. Exiting.")
        return
    logging.info(f"Initial price: {last_price:.4f} USDT")
    while True:
        time.sleep(60)
        current_price = get_price()
        if current_price is None:
            continue
        change = (current_price - last_price) / last_price
        logging.info(f"Price: {current_price:.4f} | Change: {change*100:.2f}%")
        if change >= THRESHOLD:
            sell_trx(current_price)
        elif change <= -THRESHOLD:
            buy_trx(current_price)
        else:
            logging.info("No significant change. Waiting...")
        last_price = current_price
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "backtest":
        backtest()
    else:
        run_live()
