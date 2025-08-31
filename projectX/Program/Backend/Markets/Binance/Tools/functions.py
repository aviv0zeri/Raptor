# def make_order(cur,conn,client,logger, coin, base_coin, quantity, side,fiat,receipt,test_order):
#     [cur,conn,client,logger]  
#     [coin,base_coin,quantity,side]
from binance.client import BinanceAPIException, Client
def spot_order(server:list,trade:list,fiatCoin:str, receipt, test:bool):
    try:
        symbol = check_and_format_pair(coin, base_coin, exchange, client)
    except (InvalidTradingPairError, UnsupportedClientTypeError, TradingPairCheckError) as e:
        receipt.error = str(e)
        return receipt



def check_and_format_pair(coin, base_coin, client_type, client):
    symbol = f'{coin.upper()}{base_coin.upper()}'
    symbols = get_binance_symbols(client)
    if symbol in symbols:
        return symbol
    else:
        return None # Raise an error maybe? because the symbol is not present.
    
    
def get_binance_symbols(client):
    # try:
        exchange_info = client.get_exchange_info()
        symbols = []
        for symbol in exchange_info['symbols']:
            # Ensure you add the correct format to the symbols list
            symbols.append(symbol['symbol'].upper())
        # Remove duplicates and return sorted symbols
        return sorted(list(set(symbols)))
    
    # except BinanceAPIException as e:
        

        #NEED TO CONTINUE FROM HERE NEED TO MAKE SKETCHES >> AND PREPARE SPOTS FOR EXCEPTIONS AND MAKE IT IN BINANCE.EXCEPTIONS\
        #ADD TO THIS FILE ROOT DECLARATION WHEN NEEDED
        #FIRST FINISH THE BUY FUNCTION - REMOVE ALL BYBIT MENTIONS AND PREPARE EXCPTIONS STOPS AND USE THREADS. #
        #SECONDS EITHER MAKE AN ASYNC WRAPPER OR MAKE THIS AN ASYNC.#