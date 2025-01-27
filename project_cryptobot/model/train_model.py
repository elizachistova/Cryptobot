import datetime
import joblib
import json
import keras_tuner as kt
from keras.layers import LSTM, Dense, Dropout, Input
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from tensorflow.keras.models import Sequential


DATA_PREDICTED_DIR = os.path.join(os.path.dirname(__file__), '../data/data_predicted')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../config/config.json')

def get_data(symbol):
    """
    Gets preprocessed data for a symbol

    Parameters:
    Symbol-str:cryptocurrency such as BTCUSDT

    Returns:
    Dataframe
    """
    json_path = f'../data/data_processed/{symbol}_final.json'
    with open(json_path, 'r') as file:
        json_data = json.load(file)
    data = json_data['data']
    df = pd.DataFrame(data)
    df['openTime'] = pd.to_datetime(df['openTime'])
    df.set_index('openTime', inplace=True)
    df = df.drop(df[df['volume']==0].index)
    return df

def model_preprocessing(df, features, target, test_size):
    """
    Preprocessing for LSTM model. 
    (a)scale the data using minmax scaler;
    (b) split it into training and testing sets;
    (c) reshapes to be 3D for LSTM input;
    
    Parameters:
        df - (pd.DataFrame): Input dataframe containing the data;
        features - (list): List of feature column names to be scaled;
        target - (str): Target column name to be scaled;
        test_size - test size for model training

    Returns:
        X_train - (np.array): Scaled and reshaped training features;
        X_test - (np.array): Scaled and reshaped testing features;
        y_train - (np.array): Scaled and reshaped training target;
        y_test - (np.array): Scaled and reshaped testing target;
        Scaler, scaler_y: minmax scalers
    """

    X_train, X_test, y_train, y_test = train_test_split(df[features].values, df[target].values, test_size=test_size, random_state=42, shuffle=False)
    #X_train, X_test, y_train, y_test = np.array(X_train), np.array(X_test), np.array(y_train), np.array(y_test)
    

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler_y = MinMaxScaler(feature_range=(0, 1))

    # Fit scalers on training data
    X_train = scaler.fit_transform(X_train)
    y_train = scaler_y.fit_transform(y_train.reshape(-1, 1))

    # Apply the same transformation to the test data
    X_test = scaler.transform(X_test)
    y_test = scaler_y.transform(y_test.reshape(-1, 1))
    print(X_train.shape)

    # Reshape input to be 3D (samples, timesteps, features)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    print(X_train.shape)

    return X_train, X_test, y_train, y_test, scaler, scaler_y


def model_builder(hp, input_shape):
    """
    Function that defines model space search

    Parameters:
     Hp is an object that we pass to the model-building function, that allows us to define the space search of the hyperparameters
    
    Return:
    model
    """
    model = Sequential()

    #Input Layer + first layer
    model.add(Input(shape=input_shape))
    model.add(LSTM(hp.Int('input_unit', min_value=32, max_value=512, step=32), return_sequences=True))
    
    #Hidden Layers
    for i in range(hp.Int('n_layers', 1, 4)):
        model.add(LSTM(hp.Int(f'lstm_{i}_units', min_value=32, max_value=512, step=32), return_sequences=True))
    
    #Final LSTM layer
    model.add(LSTM(hp.Int('layer_2_neurons', min_value=32, max_value=512, step=32), return_sequences=False))
    
    #Dropout layer to avoid overfitting. When dropout rate is 0.5 -> the dropout layer will hide half of the neurons every iteration.
    model.add(Dropout(hp.Float('Dropout_rate', min_value=0, max_value=0.5, step=0.1)))
    
    #Dense Layers
    model.add(Dense(30, activation=hp.Choice('dense_activation', values=['relu', 'sigmoid'], default='relu')))
    model.add(Dense(1, activation=hp.Choice('dense_activation', values=['relu', 'sigmoid'], default='relu')))
   
    model.compile(loss='mean_squared_error', optimizer='adam', metrics = ['mse'])
    return model

def train_and_save_model(symbol, X_train, y_train, X_test, y_test, input_shape):
    print("Starting the tuning")
    tuner = kt.RandomSearch(lambda hp: model_builder(hp, input_shape=input_shape), 
                            objective="mse", 
                            max_trials = 4, 
                            executions_per_trial = 2, 
                            directory=MODEL_DIR,
                            project_name=f"{symbol}_lstm_tuning")
    tuner.search(x=X_train, 
                 y=y_train, 
                 epochs = 10, 
                 batch_size =256, 
                 validation_data=(X_test, y_test))
    
    print("Hyperparameter tuning complete.")
    best_model = tuner.get_best_models(num_models=1)[0]
    best_trials = tuner.oracle.get_best_trials(num_trials=1)  # List of best trials
    best_trial = best_trials[0]  # Get the first (best) trial
    
    # Extract the best MSE value from the best trial
    best_mse = best_trial.metrics.get_best_value("mse") 

    tuner.results_summary()
    best_model.save(f"{MODEL_DIR}/{symbol}_best_model.keras")
    print(f"Best model for {symbol} saved with mse {best_mse:.4f}!")
    

def save_scalers(scaler, scaler_y, symbol):
    """
    Save the scalers for predictions later

    Parameters:
    scaler: MinMaxScaler for features;
    scaler_y: MinMaxScaler for target;
    symbol - str: Symbol for cryptocurrency
    """
    scaler_path = f"{MODEL_DIR}/{symbol}_scaler.pkl"
    scaler_y_path = f"{MODEL_DIR}/{symbol}_scaler_y.pkl"

    # Save scalers
    joblib.dump(scaler, scaler_path)
    joblib.dump(scaler_y, scaler_y_path)

    print(f"Scalers saved: {scaler_path}, {scaler_y_path}")


def main():
    #Load configuration
    with open(CONFIG_DIR, 'r') as config_file:
        config = json.load(config_file)
    symbols = config["symbols"]
    test_size = 0.05
    print(f"Symbols to process: {symbols}")

    #Define features and target
    features =  ["open","high","low","volume","trend","volume_price_ratio","BB_MA","BB_UPPER","BB_LOWER","RSI"]
    target = ["close"]

    for symbol in symbols:
        try:
            df = get_data(symbol)
            X_train, X_test, y_train, y_test, scaler, scaler_y = model_preprocessing(df, features, target, test_size)
            save_scalers(scaler, scaler_y, symbol)
            input_shape = (X_train.shape[1],X_train.shape[2])
            train_and_save_model(symbol, X_train, y_train, X_test, y_test, input_shape) 
        except Exception as e:
            print(f"Error processing {symbol}: {e}")        

    print("\nProcessing complete for all symbols.")

if __name__ == "__main__":
    main()
    


