import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List


DATA_RAW_DIR = os.getenv('DATA_RAW_DIR', '/app/code/data/data_raw')
DATA_PROCESSED_DIR = os.getenv('DATA_PROCESSED_DIR', '/app/code/data/data_processed')

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.dataframes = {}

    def load_klines_data(self) -> Dict[str, pd.DataFrame]:
       # print(f"Data directory: {self.data_dir}")
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Directory {self.data_dir} does not exist")
           
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json") and "data_klines" in filename:
                pair = filename.replace('_data_klines.json', '')
                filepath = os.path.join(self.data_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if 'data' in data and isinstance(data['data'], list):
                            df = pd.DataFrame(data['data'])
                            self.dataframes[pair] = df
                            print(f"Loaded {pair} data with {len(df)} rows")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        return self.dataframes

class TechnicalIndicators:
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, n=20, s=2) -> pd.DataFrame:
        """Calcul des bandes de Bollinger"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        df['BB_MA'] = typical_price.rolling(window=n).mean().round(2)
        stddev = typical_price.rolling(window=n).std()
        df['BB_UPPER'] = (df['BB_MA'] + (stddev * s)).round(2)
        df['BB_LOWER'] = (df['BB_MA'] - (stddev * s)).round(2)
        return df

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, n=14) -> pd.DataFrame:
        """Calcul du RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).round(2)
        loss = (-delta.where(delta < 0, 0)).round(2)
        
        avg_gain = gain.rolling(window=n).mean()
        avg_loss = loss.rolling(window=n).mean()
        
        rs = avg_gain / avg_loss
        df['RSI'] = (100 - (100 / (1 + rs))).round(2)
        return df

class CandlePatterns:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.calculate_basic_properties()

    def calculate_basic_properties(self):
        """Calcul des propriétés de base des bougies"""
        self.df['body_size'] = (abs(self.df['close'] - self.df['open'])).round(2)
        self.df['upper_shadow'] = (self.df['high'] - self.df[['open', 'close']].max(axis=1)).round(2)
        self.df['lower_shadow'] = (self.df[['open', 'close']].min(axis=1) - self.df['low']).round(2)
        self.df['candle_size'] = (self.df['high'] - self.df['low']).round(2)

    def identify_patterns(self) -> pd.DataFrame:
        """Identification des patterns de chandelier"""
        # Doji
        self.df['DOJI'] = (self.df['body_size'] <= self.df['candle_size'] * 0.1).astype(int)
        
        # Marteau et Étoile filante
        hammer_condition = (
            (self.df['lower_shadow'] > self.df['body_size'] * 2) & 
            (self.df['upper_shadow'] <= self.df['body_size'] * 0.5)
        )
        shooting_star_condition = (
            (self.df['upper_shadow'] > self.df['body_size'] * 2) & 
            (self.df['lower_shadow'] <= self.df['body_size'] * 0.5)
        )
        
        self.df['HAMMER'] = hammer_condition.astype(int)
        self.df['SHOOTING_STAR'] = shooting_star_condition.astype(int)
        
        return self.df

class DataProcessor:
    @staticmethod
    def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        # Conversion de base
        df['openTime'] = pd.to_datetime(df['openTime'], unit='ms')
        
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quoteVolume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
        
        # Ajout des indicateurs techniques
        df = TechnicalIndicators.calculate_bollinger_bands(df)
        df = TechnicalIndicators.calculate_rsi(df)
        
        
        # Ajout des patterns
        patterns = CandlePatterns(df)
        df = patterns.identify_patterns()
        
        # Calculs supplémentaires
        df['trend'] = (df['close'] > df['open']).astype(int).replace({0: -1, 1: 1})
        df['volume_price_ratio'] = (df['volume'] / df['close']).round(4)

        # Colonnes finales
        final_columns = [
            'openTime', 'open', 'high', 'low', 'close', 'volume',
            'trend', 'volume_price_ratio',
            'BB_MA', 'BB_UPPER', 'BB_LOWER',
            'RSI',
            'DOJI', 'HAMMER', 'SHOOTING_STAR'
        ]
        df = df[final_columns].dropna()
        return df

class DataSaver:
    @staticmethod
    def save_final_data(df: pd.DataFrame, symbol: str, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, f"{symbol}_final.json")
        
        df_json = df.copy()
        df_json['openTime'] = df_json['openTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        json_data = {
            'metadata': {
                'symbol': symbol,
                'rows': len(df),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'data': df_json.to_dict(orient='records')
        }
        
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=4)
        print(f"Saved processed data to {output_file}")

def main():
    data_dir = os.path.join(os.path.dirname(__file__), '../data/data_raw')
    output_dir = os.path.join(os.path.dirname(__file__), '../data/data_processed')
    
    loader = DataLoader(data_dir)
    dataframes = loader.load_klines_data()
    
    processor = DataProcessor()
    saver = DataSaver()
    
    for symbol, df in dataframes.items():
        processed_df = processor.process_dataframe(df)
        saver.save_final_data(processed_df, symbol, output_dir)

if __name__ == "__main__":
    main()