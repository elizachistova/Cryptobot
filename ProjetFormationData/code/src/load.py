import json
from pymongo import MongoClient
from pprint import pprint
from Data_processor import DataLoader, DataProcessor
from Data_processor import main as process_data 
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
    # records = df.to_dict(orient="records")
    try:
        collection.insert_many(data)
        print(f"Data inserted successfully into {collection_name}.")
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
                all_data[symbol] = data['data']
    return all_data


def main():
    # Connection setup
    client = MongoClient(
    host = "127.0.0.1",
    port= 27017,
    username="CryptoBot",
    password="bot123"
    )

    db = client.Cryptobot # Select database
    data_dir =os.path.join(os.path.dirname(__file__), '../data/data_processed')
   
    processed_data  = load_processed_data(data_dir)
    create_collection(db, "Gary") # Create collection named "market_data"

    for symbol,df in processed_data.items():
        print(f"Inserting data for symbol: {symbol}")
        insert_data_to_mongo(db,"Gary",df) # insert collection in database

    # Verifying Data
    col = db["Gary"]
    datas = col.find().limit(5)
    print("\nSample data from MongoDB:")
    for data in datas:
        pprint(data)

if __name__ == "__main__":
    main()