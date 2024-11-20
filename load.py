from pymongo import MongoClient
from pprint import pprint
from transform import *

client = MongoClient(
    host = "127.0.0.1",
    port= 27017,
    username="CryptoBot",
    password="bot123"
    )

db = client.Cryptobot

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
    
    Algorithm:
        - Check if collection exists.
        - If the collection doesn't exist : 
            creates the collection.
        - If the collection already exist, print thr collection name.
    """
    if collection_name not in db.list_collection_names():
        if validator:
            db.create_collection(collection_name, validator=validator)
        else:
            db.create_collection(collection_name)
    else:
        print(f"collection {collection_name} already exist")


def insert_data_to_mongo(db, collection_name, df):
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
        - Converts each row of the dataFrame into a list of dictionary records.
        - Inserts records into specified MongoDB collections.
    """

    collection = db[collection_name]
    records = df.to_dict(orient='records')
    collection.insert_many(records)

create_collection(db, "market") # Create collection named "market_data"
insert_data_to_mongo(db,"market",historical) # insert collection in database

# Verifying Data
col = db["market"]
datas = col.find()
for data in datas:
    pprint(data)