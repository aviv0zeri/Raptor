from datetime import datetime
import time
import pytz
import requests
import pandas as pd
import os
from app.modules.api import wrapper

class BinancePuller:

    def __init__(self, base_url, endpoint, rawdata_path, currencies):
        self.base_url = base_url
        self.endpoint = endpoint
        self.rawdata_path = rawdata_path
        self.currencies = currencies
        # Ensure rawdata directory exists
        try:
            os.makedirs(self.rawdata_path, exist_ok=True)
        except Exception:
            pass

    def print(self):
        print(f'Base URL: {self.base_url}')
        print(f'Endpoint: {self.endpoint}')
        print(f'Rawdata path: {self.rawdata_path}')
        print(f'Currencies: {self.currencies}')

    def datetime_to_milliseconds(self, datetime_str, format):
        if datetime_str == 'now':
            dt = datetime.now()
        else:
            dt = datetime.strptime(datetime_str, format)
        dt_utc = dt.astimezone(pytz.UTC)
        milliseconds = int(dt_utc.timestamp() * 1000)
        return milliseconds

    def get_currency_data(self, currency, interval, start_date, end_date, format):
        params = {
            'symbol': currency,
            'interval': interval,
            'limit': 1500,
            'startTime': self.datetime_to_milliseconds(start_date, format),
            'endTime': self.datetime_to_milliseconds(end_date, format)
        }

        candles_data = self.get_candles_data(params)
        df = self.create_df(candles_data)

        return df

    def create_df(self, candles_data):
        columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                   'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']

        dtype = {
            'close': 'float64',
            'open': 'float64',
            'high': 'float64',
            'low': 'float64',
            'open_time': 'datetime64[ms, Asia/Jerusalem]',
        }

        df = pd.DataFrame(candles_data, columns=columns)
        df = df.astype(dtype)
        df.drop(['high', 'low', 'volume', 'close_time', 'quote_asset_volume',
                 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], axis=1, inplace=True)
        return df

    def get_last_candle(self, params):
        response = wrapper.make_binance_request("GET", self.base_url + self.endpoint, params=params)
        if len(response.json()) == 0:
            raise Exception(f'No data for the given parameters {params}')
        candles_data = []
        candles_data.extend(response.json())

        return candles_data

    def get_candles_data(self, params):
        response = wrapper.make_binance_request("GET", self.base_url + self.endpoint, params=params)

        if len(response.json()) == 0:
            raise Exception(f'No data for the given parameters {params}')

        candles_data = []

        while len(response.json()) > 0 and params['startTime'] < params['endTime']:
            candles_data.extend(response.json())
            params['startTime'] = min(candles_data[-1][0] + 1, params['endTime'])
            response = wrapper.make_binance_request("GET", self.base_url + self.endpoint, params=params)

        return candles_data

    def get_currencies_data(self, interval, start_date, end_date, format):
        for currency in self.currencies:
            currency_file = os.path.join(self.rawdata_path, f'{currency}.csv')
            # Check if file exists and is recent (less than 7 days old)
            if os.path.exists(currency_file):
                file_age = time.time() - os.path.getmtime(currency_file)
                if file_age < 604800:  # 7 days in seconds
                    print(f'Using existing data for {currency} (age: {file_age/3600:.1f} hours)')
                    continue
            
            print(f'Downloading fresh data for {currency}...')
            df = self.get_currency_data(currency, interval, start_date, end_date, format)
            if df.empty:
                raise Exception(f'Failed to withdraw data for {currency}')
            df.to_csv(currency_file, index=False)
        print('All the data is ready')

    def append_candles(self, interval):
        for currency in self.currencies:
            currency_file = os.path.join(self.rawdata_path, f'{currency}.csv')
            df = self.get_currency_last_candle(currency, interval)
            if df.empty:
                raise Exception(f'Failed to withdraw data for {currency}')
            df.to_csv(currency_file, mode='a', header=False, index=False)
        print('Last candle was appended to all the files')

    def get_currency_last_candle(self, currency, interval):
        params = {
            'symbol': currency,
            'interval': interval,
            'limit': 1
        }
        candles_data = self.get_last_candle(params)
        df = self.create_df(candles_data)
        return df

    def get_current_price(self, currency, interval):
        df = self.get_currency_last_candle(currency, interval)
        return df['close'].values[0]


def main():
    base_url = 'https://fapi.binance.com'
    endpoint = '/fapi/v1/klines'
    rawdata_path = os.path.join('Data', 'rawdata')
    currencies = ['CHZUSDT', 'UNIUSDT', 'DOTUSDT', 'ETCUSDT', 'ANKRUSDT', 'BTCUSDT']

    binance_puller = BinancePuller(base_url, endpoint, rawdata_path, currencies)
    print(f"The current price of CHZUSDT is {binance_puller.get_current_price('CHZUSDT', '1m')}")


if __name__ == '__main__':
    main()
