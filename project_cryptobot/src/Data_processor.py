import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv
from pymongo import MongoClient
import os

class MongoDataHandler:
    def __init__(self):
        # Charger les variables d'environnement
        dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
        load_dotenv(dotenv_path)
        
        # Connexion MongoDB
        self.client = MongoClient(
            host="mongodb",
            port=int(os.getenv("PORT", "27017").strip(",")),
            username=os.getenv("USERNAME", "").strip(),
            password=os.getenv("PASSWORD", "").strip()
        )
        self.db = self.client.Cryptobot

    def get_unprocessed_data(self, symbol: str) -> pd.DataFrame:
        """Récupère les données non traitées depuis raw_market_data"""
        # Trouver le dernier timestamp traité dans market_data
        last_processed = self.db.market_data.find_one(
            {"symbol": symbol},
            sort=[("openTime", -1)]
        )
        
        # Construire la requête pour les nouvelles données
        query = {"symbol": symbol}
        if last_processed:
            query["openTime"] = {"$gt": last_processed["openTime"]}
        
        # Récupérer les nouvelles données
        cursor = self.db.raw_market_data.find(
            query,
            {"_id": 0}  # Exclure le champ _id
        ).sort("openTime", 1)
        
        # Convertir en DataFrame
        df = pd.DataFrame(list(cursor))
        
        if not df.empty:
            # Conversion des types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col])
            
        return df

    def save_processed_data(self, symbol: str, df: pd.DataFrame):
        """Sauvegarde les données traitées dans market_data"""
        if df.empty:
            return
            
        # Préparation des documents
        documents = []
        for _, row in df.iterrows():
            indicator = {
                "BB_MA": row["BB_MA"],
                "BB_UPPER": row["BB_UPPER"],
                "BB_LOWER": row["BB_LOWER"],
                "RSI": row["RSI"],
                "DOJI": row["DOJI"],
                "HAMMER": row["HAMMER"],
                "SHOOTING_STAR": row["SHOOTING_STAR"]
            }
            
            document = {
                "symbol": symbol,
                "openTime": row["openTime"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
                "trend": row["trend"],
                "volume_price_ratio": row["volume_price_ratio"],
                "indicator": indicator,
                "last_updated": datetime.now()
            }
            documents.append(document)
        
        # Insertion dans MongoDB
        if documents:
            self.db.market_data.insert_many(documents)
            print(f"Inserted {len(documents)} processed records for {symbol}")

    def close(self):
        if self.client:
            self.client.close()


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
        if df.empty:
            return df
            
        # Calculs supplémentaires
        df['trend'] = (df['close'] > df['open']).astype(int).replace({0: -1, 1: 1})
        df['volume_price_ratio'] = (df['volume'] / df['close']).round(4)
        
        # Ajout des indicateurs techniques
        df = TechnicalIndicators.calculate_bollinger_bands(df)
        df = TechnicalIndicators.calculate_rsi(df)
        
        # Ajout des patterns
        patterns = CandlePatterns(df)
        df = patterns.identify_patterns()
        
        return df.dropna()


def main():
    try:
        # Initialisation du gestionnaire de données MongoDB
        mongo_handler = MongoDataHandler()
        
        # Récupérer la liste des symboles depuis raw_market_data
        symbols = mongo_handler.db.raw_market_data.distinct("symbol")
        
        processor = DataProcessor()
        
        for symbol in symbols:
            try:
                # Récupérer les nouvelles données non traitées
                df = mongo_handler.get_unprocessed_data(symbol)
                
                if not df.empty:
                    # Traiter les données
                    processed_df = processor.process_dataframe(df)
                    
                    # Sauvegarder les résultats
                    mongo_handler.save_processed_data(symbol, processed_df)
                else:
                    print(f"Pas de nouvelles données à traiter pour {symbol}")
                    
            except Exception as e:
                print(f"Erreur lors du traitement de {symbol}: {e}")
                continue
                
    except Exception as e:
        print(f"Erreur générale: {e}")
        
    finally:
        mongo_handler.close()


if __name__ == "__main__":
    main()