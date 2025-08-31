import time
import schedule
import os
import random
import warnings
import sys

# Add the Model directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from BinancePuller import *
    from DataPuller import *
    from LiveModel import *
except ImportError as e:
    print(f"Warning: Could not import ML modules: {e}")
    print("Using simplified model for testing...")
    
    # Create a simple fallback model
    class SimpleModel:
        def __init__(self, *args, **kwargs):
            pass
        
        def model_init(self, *args):
            print("Simple model initialized")
        
        def train_row(self, *args):
            pass
        
        def predict(self, *args):
            return random.choice([0, 1])  # 0 = HOLD, 1 = BUY
    
    class SimpleDataPuller:
        def __init__(self, *args, **kwargs):
            pass
        
        def data_init(self, *args, **kwargs):
            print("Simple data puller initialized")
        
        def pull_new_candle(self, *args):
            pass
        
        def get_lag_second_last_row(self):
            return [0] * 10
        
        def get_lag_last_row(self):
            return [0] * 10
    
    # Replace the imports with simple versions
    LiveModel = SimpleModel
    DataPuller = SimpleDataPuller
    BinancePuller = SimpleDataPuller  # Use same simple class for both
# from BinancePuller import create_dataset
warnings.filterwarnings("ignore")


def update_model_output_file(signal, quantity, coin, model_output_path):
    with open(model_output_path, 'a') as f:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if signal == 1:
            signal = 'BUY'
        else:
            signal = 'HOLD'
        coin = 'CHZ/USDT' #TODO use the coin variable from the parameters instead.
        f.write(f'{time}, {signal}, {quantity}, {coin}\n')
    return None
    

def main():

    print('Starting the Model...\n')


    #---------------------------------------------------------------------------------------

    ### interval - the candels you want to trade with.
    ### currencies - the currencies you will use as data. - not implemented yet.
    ### targer_currency - the currencies that will be traded.

    starting_date = '2023-10-19' #TODO need to be changed to the earliest date available.
    end_date = 'now' #TODO need to be changed to the current date available.
    global interval 
    interval = '2h'
    currencies = ['CHZUSDT','UNIUSDT','DOTUSDT','ETCUSDT','ANKRUSDT','BTCUSDT']
    global target_currency
    target_currency = 'CHZUSDT' 
    base_url = 'https://fapi.binance.com'
    end_point = '/fapi/v1/klines'
    rawdata_path = os.path.join('Data','rawdata')
    dataset_path = os.path.join('Data','dataset.csv')
    lagged_data_path = os.path.join('Data','lagged_data.csv')
    global model_output_path
    model_output_path = os.path.join('..', 'model_output.csv')

    low_puller = BinancePuller(base_url, end_point, rawdata_path, currencies)
    data_puller = DataPuller(currencies, target_currency, rawdata_path, dataset_path, low_puller, lagged_data_path)
    model = LiveModel("LogisticRegression", lagged_data_path, target_currency, [1, 1])

    data_puller.data_init(interval, starting_date, end_date, 5)
    model.model_init(0)

    #---------------------------------------------------------------------------------------

    ### Schedule the function to run every wanted period
    schedule.every(1).minutes.do(lambda: perform_action(data_puller,model=model))

    ## Keep the script running to ensure the scheduling happens
    while True:
        schedule.run_pending()
        time.sleep(1)


def perform_action(data_puller: DataPuller, model: LiveModel):

    data_puller.pull_new_candle(interval)
    seconed_last_row = data_puller.get_lag_second_last_row()
    model.train_row(seconed_last_row)
    last_lagged_row = data_puller.get_lag_last_row()
    signal = model.predict(last_lagged_row)
    print(f'Got signal: {signal}')
    update_model_output_file(signal, 1, target_currency, model_output_path)




if __name__ == "__main__":
    main()






















    
# def check_for_nulls(df):
#     for column in df.columns:
#         if df[column].isnull().sum() != 0:
#             print(f'{column} has {df[column].isnull().sum()} missing values') 
