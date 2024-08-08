from vnstock3 import Vnstock
import warnings
import os
import pandas as pd
from datetime import datetime
warnings.filterwarnings('ignore')

class GetVNStock:
    def __init__(self):
        self.vnstock = Vnstock()

    def list_all_symbols(self):
        ticker_list = self.vnstock.stock().listing.all_symbols()
        return ticker_list
    
    def list_symbols_by_exchange(self):
        ticker_list = self.vnstock.stock().listing.symbols_by_exchange()
        return ticker_list
    
    def get_data(self, ticker, start = '2000-01-01', end = '2024-07-25' , interval = '1D', output_dir='vnstock_data'):
        os.makedirs(output_dir, exist_ok=True)
        list_unavailable = []
        try:
            data = self.vnstock.stock(symbol = ticker).quote.history(start = start, end = end, interval = interval)
            data.to_csv(os.path.join(output_dir, f'{ticker}.csv'))
        except Exception as e:
            list_unavailable.append(ticker)
            print(f'{ticker} + not available: {e}')

    def get_data_for_all(self, tickers, start='2000-01-01', end= '2024-07-25', interval='1D', output_dir='data'):
        os.makedirs(output_dir, exist_ok=True)
        list_unavailable = []
        for ticker in tickers:
            try:
                data = self.vnstock.stock(symbol=ticker).quote.history(start=start, end=end, interval=interval)
                data.to_csv(os.path.join(output_dir, f'{ticker}.csv'))
            except Exception as e:
                list_unavailable.append(ticker)
                print(f'{ticker} not available: {e}')
        return list_unavailable
    
    def get_industry(self):
        industry = self.vnstock.stock().listing.symbols_by_industries()
        return industry
    
    def stocks_by_group(self):
        stock_group = self.vnstock.stock().listing.symbols_by_group()
        return stock_group
    
if __name__ == '__main__':
    vnstock = GetVNStock()

    all_symbols = vnstock.list_all_symbols()
    for i in all_symbols['ticker']:
        vnstock.get_data(i)



