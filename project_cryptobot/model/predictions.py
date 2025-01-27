import datetime
import joblib
import json
import numpy as np
import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

DATA_PREDICTED_DIR = os.path.join(os.path.dirname(__file__), '../data/data_predicted')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../config/config.json')

def load_data(symbol, features, scaler, model):
    """
    Loading data for prediction for model

    Parameters:
    Symbol - str: cryptocurrency
    features - str: all features used
    scaler: loaded scaler (minmax)
    model: best model loaded

    Output:
    input data and timestamp where prediction start
    """
    json_path = f'../data/data_processed/{symbol}_final.json'
    with open(json_path, 'r') as file:
        json_data = json.load(file)

    data = json_data['data']
    df = pd.DataFrame(data)
    df['openTime'] = pd.to_datetime(df['openTime'])
    df.set_index('openTime', inplace=True)
    df = df.sort_index()
    #shape of model input
    df = df[-model.input_shape[1]:]

    # Scale the data using the previously fitted scaler
    scaled_data = scaler.transform(df[features].values)  
    
    #reshaping to 3D as in model
    input_data = np.reshape(scaled_data, (scaled_data.shape[0], scaled_data.shape[1], 1))

    #getting latest timestamp for existing data
    last_timestamp = df.index.max() 
    
    return input_data, last_timestamp

def load_scalers(symbol):
    """
    Load the scalers for a symbol

    Parameters:
    symbol - str: cryptocurrency symbol to load the scalers

    Returns:
    scaler: MinMaxScaler for features;
    scaler_y: MinMaxScaler for target;
    """
    scaler_path = f"{MODEL_DIR}/{symbol}_scaler.pkl"
    scaler_y_path = f"{MODEL_DIR}/{symbol}_scaler_y.pkl"

    # Load scalers
    scaler = joblib.load(scaler_path)
    scaler_y = joblib.load(scaler_y_path)

    print(f"Scalers loaded: {scaler_path}, {scaler_y_path}")
    return scaler, scaler_y

def make_pred(symbol, model, scaler_y, latest_data, last_timestamp, interval_hours):
    """
    Making predictions

    Parameters:
    ----------
    model: Trained LSTM model
    last_data: np.array, Last sequence of input data from the dataset
    scaler_y: Scaler used to scale the target variable
    num_predictions - int: # of predictions to make
    interval_hours - int: time interval in hours for each prediction step

    Returns:
    future_predictions: predicted values
    """

    prediction = model.predict(latest_data, verbose=0)  
    #Inverse transform the predicted values to get the real values
    predicted_values = scaler_y.inverse_transform(prediction) 

    future_pred = []
    for i, value in enumerate(predicted_values):
        next_timestamp = last_timestamp + datetime.timedelta(hours=interval_hours * (i + 1))
        future_pred.append({"timestamp": next_timestamp, "prediction": round(value.item(),2)})

    return future_pred

def save_data(symbol, future_pred):
    """
    Saves the predcited data in the JSON file for each symbol.

    Parameters:
    ----------
    Symbol- str: Cryptocurrency pair (e.g. "BTCUSDT")
    Pred: prediction

    Returns:
    --------
    Prediction data loaded in data folder
    """
    filename = os.path.join(DATA_PREDICTED_DIR, f'{symbol}_data_predicted.json')
    json_data = {
            'metadata': {
                'symbol': symbol
            },
            'data': future_pred
        }
        
    with open(filename, 'w') as file:
        json.dump(json_data, file, indent=4, default = str)
    print(f"Prediction data saved to {filename}")    

def main():
    #Load configuration
    with open(CONFIG_DIR, 'r') as config_file:
        config = json.load(config_file)
    symbols = config["symbols"]
    features = ["open", "high", "low", "volume", "trend", "volume_price_ratio", "BB_MA", "BB_UPPER", "BB_LOWER", "RSI"]
    interval_hours = 4
    
    print(f"Symbols to process: {symbols}")
    for symbol in symbols:
        try:
            #get model
            model_path = f"{MODEL_DIR}/{symbol}_best_model.keras"
            model = load_model(model_path)
            print(f"Loaded model from {model_path}")

            # Load scaler
            scaler, scaler_y = load_scalers(symbol)

            # Get latest data
            latest_data, last_timestamp = load_data(symbol, features, scaler, model)

            # Predict future values
            future_pred = make_pred(symbol, model, scaler_y, latest_data, last_timestamp, interval_hours)

            # Save predictions
            save_data(symbol, future_pred)
            print("predictions saved for {symbol}")

        except Exception as e:
            print(f"An error occurred while processing {symbol}: {e}")


if __name__ == "__main__":
    main()
    