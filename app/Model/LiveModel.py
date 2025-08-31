import os
import sys
import pandas as pd
from sklearn.linear_model import LogisticRegression
import warnings
import urllib3

# 🤫 Suppress SSL warnings from urllib3 - we know what we're doing  
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")
warnings.filterwarnings("ignore", message="ssl module.*LibreSSL")
from Bot.ver_1.tools import wrapper

class LiveModel:

    def __init__(self, model_name, path_to_dataset, target_currency, weights):
        self.dataset_path = path_to_dataset
        self.model_name = model_name
        self.target = target_currency
        seed_value = 42
        w0, w1 = weights

        if model_name == 'LogisticRegression':
            self.model = LogisticRegression(max_iter=2000, random_state=seed_value, class_weight={0: w0, 1: w1})

    def model_init(self, thresholds):
        df = pd.read_csv(self.dataset_path)
        df['open_time'] = pd.to_datetime(df['open_time'])
        df.set_index('open_time', inplace=True)
        target_column = self.target + '_T+1'
        X = df.drop([target_column], axis=1)
        Y = self.get_labels(df[self.target + '_T+1'], thresholds)
        self.model.fit(X, Y)

    def predict(self, last_row):
        X = last_row.drop([self.target + '_T+1', 'open_time']).to_frame().T
        return self.model.predict(X)[0]

    def get_labels(self, sr, threshold):
        sr['label'] = sr.apply(lambda x: 1 if x > threshold else 0)
        return sr['label']

    def calc_weights(self, y_train):
        w0 = 0.5
        w1 = 0.5
        return w0, w1
 
    def train_row(self, row):
        #TODO need to switch the way we are training the model
        self.model_init(0)
        # row.drop(['open_time'], inplace=True)
        # X = row.drop([self.target+'_T+1']).to_frame().T  # Convert to a DataFrame with a single row
        # Y = self.get_row_labels(row[self.target+'_T+1'], 0)
        # Y = pd.DataFrame(Y, columns=['Numbers'])
        # self.model.partial_fit(X, Y)

def main():
    model = LiveModel("LogisticRegression", os.path.abspath(os.path.join('Data', 'lagged_data.csv')), 'CHZUSDT', [1, 1])
    model.model_init(0)
    last_lagged_row = pd.read_csv(os.path.abspath(os.path.join('Data', 'lagged_data.csv'))).iloc[-2, :]
    model.train_row(last_lagged_row)

    # Sample implementation for fetching coin data (as an example)
    coin = 'CHZUSDT'
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": coin}

    try:
        # Fetch coin data using the new API wrapper
        response = wrapper.make_binance_request("GET", url, params=params)
        print(f"Current price of {coin}: {response['price']}")
    except Exception as e:
        print(f"Error fetching data for {coin}: {e}")


if __name__ == '__main__':
    main()

