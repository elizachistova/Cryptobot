import json
import os
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../config/config.json')
def load_config(CONFIG_DIR=CONFIG_DIR):
    """
    Loads the configuration json file.
    
    Returns: 
    -------
    Configuration files as a dictionary.
    """
    try:
        with open(CONFIG_DIR, 'r') as file:
            return json.load(file)
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_DIR}")
    
def fetch_data_klines(endpoint, symbol, interval, columns, limit, start_date=None, end_date=None):
    data_klines = []

    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        print("Fetching from the earliest available data.")

    end_timestamp = int(end_date.timestamp() * 1000)
    start_timestamp = int(start_date.timestamp() * 1000) if start_date else 0

    params = {'symbol': symbol, 'interval': interval, 'limit': limit, 'startTime': start_timestamp, 'endTime': end_timestamp}

    while True:
        response = requests.get(endpoint, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code},{response.text}")
        
        klines = response.json()
        
        if not klines:
            print("No more data returned, breaking the loop.")
            break
        
        for kline in klines:
            kline_dict = dict(zip(columns, kline))
            data_klines.append(kline_dict)
        
        params['startTime'] = klines[-1][0] + 1

        print(f"Fetched {len(data_klines)} rows for {symbol} from {start_date if start_date else 'earliest available'} to {end_date.strftime('%Y-%m-%d')}")
        if klines[-1][0] >= end_timestamp:
            print("Reached end date, breaking the loop.")
            break
        time.sleep(0.1)

    data_klines.sort(key=lambda x: x['openTime'], reverse=True)
    
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
        
      data_trades = []
      for trade in data:
        if len(trade) != len(columns):
            raise Exception(f"Column count mismatch: expected {len(columns)} columns, but the trade data has {len(trade)} items.")
        
        trade_dict = {columns[i]: trade[list(trade.keys())[i]] for i in range(len(columns))}
        data_trades.append(trade_dict)
    
      return data_trades
