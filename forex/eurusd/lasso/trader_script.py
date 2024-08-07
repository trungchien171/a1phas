from ib_insync import *
from IPython.display import display, clear_output
import pandas as pd
import numpy as np
import datetime as dt
import joblib
import time
import telegram
import matplotlib.pyplot as plt
util.startLoop()

def fetch_eurusd_data(duration='3 M', bar_size='5 mins'):
    ib = IB()
    ib.connect()
    contract = Forex('EURUSD')
    
    # Use the current date and time as the start date
    end_date = dt.datetime.now()
    end_date_str = end_date.strftime('%Y%m%d %H:%M:%S') + ' US/Eastern'
    
    data = ib.reqHistoricalData(
        contract,
        endDateTime=end_date_str,
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow='BID',
        useRTH=True,
        formatDate=2,
        timeout=0
    )
    
    df = util.df(data)
    df = df[['date', 'close']]

    ib.disconnect()
    
    return df

def backtest_price(price_series, position_series):
    bt = pd.DataFrame(price_series.diff() * position_series.shift())
    bt['Date'] = [str(i)[:10] for i in bt.index]
    daily_pnl = bt.groupby('Date').sum()
    return daily_pnl

# def backtest_trade_pnl(price_series, position_series):
#     trade_pnl = pd.DataFrame()
#     trade_pnl['TradePnL'] = price_series.diff() * position_series.shift()
#     trade_pnl['Date'] = trade_pnl.index.date
#     trade_pnl['CumulativePnL'] = trade_pnl.groupby('Date')['TradePnL'].cumsum()
#     trade_pnl['TradeCumulativePnL'] = trade_pnl['CumulativePnL'] - trade_pnl['TradePnL']
    
#     return trade_pnl


def paper_trade():
    data = fetch_eurusd_data()
    data['close_mul'] = data['close'] * 100000
    data.set_index('date', inplace=True)
    data_model = pd.DataFrame()
    data_model['price'] = data['close_mul']
    data_model['target'] = data['close_mul'].shift(-4) - data['close_mul']
    for i in range(5):
        data_model[f'lag_{i}'] = data['close_mul'].shift(i) - data['close_mul'].shift(i+1)
    for i in range(5):
        data_model[f'ret_{i}'] = data['close_mul'] - data['close_mul'].shift(i)
    data_model.dropna(inplace=True)
    data_model.index = pd.to_datetime(data_model.index)
    model = joblib.load('lasso_model.joblib')
    f_names = ['lag_0', 'lag_1', 'lag_2', 'lag_3']
    predictions = model.predict(data_model[f_names])
    prediction_series = pd.Series(predictions)
    moving_avg = prediction_series.rolling(window=10).mean()
    
    def determine_position(pred, ma):
        if pred > ma:
            return 1
        elif pred < ma:
            return -1
        else:
            return 0
    
    data_model['position'] = [determine_position(p, ma) for p, ma in zip(predictions, moving_avg)]
    bt = backtest_price(data_model['price'], data_model['position'])
    
    try:
        bot = telegram.Bot(token='7117934389:AAFvk_lHb-kKg8Z75z2gZ4NwSjIleetHjdQ')
        message = f'Last trade position: {np.round(data_model["position"].iloc[-1], 2)}, ' \
                  f'Last trade time: {data_model.index[-1]}, ' \
                  f'Today total gain: {np.round(bt.iloc[-1][0], 2)}'
        bot.send_message(chat_id='-4186163291', text=message, parse_mode='HTML')
    except Exception as ex:
        print(ex)

while True:
    paper_trade()
    time.sleep(300)
