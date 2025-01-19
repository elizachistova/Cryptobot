import json
import os
import requests
import time
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv


def load_config(CONFIG_DIR='/app/config/config.json'):
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
    
    
def fetch_data_klines(mongodb_client, symbol, interval, columns, limit, endpoint_klines, start_date=None, end_date=None):
    """
    Récupère les données klines et les insère directement dans raw_market_data
    
    Args:
        mongodb_client: Client MongoDB
        symbol: Paire de trading (ex: "BTCUSDT")
        interval: Intervalle temporel
        columns: Noms des colonnes
        limit: Limite de données par requête
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
    """
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        # On ne prend que 2 ans de donneés
        start_date = end_date - timedelta(days=730)

    end_timestamp = int(end_date.timestamp() * 1000)
    start_timestamp = int(start_date.timestamp() * 1000)

    params = {
        'symbol': symbol, 
        'interval': interval, 
        'limit': limit, 
        'startTime': start_timestamp, 
        'endTime': end_timestamp
    }

    raw_market_data = mongodb_client.Cryptobot.raw_market_data
    
    while True:
        response = requests.get(endpoint_klines, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code},{response.text}")
        
        klines = response.json()
        
        if not klines:
            print("No more data returned, breaking the loop.")
            break
        
        # Préparation des documents pour MongoDB
        documents = []
        for kline in klines:
            document = dict(zip(columns, kline))
            # Conversion des types pour MongoDB
            document['symbol'] = symbol
            document['openTime'] = datetime.fromtimestamp(document['openTime'] / 1000)
            document['open'] = float(document['open'])
            document['high'] = float(document['high'])
            document['low'] = float(document['low'])
            document['close'] = float(document['close'])
            document['volume'] = float(document['volume'])
            documents.append(document)

        # Insertion par lots dans MongoDB
        if documents:
            try:
                raw_market_data.insert_many(documents)
                print(f"Inserted {len(documents)} documents for {symbol}")
            except Exception as e:
                print(f"Error inserting documents for {symbol}: {e}")

        # Mise à jour du startTime pour la prochaine itération
        params['startTime'] = klines[-1][0] + 1
        
        if klines[-1][0] >= end_timestamp:
            print("Reached end date, breaking the loop.")
            break
            
        time.sleep(0.1)  # Respect des limites de l'API

    return len(documents)  # Retourne le nombre de documents insérés


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
    # Charger les variables d'environnement et la configuration
    dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
    load_dotenv(dotenv_path)

    config = load_config()
    symbols = config["symbols"]
    interval = config["interval"]
    columns_klines = config["columns_klines"]
    columns_trades = config["columns_trades"]
    limit = config["limit"]
    endpoint_klines = config["api_endpoints"]["binance_klines"]
    endpoint_ticker = config["api_endpoints"]["binance_ticker"]
    endpoint_trades = config["api_endpoints"]["binance_trades"]

    # Configuration MongoDB
    try:
        mongodb_client = MongoClient(
            host="mongodb",
            port=int(os.getenv("PORT", "27017").strip(",")),
            username=os.getenv("USERNAME", "").strip(),
            password=os.getenv("PASSWORD", "").strip()
        )
        
        # Extract data for each symbol
        for symbol in symbols:
            try:
                inserted_count = fetch_data_klines(
                    mongodb_client,
                    symbol,
                    interval,
                    columns_klines,
                    limit,
                    endpoint_klines
                )
                print(f"Processed {symbol}: {inserted_count} documents inserted")

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue

    except Exception as e:
        print(f"MongoDB connection error: {e}")
    
    finally:
        if 'mongodb_client' in locals():
            mongodb_client.close()
            
if __name__ == "__main__":
    main()