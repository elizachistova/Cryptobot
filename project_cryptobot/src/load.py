import json
from pymongo import MongoClient
from pprint import pprint 
from dotenv import load_dotenv
from datetime import datetime
import os



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
            collection.insert_many(data)
            print(f"Data inserted successfully into {collection_name}.")
        else:
            print(f"Data insertion failed into {collection_name}.")
    except Exception as e:
        print(f"Error data insertion into {collection_name} : {e}")


def load_processed_data(processed_dir):
    all_data = {}
    for filename in os.listdir(processed_dir):
        if filename.endswith("_final.json"):
            symbol = filename.replace("_final.json", "")
            filepath = os.path.join(processed_dir, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                meta_data = data.get("metadata", {})
                data_market = data.get("data", [])
                
                transformed_data = []
                for record in data_market:
                    # Regrouper les indicateurs dans un champ "indicator"
                    indicator = {
                        "BB_UPPER": record.pop("BB_UPPER"),
                        "BB_LOWER": record.pop("BB_LOWER"),
                        "RSI": record.pop("RSI"),
                        "DOJI": record.pop("DOJI"),
                        "HAMMER": record.pop("HAMMER"),
                        "SHOOTING_STAR": record.pop("SHOOTING_STAR"),
                    }
                    
                    # Ajouter les métadonnées
                    record.update(meta_data)
                    
                    # Créer le format final avec un champ "indicator"
                    transformed_data.append({
                        "symbol": record["symbol"],
                        "last_updated": datetime.strptime(record["last_updated"], "%Y-%m-%d %H:%M:%S"),
                        "rows": record["rows"],
                        "openTime": datetime.strptime(record["openTime"], "%Y-%m-%d %H:%M:%S"),
                        "open": record["open"],
                        "high": record["high"],
                        "low": record["low"],
                        "close": record["close"],
                        "volume": record["volume"],
                        "trend": record["trend"],
                        "volume_price_ratio": record["volume_price_ratio"],
                        "indicator": indicator
                    })
                
                all_data[symbol] = transformed_data
    return all_data


def main():

    # Load .env file from a custom path
    dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
    load_dotenv(dotenv_path)
    
    host = os.getenv("HOST", "localhost").strip(",")  # Remove any trailing commas
    port = os.getenv("PORT", "27017").strip(",")  # Remove any trailing commas
    username = os.getenv("USERNAME", "").strip()
    password = os.getenv("PASSWORD", "").strip()

    try:

        # Connection setup
        client = MongoClient(
        host=host,
        port=int(port),
        username=username,
        password=password,
        #authSource="Cryptobot"
       )

        db = client.Cryptobot # Select database
        data_dir =os.path.join(os.path.dirname(__file__), '../data/data_processed')
   
        processed_data  = load_processed_data(data_dir)
        create_collection(db, "market_data") # Create collection named "market_data"

        for symbol,df in processed_data.items():
            print(f"Inserting data for symbol: {symbol}")
            insert_data_to_mongo(db,"market_data",df) # insert collection in database


        # Verifying 
        col = db["market_data"]
        datas = col.find().limit(5)
        print("\nSample data from MongoDB:")
        for data in datas:
            pprint(data)
    except Exception as e:
        print(f"Error connecting to MongoDB for insertion: {e}")

if __name__ == "__main__":
    main()