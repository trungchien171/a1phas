from datetime import timedelta, datetime
import requests
import pandas as pd
import os

class GeneratePosition:
    def __init__(self, symbol = 'HSI.INDX', api_token = '667ce9a6ed0a88.82288241'):
        self.symbol = symbol
        self.api_token = api_token

    def get_feature(self):
        three_months_ago = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')
        today = datetime.today().strftime('%Y-%m-%d')
        url = f'https://eodhd.com/api/eod/{self.symbol}?from={three_months_ago}&to={today}&period=d&api_token={self.api_token}&fmt=json'
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date']).dt.date
            df.set_index('date', inplace=True)
            df = df[['close']]
            df.rename(columns={'close': self.symbol.split('.')[0]}, inplace=True)
            df = df.tail(3)
            return df
        else:
            print(f"Failed to fetch data. Status code: {resp.status_code}")
            return None
        
    def posgen(self, df):
        if df is not None and len(df) == 3:
            if df['HSI'].iloc[-2] > df['HSI'].iloc[-3]:
                pos = 1
            elif df['HSI'].iloc[-2] < df['HSI'].iloc[-3]:
                pos = -1
            else:
                pos = 0
            return pos
        else:
            print("Insufficient data to generate position")
            return None