import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime, timedelta, timezone

class TradingData:
    def __init__(self, symbol, csv_file):
        self.symbol = symbol
        self.csv_file = csv_file
    
    def get_vn30f1m_trading(self):
        resp = requests.get("https://services.entrade.com.vn/chart-api/chart?from=0&resolution=1&symbol=VN30F1M&to=9999999999")
        data = resp.json()
        vn30f1m = pd.DataFrame(data).iloc[:, :6]
        vn30f1m['t'] = vn30f1m['t'].astype(int).apply(lambda x: (datetime.fromtimestamp(x, timezone.utc) + timedelta(hours=7)).replace(tzinfo=None))
        vn30f1m.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        vn30f1m = vn30f1m[vn30f1m['Date'].dt.time == datetime.strptime('14:00:00', '%H:%M:%S').time()]
        vn30f1m = vn30f1m.tail(1)
        return vn30f1m

    def update_data(self, df):
        try:
            if os.path.exists(self.csv_file):
                existing_df = pd.read_csv(self.csv_file)
                existing_df['Date'] = pd.to_datetime(existing_df['Date'])
                df['Date'] = pd.to_datetime(df['Date'])
                new_data = df[~df['Date'].isin(existing_df['Date'])]
                new_df = pd.concat([existing_df, new_data])
                new_df.to_csv(self.csv_file, index = False)
            else:
                df.to_csv(self.csv_file, index = False)
        except Exception as e:
            print(f"Error updating data: {e}")
    
    def update_position(self, pos):
        try:
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
                df['Date'] = pd.to_datetime(df['Date'])
                df.sort_values(by = 'Date', inplace = True)
                df.loc[df.index[-1], 'Position'] = pos
                df.to_csv(self.csv_file, index=False)
                return df
            else:
                print(f"{self.csv_file} does not exist. Please ensure that the data is available")
        except Exception as e:
            print(f"Error updating position: {e}")