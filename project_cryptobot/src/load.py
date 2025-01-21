import json
from pymongo import MongoClient
from pprint import pprint 
from dotenv import load_dotenv
import datetime
from extract import load_config, fetch_data_klines
from Data_processor import DataProcessor
import os
import pandas as pd



def create_collection(db, collection_name, validator=None):
    """
    Creates a collection if it doesn't already exist in MongoDB.

    Parameters:
        - db : MongoDB database.
            Where the collection will be created.
        - collection_name (str): 
            Name of the collection to create.
        - validator: 
            Enforce schema of validation rules.
    
    Algorithms:
        - Check if collection exists.
        - If the collection doesn't exist : 
            creates the collection.
        - If the collection already exist, print the collection name.
    """
    if collection_name not in db.list_collection_names():
        if validator:
            db.create_collection(collection_name, validator=validator)
        else:
            db.create_collection(collection_name)
    else:
        print(f"collection {collection_name} already exist")


def transform_data(row):
    """
    Transforms data into Document for MongoDB.
    """
    if isinstance(row, pd.Series):
        row = row.to_dict()

    return {"symbol": row.get("symbol"),
        "last_updated": datetime.datetime.now(),
        "rows": row.get("rows"),
        "openTime": row.get("openTime"),
        "open": row.get("open"),
        "high": row.get("high"),
        "low": row.get("low"),
        "close": row.get("close"),
        "volume": row.get("volume"),
        "trend": row.get("trend"),
        "volume_price_ratio": row.get("volume_price_ratio"),
        "indicator": {
            "BB_MA": row.get("BB_MA"),
            "BB_UPPER": row.get("BB_UPPER"),
            "BB_LOWER": row.get("BB_LOWER"),
            "RSI": row.get("RSI"),
            "DOJI": row.get("DOJI"),
            "HAMMER": row.get("HAMMER"),
            "SHOOTING_STAR": row.get("SHOOTING_STAR"),
        },
    }


def insert_data_to_mongo(db, collection_name, data):
    """
    Inserts data into MongoDB collection.

    Parameters:
        - db : MongoDB database.
            Where the collection will be created.
        - collection_name (str): 
            Name of the collection to create.
        - df : DataFrame
            The DataFrame containing the cleaned data to be inserted. 
            Each row will be converted to document
    
    Algorithms:
        - Attemps inserts records into specified MongoDB collections.
        - Handles errors of insertion
    """

    collection = db[collection_name]
    try:
        if isinstance(data, list) and all(isinstance(doc, dict) for doc in data):
            print(f"Inserting data into collection {collection_name}.")
            collection.insert_many(data)
            print(f"Data inserted successfully into {collection_name}.")
        else:
            print(f"Data insertion failed into {collection_name}.")
    except Exception as e:
        print(f"Error data insertion into {collection_name} : {e}")

def main():

    # Load .env file from a custom path
    dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
    load_dotenv(dotenv_path)
    
    host = os.getenv("HOST", "localhost").strip(",")  
    port = os.getenv("PORT", "27017").strip(",") 
    username = os.getenv("USERNAME", "").strip()
    password = os.getenv("PASSWORD", "").strip()

    config = load_config()
    symbols = config["symbols"]
    interval = config["interval"]
    columns_klines = config["columns_klines"]
    limit = config["limit"]
    endpoint_klines = config["api_endpoints"]["binance_klines"]

    try:

        # Connection setup
        client = MongoClient(
        host=host,
        port=int(port),
        username=username,
        password=password,
       )

        db = client.Cryptobot # Select database
        create_collection(db, "market_data") # Create collection named "market_data"


        for symbol in symbols:
            print(f"Fetching data for symbol: {symbol}")
            data = fetch_data_klines(endpoint_klines, symbol, interval, columns_klines, limit)
            if not isinstance(data, list):
                print(f"Erreur: Les données pour le symbole {symbol} ne sont pas une liste.")
                continue
            
            #
            if not all(isinstance(record, dict) for record in data):
                print(f"Erreur: Les éléments de données pour le symbole {symbol} ne sont pas des dictionnaires.")
                continue
            for record in data:
                record['close'] = float(record['close'])
                record['open'] = float(record['open'])
                record['high'] = float(record['high'])
                record['low'] = float(record['low'])
                record['volume'] = float(record['volume'])
                record['quoteVolume'] = float(record['quoteVolume'])
                record['openTime'] = pd.to_datetime(record['openTime'], unit='ms')
                record['closeTime'] = pd.to_datetime(record['closeTime'], unit='ms')
            
            df = pd.DataFrame(data)
            print(f"Processing data for symbol: {symbol}")
            df = DataProcessor.process_dataframe(df)
            df['symbol'] = symbol
            df['rows'] = len(df) 

            df_final = [transform_data(row.to_dict()) for _, row in df.iterrows()]
            print(f"Inserting data for symbol: {symbol}")
            insert_data_to_mongo(db,"market_data",df_final) # insert collection in database


        # Verifying 
        col = db["market_data"]
        datas = db.market_data.find({"symbol": "BTCUSDT"}).sort({"openTime": -1}).limit(5)

        print("\nSample data from MongoDB:")
        for data in datas:
            pprint(data)
    except Exception as e:
        print(f"Error insert data to MongoDB: {e}")

if __name__ == "__main__":
    main()