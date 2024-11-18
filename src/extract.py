import datetime
import requests
import json
import os
import pandas as pd
import time

def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

config = load_config()

# API endpoint
endpoint = 'https://api1.binance.com/api/v3/klines'

# Parameters from config 
symbols = config["symbols"]
interval = config["interval"]
columns = config["columns"]
limit = config["limit"]

def fetch_data(symbol, interval, start_time):
      """ 
      This function fetches historical Binance Data

      Parameters:
      - symbol
      - interval

      Returns:
      A DataFrame for further processing
      """
      data=[]
      params = {'symbol': symbol, 
                'interval': interval, 
                'limit': limit,
                'startTime': start_time}
      
      while True:
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
                raise Exception(f"Error: {response.status_code},{response.text}")

        klines = json.loads(response.text)
        if not klines:
                break
        
        for kline in klines:
            kline_dict = dict(zip(columns, kline))
            data.append(kline_dict)

        #update starttime
        params['startTime'] = int(klines[-1][0]) + 1
        time.sleep(0.1)

      return data

# Storing response data in json file
def load_data(symbol):
    """
    Load the fetched data from the JSON file for a symbol
    """
    filename = os.path.join("../data", f'{symbol}_historical_data.json')
    
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_data = json.load(file)
            return existing_data
    else:
        return {'columns': columns, 'data': []}

# Updating data
def update_data(symbol):
    """
    Update historical data daily
    """
    existing_data = load_data(symbol)
    
    if existing_data['data']:
        last_timestamp = existing_data['data'][-1]['open_time']
    else:
        last_timestamp = 0
    
    # Fetch new data from the last timestamp
    new_data = fetch_data(symbol, interval, last_timestamp)
    
    # Check if new data is returned
    if new_data:
        # Append the new data to the existing data
        existing_data['data'].extend(new_data)
        
        # Save the updated data back to the JSON file
        filename = os.path.join("../data", f'{symbol}_historical_data.json')

        with open(filename, 'w') as file:
            json.dump(existing_data, file, indent=4)
        
        print(f"Data for {symbol} updated successfully!")
    else:
        print(f"No new data available for {symbol}.")


# Run the update for each symbol
try:
    for symbol in symbols:
        update_data(symbol)

except Exception as e:
    print("Error occuring:", e)  
