import datetime
import joblib
import json
import numpy as np
import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv
from tensorflow.keras.models import load_model
from pymongo import MongoClient
import logging

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Définir les chemins
DATA_PREDICTED_DIR = os.path.join(os.path.dirname(__file__), '../data/data_predicted')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../config/config.json')
dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')

# Charger les variables d'environnement
load_dotenv(dotenv_path)

host = os.getenv("HOST", "localhost").strip(",")
port = os.getenv("PORT", "27017").strip(",")
username = os.getenv("USERNAME", "").strip()
password = os.getenv("PASSWORD", "").strip()


def load_data(symbol, features, scaler, model):
    client = MongoClient(host, int(port), username=username, password=password)
    db = client.Cryptobot
    collection = db['market_data']

    # Query MongoDB
    query = {"symbol": symbol}
    projection = {
        "openTime": 1,
        "open": 1,
        "high": 1,
        "low": 1,
        "close": 1,
        "volume": 1,
        "trend": 1,
        "volume_price_ratio": 1,
        "indicator": 1,
        "_id": 0
    }
    cursor = collection.find(query,projection).sort("openTime", 1)
 
    df = pd.DataFrame(list(cursor))
 
    if 'indicator' in df.columns:
        indicator_df = pd.json_normalize(df['indicator'])
        df = pd.concat([df, indicator_df], axis=1)
        df.drop(columns=['indicator'], inplace=True)

    df = df.rename(columns={
        "openTime": "openTime",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume",
        "trend": "trend",
        "volume_price_ratio": "volume_price_ratio",
        "BB_MA": "BB_MA",
        "BB_UPPER": "BB_UPPER",
        "BB_LOWER": "BB_LOWER",
        "RSI": "RSI",
        "DOJI": "DOJI",
        "HAMMER": "HAMMER",
        "SHOOTING_STAR": "SHOOTING_STAR"
    })
 
    if 'openTime' not in df.columns:
        raise ValueError(f"'openTime' is not in the DataFrame for symbol {symbol}. Check MongoDB documents.")

    df['openTime'] = pd.to_datetime(df['openTime'])
    df.set_index('openTime', inplace=True)
    df = df.sort_index()

    df = df[-model.input_shape[1]:]
 
    scaled_data = scaler.transform(df[features].values)
    input_data = np.reshape(scaled_data, (scaled_data.shape[0], scaled_data.shape[1], 1))

    # Get latest timestamp
    last_timestamp = df.index.max()

    return input_data, last_timestamp


def load_scalers(symbol):
    scaler_path = f"{MODEL_DIR}/{symbol}_scaler.pkl"
    scaler_y_path = f"{MODEL_DIR}/{symbol}_scaler_y.pkl"

    try:
        scaler = joblib.load(scaler_path)
        scaler_y = joblib.load(scaler_y_path)
        logger.info(f"Scalers loaded: {scaler_path}, {scaler_y_path}")
    except Exception as e:
        raise ValueError(f"Failed to load scalers for {symbol}: {e}")

    return scaler, scaler_y

def get_existing_predictions(db, symbol):
    # Récupérer les prédictions existantes depuis la base de données
    db = MongoClient(host, int(port), username=username, password=password).Cryptobot
    document = db.prediction_ml.find_one({"symbol": symbol})
    if document:
        return {pred["timestamp"]: pred["prediction"] for pred in document["predictions"]}
    return {}

def make_pred(symbol, model, scaler_y, latest_data, last_timestamp, interval_hours, db):
    # Obtenir les prédictions existantes
    existing_predictions = get_existing_predictions(db, symbol)

    # Générer de nouvelles prédictions
    prediction = model.predict(latest_data, verbose=0)
    predicted_values = scaler_y.inverse_transform(prediction)
    future_pred = []
    
    for i, value in enumerate(predicted_values):
        next_timestamp = last_timestamp + datetime.timedelta(hours=interval_hours * (i + 1))
        if next_timestamp not in existing_predictions:
            future_pred.append({"timestamp": next_timestamp, "prediction": round(value.item(), 2)})

    return future_pred

