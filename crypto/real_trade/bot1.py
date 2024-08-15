import os
import pandas as pd
from binance.client import Client
from time import sleep
from dotenv import load_dotenv
import logging

load_dotenv()

api = os.getenv('API')
secret = os.getenv('SECRET')

client = Client(api, secret)

logging.basicConfig(filename='trading_strategy.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_hour_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + " hour ago UTC"))
    frame = frame.iloc[:, 0:6]
    frame.columns = ["time", "open", "high", "low", "close", "volume"]
    frame = frame.set_index("time")
    frame.index = pd.to_datetime(frame.index, unit="ms")
    frame = frame.astype(float)
    return frame

def strategytest(symbol, qty, entried=False):
    df = get_hour_data(symbol, '1h', '3')
    df['ret'] = df['close'].pct_change()
    df['price'] = df['open'].shift(-1)
    in_position = entried

    if not in_position:
        # Check entry condition
        if df['ret'].iloc[-1] > 0.01:
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
    else:
        while in_position:
            df = get_hour_data(symbol, '1h', '3')
            since_buy = df.loc[df.index > buy_time]
            if len(since_buy) > 0:
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
            sleep(3600)  # Wait for 1 hour before the next check

def run_strategy_continuously(symbol, qty):
    entried = False
    while True:
        strategytest(symbol, qty, entried)
        sleep(3600)

if __name__ == "__main__":
    logging.info("Starting strategy execution")
    run_strategy_continuously('BTCUSDT', 0.001)
