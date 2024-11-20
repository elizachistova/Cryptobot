import json
import os
import requests
import time
from datetime import datetime, timedelta


DATA_RAW_DIR = os.getenv('DATA_RAW_DIR', '/app/code/data/data_raw')
DATA_PROCESSED_DIR = os.getenv('DATA_PROCESSED_DIR', '/app/code/data/data_processed')
CONFIG_DIR = os.getenv('CONFIG_DIR', '/app/code/config')

def create_config():
    """
    Crée le fichier config.json avec les paramètres par défaut si il n'existe pas
    """
    # Configuration par défaut
    default_config = {
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "interval": "1h",
        "limit": 1000,
        "columns_klines": [
            "openTime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "closeTime",
            "quoteVolume",
            "numTrades",
            "takerBuyBaseVolume",
            "takerBuyQuoteVolume",
            "ignore"
        ],
        "columns_trades": [
            "id",
            "price",
            "qty",
            "quoteQty",
            "time",
            "isBuyerMaker",
            "isBestMatch"
        ],
        "api_endpoints": {
            "binance_klines": "https://testnet.binance.vision/api/v3/klines",
            "binance_ticker": "https://testnet.binance.vision/api/v3/ticker/24hr",
            "binance_trades": "https://testnet.binance.vision/api/v3/trades"
        }
    }

    # Création des dossiers nécessaires
    os.makedirs('/app/code/config', exist_ok=True)
    os.makedirs('app/code/data_raw', exist_ok=True)

    config_path = os.path.join(CONFIG_DIR, 'config.json')
    
    # Vérifier si le fichier existe déjà
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
            print(f"Fichier de configuration créé : {config_path}")
    
    return default_config

def load_config(config_path='/app/code/config/config.json'):
    """
    Loads the configuration json file.
    
    Parameters: 
    ----------
    Config_path: Path to the config file.
    
    Returns: 
    -------
    Configuration files as a dictionary.
    """
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Configuration file not found. Creating default configuration...")
        return create_config()

def fetch_data_klines(endpoint, symbol, interval, columns, limit, start_date=None, end_date=None):
    data_klines = []

    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=31)

    end_timestamp = int(end_date.timestamp() * 1000)
    start_timestamp = int(start_date.timestamp() * 1000)

    params = {'symbol': symbol, 'interval': interval, 'limit': limit, 'startTime': start_timestamp, 'endTime': end_timestamp}

    while True:
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code},{response.text}")
        klines = response.json()
        if not klines or klines[-1][0] > end_timestamp:
            break
        for kline in klines:
            kline_dict = dict(zip(columns, kline))
            data_klines.append(kline_dict)
        params['startTime'] = klines[-1][0] + 1

    print(f"Fetched {len(data_klines)} rows for {symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
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
    filename = os.path.join(DATA_RAW_DIR, f'{symbol}_data_{data_type}.json')

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