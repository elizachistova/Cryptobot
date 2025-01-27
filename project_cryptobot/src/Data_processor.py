import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
from extract import fetch_data_klines

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
        df['closeTime'] = pd.to_datetime(df['closeTime'], unit='ms')
        
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

