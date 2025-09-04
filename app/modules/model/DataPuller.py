import os
import sys
import pandas as pd
from app.modules.model.BinancePuller import BinancePuller
import datetime as dt
import time



class DataPuller:

    def __init__(self, currencies, target_currency, path_rawdata, path_dataset, low_puller, path_to_lagged_data):
        self.currencies = currencies
        self.target_currency = target_currency
        self.path_rawdata = path_rawdata
        self.path_dataset = path_dataset
        self.lags_df = pd.DataFrame()
        self.low_puller = low_puller
        self.path_to_lagged_data = path_to_lagged_data 


    def get_data(self, interval, start_data, end_date, format):
        self.low_puller.get_currencies_data(interval, start_data, end_date, format)
        

    def print_DataPuller(self):
        print('Currencies:', self.currencies)
        print('Target currency:', self.target_currency)
        print('Path to rawdata:', self.path_rawdata)
        print('Path to dataset:', self.path_dataset)
        print('Lags dataframe:', self.lags_df.head(5))
        print('Low puller:')
        self.low_puller.print()

    
    def combine_data(self):
        df = pd.DataFrame()
        
        # Reading the files from the rawdata folder
        files = os.listdir(self.path_rawdata)
        for file in files:
            # Calculate the returns using the close column
            df_corr = pd.read_csv(os.path.join(self.path_rawdata, file))
            df_corr['return'] = df_corr['close'].pct_change()
            df_corr = df_corr.iloc[1:, :]
            df[f'{file[:-4]}'] = df_corr['return']
            if file == self.target_currency + '.csv':
                df['open_time'] = df_corr['open_time']
        df.set_index('open_time', inplace=True)
        df.to_csv(self.path_dataset)
        return df
    
    def make_lags(self, number_of_lags):

        df = pd.read_csv(self.path_dataset)
        df_copy = pd.DataFrame()
        df_copy['open_time'] = df['open_time']

        for column in df.columns:
            if (column != 'open_time'):
                for i in range(0, number_of_lags + 1):
                    df_copy[f'{column}_T{i * -1}'] = df[column].shift(i)

        df_copy[f'{self.target_currency}_T+1'] = df[self.target_currency].shift(-1)
        df_copy = df_copy.iloc[number_of_lags:, :]
        self.lags_df = df_copy  
        df_copy.to_csv(self.path_to_lagged_data, index=False)
        return df_copy
    

    def append_row_to_data(self):
        # TODO make the function much more efficient - there is no reason to write the whole file again
        self.combine_data()
        

    def append_row_to_lagged_data(self):
        # TODO make the function much more efficient - there is no reason to write the whole file again
        self.make_lags(5)
    
    def pull_new_candle(self, interval):
        self.low_puller.append_candles(interval)
        self.append_row_to_data()
        self.append_row_to_lagged_data()


    def get_lag_last_row(self):
        # Ensure no NaNs in the row; fill with 0 for safety
        return self.lags_df.iloc[-1, :].fillna(0)


    ### This function is getting all the data from binance creating the dataset 
    ### and creating the lagged dataset.
    def data_init(self, interval, start_date, end_date, number_of_lags):
        self.get_data(interval, start_date, end_date, '%Y-%m-%d')
        self.combine_data()
        self.make_lags(number_of_lags)
        print('The dataset was created successfully!')


    def get_lag_second_last_row(self):
        return self.lags_df.iloc[-2, :].fillna(0)


def main():
    # define basic parameters for call
    base_url = 'https://fapi.binance.com'
    endpoint = '/fapi/v1/klines'
    rawdata_path = os.path.join('Data', 'rawdata')
    currencies = ['CHZUSDT', 'UNIUSDT', 'DOTUSDT', 'ETCUSDT', 'ANKRUSDT', 'BTCUSDT']
    binance_puller = BinancePuller(base_url, endpoint, rawdata_path, currencies)
    target_currency = 'CHZUSDT'
    path_rawdata = os.path.join('Data', 'rawData')
    path_dataset = os.path.join('Data', 'dataset.csv')
    path_to_lagged_data = os.path.join('Data', 'lagged_data.csv')
    data_puller = DataPuller(currencies, target_currency, path_rawdata,
                              path_dataset, binance_puller, path_to_lagged_data)
    data_puller.data_init('3m', '2024-09-14', '2024-09-15', 5)
    data_puller.print_DataPuller()
    data_puller.combine_data()
    data_puller.make_lags(5)


if __name__ == '__main__':
    main()
