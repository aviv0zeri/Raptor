from datetime import datetime
import pytz
import requests
from datetime import datetime
import pandas as pd
import os
import main
from ..Bot.ver_1.tools.api_utils import make_binance_request  # Import the new API wrapper

def get_binance_historical_data(symbol, interval, start_date, end_date=None):
    format = "%Y-%m-%d"
    start_date = datetime_to_milliseconds(start_date, format)
    end_date = datetime_to_milliseconds(end_date, format) if end_date else None
    
    # define basic parameters for call
    base_url = 'https://fapi.binance.com'
    endpoint = '/fapi/v1/klines'
    method = 'GET'
    
    # Set the start time parameter in the params dictionary
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': 1500,
        'startTime': start_date,  # Start time in milliseconds
        'endTime': end_date if end_date else 9999999999999
    }

    # Make initial API call to get candles
    response = make_binance_request("GET", base_url + endpoint, params=params)  # Replaced with the new API wrapper

    candles_data = []

    while len(response.json()) > 0:
        # Append the received candles to the list
        candles_data.extend(response.json())

        # Update the start time for the next API call
        params['startTime'] = candles_data[-1][0] + 1  # last candle open_time + 1ms
        # Make the next API call
        response = make_binance_request("GET", base_url + endpoint, params=params)  # Replaced with the new API wrapper

    # Wrap the candles data as a pandas DataFrame
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


def make_api_call(base_url, endpoint="", method="GET", **kwargs):
    # Construct the full URL
    full_url = f'{base_url}{endpoint}'

    # Make the API call
    response = requests.request(method=method, url=full_url, **kwargs)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response
    else:
        # If the request was not successful, raise an exception with the error message
        raise Exception(f'API request failed with status code {response.status_code}: {response.text}')


def get_all_data(coins, interval, start_date, path='data/', end_date=None):
    for coin in coins:
        print(f'Getting data for {coin} with interval {interval}')
        try:
            df = get_binance_historical_data(coin, interval, start_date, end_date)
        except Exception as e:
            print(f'API Failed to get data for {coin}')
            print(e)
            continue
        mindate = df['open_time'].min()

        if mindate > pd.to_datetime(start_date + ' 00:00:00+02:00', format='%Y-%m-%d %H:%M:%S%z'):
            print(f'for coin {coin} start date is {start_date} but the first data is from {mindate}')
            continue
        else:
            df.to_csv(os.path.join(path, f'{coin}.csv'), index=False)
            ROWS_NUMBER = df.shape[0]
        print(f'{coin} is done')
    print('All the data is ready')


def datetime_to_milliseconds(datetime_str, format):
    # Parse the date-time string to a datetime object with timezone information
    dt = datetime.strptime(datetime_str, format)
    # Convert the datetime object to UTC
    dt_utc = dt.astimezone(pytz.UTC)
    # Get the Unix time in seconds and convert to milliseconds
    milliseconds = int(dt_utc.timestamp() * 1000)
    return milliseconds
