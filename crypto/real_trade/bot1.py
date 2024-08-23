import os
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
from time import sleep
from dotenv import load_dotenv
import logging

load_dotenv()

api = os.getenv('API')
secret = os.getenv('SECRET')

client = Client(api, secret)

logging.basicConfig(
    handlers=[
        logging.FileHandler(r'D:\github\a1phas\crypto\real_trade\bot1.log'),
        logging.StreamHandler()
    ],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def get_hour_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + " hour ago UTC"))
    frame = frame.iloc[:, 0:6]
    frame.columns = ["time", "open", "high", "low", "close", "volume"]
    frame = frame.set_index("time")
    frame.index = pd.to_datetime(frame.index, unit="ms")
    frame = frame.astype(float)
    return frame

def strategytest(symbol, qty):
    logging.info(f"Running strategy for {symbol} with quantity {qty}")
    df = get_hour_data(symbol, '1h', '3')
    df['ret'] = df['close'].pct_change()
    df['price'] = df['open'].shift(-1)
    logging.info(f"Data retrieved: {df.head()}")

    in_position = False
    buy_time = None
    tp = None
    sl = None

    # Check entry condition
    if not in_position and df['ret'].iloc[-1] > 0.006:
        buy_price = df['price'].iloc[-1]
        tp = buy_price * 1.05
        sl = buy_price * 0.95
        try:
            order = client.create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
            logging.info(f"Entry order executed: {order}")
            in_position = True
            buy_time = pd.to_datetime(order['transactTime'], unit='ms')
        except Exception as e:
            logging.error(f"Error executing entry order: {e}")

    if in_position:
        df = get_hour_data(symbol, '1h', '3')
        since_buy = df.loc[df.index > buy_time]
        for _, row in since_buy.iterrows():
            if row['high'] > tp:
                try:
                    order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                    logging.info(f"Take Profit order executed: {order}")
                    in_position = False
                    break
                except Exception as e:
                    logging.error(f"Error executing take profit order: {e}")
                    in_position = False
                    break
            elif row['low'] < sl:
                try:
                    order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                    logging.info(f"Stop Loss order executed: {order}")
                    in_position = False
                    break
                except Exception as e:
                    logging.error(f"Error executing stop loss order: {e}")
                    in_position = False
                    break

def check_balance():
    try:
        account_info = client.get_account()
        balances = account_info['balances']
        balance_info = []
        for balance in balances:
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            if free > 0 or locked > 0:
                balance_info.append({
                    'Asset': asset,
                    'Free': free,
                    'Locked': locked
                })
        return balance_info
    except Exception as e:
        logging.error(f"Error retrieving account balance: {e}")
        return []

def log_balance():
    balance_info = check_balance()
    if balance_info:
        for info in balance_info:
            logging.info(f"Balance - Asset: {info['Asset']}, Free: {info['Free']}, Locked: {info['Locked']}")
    else:
        logging.info("No balance information available.")

def run_strategy_continuously(symbol, qty):
    while True:
        logging.info("Starting new loop iteration")
        start_time = datetime.now()
        
        log_balance()
        strategytest(symbol, qty)
        
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"Strategy execution took {duration}")
        
        next_execution_time = timedelta(hours=1) - duration
        
        sleep_duration = next_execution_time.total_seconds()
        if sleep_duration > 0:
            logging.info(f"Sleeping for {sleep_duration} seconds until next execution")
            sleep(sleep_duration)
        else:
            logging.info("Sleeping for 10 seconds due to immediate next execution")
            sleep(10)
            
        logging.info("Sleeping until next execution")



if __name__ == "__main__":
    logging.info("Starting strategy execution")
    run_strategy_continuously('BTCUSDT', 0.001)