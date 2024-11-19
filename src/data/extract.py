import json
import os
import requests
import time

def load_config(config_path='../../configs/config.json'):
    """
    Loads the configuration json file.
    
    Parameters: 
    ----------
    Config_path: Path to the config file.
    
    Returns: 
    -------
    Configuration files as a dictionary.
    """
    with open(config_path, 'r') as file:
        return json.load(file)

def fetch_data_klines(endpoint, symbol, interval, columns, limit):
      """ 
      Fetches all historical candlestick data from Binance based on parameters.

      Parameters:
      ----------
      Endpoint: str
        API endpoint for candlestick data.
      Symbol: str
        Cryptocurrency pair (e.g. "BTCUSDT")
      Interval: str
        Timeframe for candlestick data (e.g. "4h")
      Columns: list
        Column names for candlestick data
      Limit: int
        1000 (maximum allowed.)

      Returns:
      -------
      A list of dictionaries with candlestick historical data.
      """
      data_klines=[]
      params = {'symbol': symbol, 
                'interval': interval, 
                'limit': limit,
                'startTime': 0}
      
      while True:
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
                raise Exception(f"Error: {response.status_code},{response.text}")

        klines = response.json()
        if not klines:
                break
        
        for kline in klines:
            kline_dict = dict(zip(columns, kline))
            data_klines.append(kline_dict)
        
        # Looping the startTime due to the limit=1000
        params['startTime'] = klines[-1][0] + 1  #Adding 1 ms
        print(f"Fetched {len(klines)} rows for {symbol}, total rows for now: {len(data_klines)}")
        time.sleep(0.1)

      return data_klines

def fetch_data_ticker(endpoint, symbol):
      
      """ 
      Fetches ticker data from Binance (last 24hr).

      Parameters:
      ----------
      Endpoint: str
        API endpoint for candlestick data.
      Symbol: str
        Cryptocurrency pair (e.g. "BTCUSDT")

      Returns:
      -------
      A dictionary with ticker data.
      """
      params = {'symbol': symbol}
      
      response = requests.get(endpoint, params=params)
      if response.status_code != 200:
        raise Exception(f"Error: {response.status_code},{response.text}")

      ticker = response.json()
    
      return ticker

def fetch_data_trades(endpoint, symbol, columns, limit):
      """ 
      Fetches all aggregated trades data from Binance. 

      Parameters:
      ----------
      Endpoint: str
        API endpoint for candlestick data.
      Symbol: str
        Cryptocurrency pair (e.g. "BTCUSDT")
      Columns: list
        Column names for trades data
      Limit: int
        1000 (maximum allowed.)

      Returns:
      -------
      A list of dictionaries with aggregated trades data
      """
      params = {'symbol': symbol, 
                'limit': limit}
      
      response = requests.get(endpoint, params=params)
      if response.status_code != 200:
        raise Exception(f"Error: {response.status_code},{response.text}")

      data = response.json()
      #print(f"Raw Data for {symbol}: {data}")  # Log raw data for debugging
        
      data_trades = []
      for trade in data:
        if len(trade) != len(columns):
            raise Exception(f"Column count mismatch: expected {len(columns)} columns, but the trade data has {len(trade)} items.")
        
        trade_dict = {columns[i]: trade[list(trade.keys())[i]] for i in range(len(columns))}
        data_trades.append(trade_dict)
    
      return data_trades

# Storing response data in json file
def load_data(symbol, data, data_type, columns=None):
    """
    Saves the fetched data in the JSON file for each symbol.

    Parameters:
    ----------
    Symbol: str
        Cryptocurrency pair (e.g. "BTCUSDT")

    Returns:
    --------
    Data loaded in data folder (we can change this later?)
    """
    filename = os.path.join("../../data/raw/", f'{symbol}_data_{data_type}.json')

    with open(filename, 'w') as file:
        json.dump({'data': data}, file, indent=4)
    print(f"Data saved to {filename}")    


def main():
    #Extracting common parameters

    config = load_config()
    symbols = config["symbols"]
    interval = config["interval"]
    columns_klines = config["columns_klines"]
    columns_trades = config["columns_trades"]
    limit = config["limit"]
    endpoint_klines = config["api_endpoints"]["binance_klines"]
    endpoint_ticker = config["api_endpoints"]["binance_ticker"]
    endpoint_trades = config["api_endpoints"]["binance_trades"]

    #Extract and load data for each symbol
    try:
        for symbol in symbols:
            data_klines = fetch_data_klines(endpoint_klines, symbol, interval, columns_klines, limit)
            load_data(symbol, data_klines, "klines", columns_klines)
            
            data_trades = fetch_data_trades(endpoint_trades, symbol, columns_trades, limit)
            load_data(symbol, data_trades, "trades", columns_trades)

            data_ticker = fetch_data_ticker(endpoint_ticker, symbol)
            load_data(symbol, data_ticker, "ticker")
    
    except Exception as e:
        print("Error occuring:", e) 

if __name__ == "__main__":
    main()