import os
import json
from datetime import datetime
from typing import Counter, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from models import MarketData, UpdateMarketData,PredictionRequest
from predictions import load_data, load_scalers, make_pred 
from prometheus_client import Counter, REGISTRY, generate_latest, CollectorRegistry, multiprocess
from prometheus_fastapi_instrumentator import Instrumentator
from bson import ObjectId
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uvicorn
from tensorflow.keras.models import load_model

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
load_dotenv(dotenv_path)
FASTAPI_ENV = os.getenv("FASTAPI_ENV", "development")
print("FASTAPI_ENV =", FASTAPI_ENV)



if FASTAPI_ENV == "development" and "prediction_requests" in REGISTRY._names_to_collectors:
    print("Métrique déjà définie, utilisation de l'existante.")
    prediction_counter = REGISTRY._names_to_collectors["prediction_requests"]
else:
    print("Définition d'une nouvelle métrique.")
    prediction_counter = Counter(
        "prediction_requests",
        "Count of prediction requests",
        ["symbol"]
    )




# Define model directory
MODEL_DIR = os.getenv("MODEL_DIR", "../models")


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

# Create collection if not exists
async def create_collection(db, collection_name, validator=None):
    """
    Create a MongoDB collection if it does not exist.

    Args:
        db: The database instance.
        collection_name: The name of the collection to create.
        validator: Optional validator for the collection schema.
    """
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
            print(f"Data insertion failed into {collection_name}: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during data insertion into {collection_name}: {e}")
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MongoDB...")
    app.state.db = client.Cryptobot
    try:
        await create_collection(app.state.db, "market_data")
        await create_collection(app.state.db, "prediction_ml")

        print("MongoDB connection established and Collection created successfully.")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise

    yield

    print("Closing MongoDB connection...")
    client.close()

# FastAPI App
app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

@app.get("/metrics")
async def metrics():
    return JSONResponse(content=generate_latest(REGISTRY))

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# CRUD Operations
# Create a new data market
@app.post("/market_data", response_model=dict)
async def create_market_data(data: MarketData):
    try:
        new_data = data.model_dump()
        result = await db.market_data.insert_one(new_data)
        created_doc = await db.market_data.find_one({"_id": result.inserted_id})
        return document_to_dict(created_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating market data: {str(e)}")

# Retrieve all data 
@app.get("/market_data", response_model=List[dict])
async def get_all_market_data():
    try:
        # Récupérer les 100 derniers documents triés par date
        cursor = db.market_data.find().sort("openTime", -1).limit(100)
        documents = await cursor.to_list(length=100)
        return [document_to_dict(doc) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve data with matching Id
@app.get("/market_data/{item_id}", response_model=dict)
async def get_market_data_by_id(item_id: str):
    try:
        document = await db.market_data.find_one({"_id": ObjectId(item_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Market data not found")
        return document_to_dict(document)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def save_data(symbol, future_pred):
    # Prediction Counter
    prediction_counter.labels(symbol).inc()
    
    # Récupérer les données existantes
    existing_doc = await db.prediction_ml.find_one({"symbol": symbol})
   
    if existing_doc:
        existing_predictions = {pred["timestamp"]: pred["prediction"] for pred in existing_doc["predictions"]}
        unique_predictions = [
            pred for pred in future_pred if pred["timestamp"] not in existing_predictions
        ]

        if unique_predictions:
            result = await db.prediction_ml.update_one(
                {"symbol": symbol},
                {"$push": {"predictions": {"$each": unique_predictions}}}
            )
            
            return result 
    else:
        document = {
            'symbol': symbol,
            'predictions': future_pred,
            'metadata': {
                'created_at': datetime.utcnow()
            }
        }

        #prediction_counter = Counter("prediction_requests", "Count of prediction requests", ["method", "endpoint"])
        #prediction_counter.labels("POST", "/predict/").inc()
        
        
        result = await db.prediction_ml.insert_one(document)

        return result.inserted_id

#prediction_counter = Counter("prediction_requests", "Count of prediction requests", ["symbol"])

@app.post("/predict/")
async def predict(request: PredictionRequest):
    try:

        MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        symbol = request.symbol
        interval_hours = request.interval_hours
        
        # Charger le modèle
        model_path = f"{MODEL_DIR}/{symbol}_best_model.keras"
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Model not found")

        model = load_model(model_path)
        scaler, scaler_y = load_scalers(symbol)
        features = ["open", "high", "low", "volume", "trend", "volume_price_ratio", "BB_MA", "BB_UPPER", "BB_LOWER", "RSI"]
        latest_data, last_timestamp = load_data(symbol, features, scaler, model)
        future_pred = make_pred(symbol, model, scaler_y, latest_data, last_timestamp, interval_hours, db)
    
       
        # Sauvegarder les prédictions dans MongoDB
        saved_id = await save_data(symbol, future_pred)
        


        return {"symbol": symbol, "predictions": future_pred, "saved_id": str(saved_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("fastapi-mongo:app", host="127.0.0.1", port=8000, reload=True)
