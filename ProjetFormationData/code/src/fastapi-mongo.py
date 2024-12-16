import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from models import MarketData, UpdateMarketData, Indicator, UpdateIndicator
from pydantic import BaseModel
from bson import ObjectId
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uvicorn

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
load_dotenv(dotenv_path)

# MongoDB Configuration
MONGO_DETAILS = {
    "host": os.getenv("HOST", "localhost"),
    "port": int(os.getenv("PORT", "27017")),
    "username": os.getenv("USERNAME", None),
    "password": os.getenv("PASSWORD", None),
    "authSource": os.getenv("AUTH_SOURCE", None),
}

client = AsyncIOMotorClient(
    host=MONGO_DETAILS["host"],
    port=MONGO_DETAILS["port"],
    username=MONGO_DETAILS["username"],
    password=MONGO_DETAILS["password"],
)
db = client["Cryptobot"]

# Helper to convert MongoDB ObjectId
def document_to_dict(doc):
    doc["_id"] = str(doc["_id"])
    return doc


# Load and process data
async def load_processed_data(processed_dir):
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
                    indicator = {
                        "BB_UPPER": record.pop("BB_UPPER"),
                        "BB_LOWER": record.pop("BB_LOWER"),
                        "RSI": record.pop("RSI"),
                        "DOJI": record.pop("DOJI"),
                        "HAMMER": record.pop("HAMMER"),
                        "SHOOTING_STAR": record.pop("SHOOTING_STAR"),
                    }
                    
                    record.update(meta_data)
                    
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

# Create collection if not exists
async def create_collection(db, collection_name, validator=None):
    if collection_name not in await db.list_collection_names():
        print(f"Creating collection: {collection_name}")
        if validator:
            await db.create_collection(collection_name, validator=validator)
        else:
            await db.create_collection(collection_name)
    else:
        print(f"Collection {collection_name} already exists.")

# Insert data into MongoDB
async def insert_data_to_mongo(db, collection_name, data):
    collection = db[collection_name]
    try:
        if isinstance(data, list) and all(isinstance(doc, dict) for doc in data):
            print(f"Inserting data into collection {collection_name}.")
            await collection.insert_many(data)
            print(f"Data inserted successfully into {collection_name}.")
        else:
            print(f"Data insertion failed into {collection_name}.")
    except Exception as e:
        print(f"Error during data insertion into {collection_name}: {e}")

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MongoDB...")
    app.state.db = client.Cryptobot

    try:
        data_dir = os.path.join(os.path.dirname(__file__), "../data/data_processed")
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        processed_data = await load_processed_data(data_dir)
        print(f"Processed data loaded: {processed_data.keys()}")

        await create_collection(app.state.db, "market_data")
        await create_collection(app.state.db, "prediction_ml")
        for symbol, records in processed_data.items():
            print(f"Inserting data for {symbol}")
            await insert_data_to_mongo(app.state.db, "market_data", records)

        print("Startup data loaded successfully.")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise

    yield

    print("Closing MongoDB connection...")
    client.close()

# FastAPI App
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# CRUD Operations
# Create a new data market
@app.post("/market_data", response_model=dict)
async def create_market_data(data: MarketData):
    try:
        new_data = data.dict()
        result = await db.market_data.insert_one(new_data)
        created_doc = await db.market_data.find_one({"_id": result.inserted_id})
        return document_to_dict(created_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating market data: {str(e)}")

# Retrieve all data 
@app.get("/market_data", response_model=List[dict])
async def get_all_market_data():
    documents = await db.market_data.find().to_list(100)
    return [document_to_dict(doc) for doc in documents]

# Retrieve data with matching Id
@app.get("/market_data/{item_id}", response_model=dict)
async def get_market_data_by_id(item_id: str):
    document = await db.market_data.find_one({"_id": ObjectId(item_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Market data not found")
    return document_to_dict(document)

# Update data with matching Id
@app.put("/market_data/{item_id}", response_model=dict)
async def update_market_data(item_id: str, update_data: UpdateMarketData):
    update_fields = {k: v for k, v in update_data.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    result = await db.market_data.update_one({"_id": ObjectId(item_id)}, {"$set": update_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Market data not found")
    updated_doc = await db.market_data.find_one({"_id": ObjectId(item_id)})
    return document_to_dict(updated_doc)

# Delete data from MongoDB
@app.delete("/market_data/{item_id}", response_model=dict)
async def delete_market_data(item_id: str):
    deleted_doc = await db.market_data.find_one_and_delete({"_id": ObjectId(item_id)})
    if not deleted_doc:
        raise HTTPException(status_code=404, detail="Market data not found")
    return document_to_dict(deleted_doc)

## Collection ML Prediction

if __name__ == "__main__":
    uvicorn.run("fastapi-mongo:app", host="127.0.0.1", port=8000, reload=True)
