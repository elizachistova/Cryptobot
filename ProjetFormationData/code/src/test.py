import os

base_dir = '../config'
filename = 'config.json'
# Construct the full path
CONFIG_DIR = os.path.join(base_dir, filename)
DATA_RAW_DIR = os.path.join(os.path.dirname(__file__), '../data/data_raw')
CONFIG = os.path.join(os.path.dirname(__file__), '../config/config.json')
print(os.path.join(CONFIG))
print(CONFIG_DIR)
print(CONFIG)
""""
def fetch_data_klines(endpoint, symbol, interval, columns, limit, start_date=None, end_date=None):
    data_klines = []

    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=31)

    end_timestamp = int(end_date.timestamp() * 1000)
    start_timestamp = int(start_date.timestamp() * 1000)

    params = {'symbol': symbol, 'interval': interval, 'limit': limit, 'startTime': start_timestamp, 'endTime': end_timestamp}

    while True:
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code},{response.text}")
        klines = response.json()
        if not klines or klines[-1][0] > end_timestamp:
            break
        for kline in klines:
            kline_dict = dict(zip(columns, kline))
            data_klines.append(kline_dict)
        params['startTime'] = klines[-1][0] + 1

    print(f"Fetched {len(data_klines)} rows for {symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    data_klines.sort(key=lambda x: x['openTime'], reverse=True)
    
    return data_klines


data_klines = []

    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=31)

    end_timestamp = int(end_date.timestamp() * 1000)
    start_timestamp = int(start_date.timestamp() * 1000)

    params = {'symbol': symbol, 'interval': interval, 'limit': limit, 'startTime': start_timestamp, 'endTime': end_timestamp}

    while True:
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code},{response.text}")
        klines = response.json()
        if not klines or klines[-1][0] > end_timestamp:
            break
        for kline in klines:
            kline_dict = dict(zip(columns, kline))
            data_klines.append(kline_dict)
        params['startTime'] = klines[-1][0] + 1
"""