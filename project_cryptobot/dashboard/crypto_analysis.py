from pymongo import MongoClient
import pandas as pd
import json
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TechnicalIndicators:
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, n=20, s=2) -> pd.DataFrame:
        """
        Calcule les bandes de Bollinger
        n: période
        s: nombre d'écarts-types
        """
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            raise ValueError("DataFrame doit contenir les colonnes 'high', 'low', 'close'")

        # Utilise le prix typique pour le calcul
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # Moyenne mobile
        df['BB_MA'] = typical_price.rolling(window=n).mean()
        
        # Écart-type
        stddev = typical_price.rolling(window=n).std()
        
        # Bandes supérieure et inférieure
        df['BB_UPPER'] = df['BB_MA'] + (stddev * s)
        df['BB_LOWER'] = df['BB_MA'] - (stddev * s)
        
        # Arrondir les valeurs
        for col in ['BB_MA', 'BB_UPPER', 'BB_LOWER']:
            df[col] = df[col].round(2)
            
        return df

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, n=14) -> pd.DataFrame:
        """
        Calcule le RSI (Relative Strength Index)
        n: période
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame doit contenir la colonne 'close'")

        # Calcul des variations
        delta = df['close'].diff()
        
        # Sépare les gains et les pertes
        gain = (delta.where(delta > 0, 0)).round(2)
        loss = (-delta.where(delta < 0, 0)).round(2)
        
        # Calcul des moyennes
        avg_gain = gain.rolling(window=n, min_periods=1).mean()
        avg_loss = loss.rolling(window=n, min_periods=1).mean()
        
        # Calcul du RSI
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df['RSI'] = df['RSI'].round(2)
        
        return df

    @staticmethod
    def calculate_ema(df: pd.DataFrame, periods=[9, 20, 50]) -> pd.DataFrame:
        """
        Calcule les moyennes mobiles exponentielles
        periods: liste des périodes à calculer
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame doit contenir la colonne 'close'")
            
        for period in periods:
            df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean().round(2)
        
        return df

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
        """
        Calcule le MACD (Moving Average Convergence Divergence)
        fast: période rapide
        slow: période lente
        signal: période du signal
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame doit contenir la colonne 'close'")
            
        # Calcul des EMA
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        
        # Calcul du MACD
        df['MACD_LINE'] = (exp1 - exp2).round(2)
        df['MACD_SIGNAL'] = df['MACD_LINE'].ewm(span=signal, adjust=False).mean().round(2)
        df['MACD_HIST'] = (df['MACD_LINE'] - df['MACD_SIGNAL']).round(2)
        
        return df

    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, k_period=14, d_period=3) -> pd.DataFrame:
        """
        Calcule l'oscillateur stochastique
        k_period: période pour %K
        d_period: période pour %D
        """
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            raise ValueError("DataFrame doit contenir les colonnes 'high', 'low', 'close'")
            
        # Calcul du %K
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        df['STOCH_K'] = ((df['close'] - lowest_low) / (highest_high - lowest_low) * 100).round(2)
        
        # Calcul du %D (moyenne mobile simple du %K)
        df['STOCH_D'] = df['STOCH_K'].rolling(window=d_period).mean().round(2)
        
        return df
    

class CryptoAnalyzer:
    def __init__(self, mongodb_uri):
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.db = None
        self.available_symbols = []
        self._init_connection()

    def _init_connection(self):
        """Initialise la connexion MongoDB"""
        try:
            logger.info(f"Tentative de connexion à MongoDB...")
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client.Cryptobot
            logger.info(f"Connexion à MongoDB établie avec succès")
            self.init_symbols()
            collections = self.db.list_collection_names()
            logger.info(f"Collections disponibles: {collections}")

            count = self.db.market_data.count_documents({})
            logger.info(f"Nombre de documents dans market_data: {count}")


        except Exception as e:
            logger.error(f"Erreur de connexion à MongoDB: {e}")
            raise

    def init_symbols(self):
        """Initialise la liste des symboles disponibles"""
        try:

            collections = self.db.list_collection_names()
            logger.info(f"Collections disponibles: {collections}")

            count = self.db.market_data.count_documents({})
            logger.info(f"Nombre de documents dans market_data: {count}")


            self.available_symbols = self.db.market_data.distinct("symbol")
            logger.info(f"Symboles disponibles: {self.available_symbols}")
            return self.available_symbols
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des symboles: {e}")
            return []

    def get_timeframe_start_date(self, timeframe: str) -> datetime:
        """Calcule la date de début en fonction du timeframe"""
        end_date = datetime.now()
        timeframe_mapping = {
            '1D': timedelta(days=1),
            '7D': timedelta(days=7),
            '1M': timedelta(days=30),
            '3M': timedelta(days=90),
            '6M': timedelta(days=180),
            '1Y': timedelta(days=365),
            'ALL': None
        }
        
        if timeframe not in timeframe_mapping:
            return end_date - timedelta(days=1)  # Par défaut : 1 jour
            
        delta = timeframe_mapping[timeframe]
        return None if delta is None else end_date - delta

    def load_data(self, symbol: str, timeframe: str = '1Y') -> pd.DataFrame:
        try:
            logger.info(f"Chargement des données pour {symbol} sur {timeframe}")
            
            # Obtenir la dernière date disponible
            latest_record = self.db.market_data.find_one(
                {"symbol": symbol},
                sort=[("openTime", -1)]
            )
            if not latest_record:
                return pd.DataFrame()
                
            end_date = latest_record['openTime']
            logger.info(f"Dernière date disponible: {end_date}")
            
            # Calculer la date de début en fonction du timeframe
            delta = self.get_timeframe_delta(timeframe)
            start_date = end_date - delta if delta else None
            
            # Construire la requête MongoDB
            query = {"symbol": symbol}
            if start_date:
                query["openTime"] = {
                    "$gte": start_date,
                    "$lte": end_date
                }
                
            logger.info(f"Requête MongoDB: {query}")
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
            cursor = self.db.market_data.find(query,projection).sort("openTime", 1)
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
            
            #documents = list(cursor)
            logger.info(f"Nombre de documents récupérés: {len(df)}")
            

            # Conversion des types
            df['openTime'] = pd.to_datetime(df['openTime'])
          
           # df['openTime'] = pd.to_datetime(df['openTime'])
            numeric_cols = ['open', 'high', 'low', 'close', 'volume',
                        'trend', 'volume_price_ratio', 'BB_MA', 
                        'BB_UPPER', 'BB_LOWER', 'RSI']
            
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"Données chargées: {len(df)} entrées de {df['openTime'].min()} à {df['openTime'].max()}")
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            raise

    def get_timeframe_delta(self, timeframe: str) -> timedelta:
        """Helper pour convertir le timeframe en timedelta"""
        timeframe_mapping = {
            '1D': timedelta(days=1),
            '7D': timedelta(days=7),
            '1M': timedelta(days=30),
            '3M': timedelta(days=90),
            '6M': timedelta(days=180),
            '1Y': timedelta(days=365),
            'ALL': None
        }
        return timeframe_mapping.get(timeframe, timedelta(days=1))
    
    def calculate_24h_stats(self, df: pd.DataFrame) -> dict:
        """Calcule les statistiques sur 24h"""
        try:
            if df.empty:
                return {}
                
            # S'assurer que nous avons des données sur 24h
            latest_timestamp = df['openTime'].max()
            last_24h = df[df['openTime'] >= (latest_timestamp - timedelta(days=1))]

            if last_24h.empty:
                return {}
                
            current_price = float(df['close'].iloc[-1])
            day_open = float(last_24h['open'].iloc[0])
            
            price_change = current_price - day_open
            price_change_percent = (price_change / day_open) * 100
            
            return {
                'current_price': current_price,
                'price_change_24h': price_change,
                'price_change_percentage_24h': price_change_percent,
                'high_24h': float(last_24h['high'].max()),
                'low_24h': float(last_24h['low'].min()),
                'volume_24h': float(last_24h['volume'].sum())
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques 24h: {e}")
            return {}

    def analyze_symbol(self, symbol: str, timeframe: str = '1Y', indicators: List[str] = None) -> Dict[str, Any]:
        """
        Analyse un symbole avec les indicateurs spécifiés
        
        Args:
            symbol (str): Le symbole à analyser
            timeframe (str): La période d'analyse ('1D', '7D', '1M', '3M', '6M', '1Y', 'ALL')
            indicators (List[str]): Liste des indicateurs à calculer et afficher
            
        Returns:
            Dict[str, Any]: Résultats de l'analyse incluant les graphiques et statistiques
        """
        try:
            # Ensure indicators is a list
            if isinstance(indicators, str):
                indicators = indicators.split(',')
            elif indicators is None:
                indicators = ['BB']  # default indicators

            if symbol not in self.available_symbols:
                self.init_symbols()
                if symbol not in self.available_symbols:
                    logger.error(f"Symbole {symbol} non disponible")
                    return {}

            logger.info(f"Début de l'analyse pour {symbol} avec indicateurs: {indicators}")
            df = self.load_data(symbol, timeframe)
            
            if df.empty:
                logger.error(f"DataFrame vide pour {symbol}")
                return {}

            # Calcul des indicateurs techniques
            technical_indicator = TechnicalIndicators()
            
            if 'BB' in indicators:
                df = technical_indicator.calculate_bollinger_bands(df)
            if 'RSI' in indicators:
                df = technical_indicator.calculate_rsi(df)
            if 'EMA' in indicators:
                df = technical_indicator.calculate_ema(df)
            if 'MACD' in indicators:
                df = technical_indicator.calculate_macd(df)
            if 'STOCH' in indicators:
                df = technical_indicator.calculate_stochastic(df)

            # Calculer les statistiques sur 24h
            stats_24h = self.calculate_24h_stats(df)
            
            # Créer les graphiques
            technical_chart = self.plot_technical_indicators(df, symbol, indicators)

            # Assembler les résultats
            results = {
                'symbol': symbol,
                'timeframe': timeframe,
                'technical_chart': json.dumps(technical_chart, cls=plotly.utils.PlotlyJSONEncoder),
                'last_update': df['openTime'].max().strftime("%Y-%m-%d %H:%M:%S"),
                'current_price': df['close'].iloc[-1] if not df.empty else None,
                'price_change_24h': stats_24h.get('price_change_24h', None),
                'price_change_percentage_24h': stats_24h.get('price_change_percentage_24h', None),
                'high_24h': stats_24h.get('high_24h', None),
                'low_24h': stats_24h.get('low_24h', None),
                'volume_24h': stats_24h.get('volume_24h', None)
            }
            
            logger.info(f"Résultats des 3 dernières analyses: {dict(list(results.items())[-3:])}")
            return results


        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {symbol}: {e}")
            return {}

    def init_symbols(self):
        """Initialise la liste des symboles disponibles"""
        try:
            self.available_symbols = self.db.market_data.distinct("symbol")
            logger.info(f"Symboles disponibles: {self.available_symbols}")
            return self.available_symbols
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des symboles: {e}")
            return []
        
    def plot_technical_indicators(self, df: pd.DataFrame, symbol: str, indicators: List[str] = None) -> go.Figure:
        """Crée un graphique avec les indicateurs techniques"""
        if df.empty:
            raise ValueError("DataFrame est vide")

        # Configuration des sous-graphiques basée sur les indicateurs
        subplot_rows = 1  # Prix principale
        if any(ind in indicators for ind in ['RSI', 'MACD', 'STOCH']):
            subplot_rows += 1

        # Création de la figure avec les sous-graphiques
        fig = make_subplots(
            rows=subplot_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7] + [0.3] * (subplot_rows - 1),            
        )

        # Graphique des prix (chandelier)
        fig.add_trace(
            go.Candlestick(
                x=df['openTime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Prix'
            ),
            row=1, col=1
        )

        # Bandes de Bollinger (superposées au prix) ou EMA
        if 'BB' in indicators and all(col in df.columns for col in ['BB_UPPER', 'BB_LOWER', 'BB_MA']):
            for band, name, color in [
                ('BB_UPPER', 'BB Upper', '#ADD8E6'),
                ('BB_LOWER', 'BB Lower', '#ADD8E6'),
                ('BB_MA', 'BB MA', '#FFD7AD')
            ]:
                fig.add_trace(
                    go.Scatter(
                        x=df['openTime'],
                        y=df[band],
                        name=name,
                        line=dict(color=color, width=1),
                        opacity=0.7
                    ),
                    row=1, col=1
                )
        elif 'EMA' in indicators:
            for period in [9, 20, 50]:
                if f'EMA_{period}' in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df['openTime'],
                            y=df[f'EMA_{period}'],
                            name=f'EMA {period}',
                            line=dict(width=1)
                        ),
                        row=1, col=1
                    )

        current_row = 1
        # Si un autre indicateur est présent, l'ajouter dans un subplot
        if any(ind in indicators for ind in ['RSI', 'MACD', 'STOCH']):
            current_row += 1

            # RSI
            if 'RSI' in indicators and 'RSI' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['openTime'],
                        y=df['RSI'],
                        name='RSI',
                        line=dict(color='#9370DB', width=1)
                    ),
                    row=current_row, col=1
                )
                
                # Niveaux de surachat/survente
                for level in [30, 70]:
                    fig.add_hline(
                        y=level,
                        line_dash="dash",
                        line_color="#808080",
                        row=current_row,
                        col=1
                    )

            # MACD
            if 'MACD' in indicators and all(col in df.columns for col in ['MACD_LINE', 'MACD_SIGNAL', 'MACD_HIST']):
                # MACD Line
                fig.add_trace(
                    go.Scatter(
                        x=df['openTime'],
                        y=df['MACD_LINE'],
                        name='MACD',
                        line=dict(color='#1E90FF', width=1)
                    ),
                    row=current_row, col=1
                )
                # Signal Line
                fig.add_trace(
                    go.Scatter(
                        x=df['openTime'],
                        y=df['MACD_SIGNAL'],
                        name='Signal',
                        line=dict(color='#FFA500', width=1)
                    ),
                    row=current_row, col=1
                )
                # Histogram
                fig.add_trace(
                    go.Bar(
                        x=df['openTime'],
                        y=df['MACD_HIST'],
                        name='MACD Hist',
                        marker_color='#008000'
                    ),
                    row=current_row, col=1
                )

            # Stochastique
            if 'STOCH' in indicators and all(col in df.columns for col in ['STOCH_K', 'STOCH_D']):
                # %K
                fig.add_trace(
                    go.Scatter(
                        x=df['openTime'],
                        y=df['STOCH_K'],
                        name='%K',
                        line=dict(color='#1E90FF', width=1)
                    ),
                    row=current_row, col=1
                )
                # %D
                fig.add_trace(
                    go.Scatter(
                        x=df['openTime'],
                        y=df['STOCH_D'],
                        name='%D',
                        line=dict(color='#FFA500', width=1)
                    ),
                    row=current_row, col=1
                )
                # Niveaux de surachat/survente
                for level in [20, 80]:
                    fig.add_hline(
                        y=level,
                        line_dash="dash",
                        line_color="#808080",
                        row=current_row,
                        col=1
                    )

        # Configuration du layout
        fig.update_layout(
            height=600 + (200 * (subplot_rows - 1)),  # Hauteur dynamique            
            showlegend=True,
            xaxis_rangeslider_visible=False,
            paper_bgcolor='#161B22',
            plot_bgcolor='#161B22',
            font=dict(color='#E6EDF3')
        )

        # Configuration des axes Y
        fig.update_yaxes(title_text="Prix", row=1, col=1)
        
        # Titre dynamique de la deuxième ligne
        if subplot_rows > 1:
            if 'RSI' in indicators:
                fig.update_yaxes(title_text="RSI", row=2, col=1)
            elif 'MACD' in indicators:
                fig.update_yaxes(title_text="MACD", row=2, col=1)
            elif 'STOCH' in indicators:
                fig.update_yaxes(title_text="Stochastique", row=2, col=1)

        return fig

    def plot_price_volume(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        try:
            pattern_config = {
                'DOJI': {
                    'marker_symbol': 'arrow-down-open',
                    'marker_color': 'blue',
                    'marker_size': 12,
                    'offset': 1.01
                },
                'HAMMER': {
                    'marker_symbol': 'triangle-up',
                    'marker_color': 'green',
                    'marker_size': 12,
                    'offset': 1.02
                },
                'SHOOTING_STAR': {
                    'marker_symbol': 'triangle-down',
                    'marker_color': 'red',
                    'marker_size': 12,
                    'offset': 1.03
                }
            }

            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(f'{symbol} Prix', 'Volume'),
                row_heights=[0.7, 0.3]
            )

            # Graphique des prix
            fig.add_trace(
                go.Candlestick(
                    x=df['openTime'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Prix'
                ),
                row=1, col=1
            )

            # Ajout des patterns
            for pattern_name, config in pattern_config.items():
                if pattern_name in df.columns:
                    pattern_points = df[df[pattern_name] == 1]
                    if not pattern_points.empty:
                        fig.add_trace(
                            go.Scatter(
                                x=pattern_points['openTime'],
                                y=pattern_points['high'] * config['offset'],
                                mode='markers',
                                name=pattern_name,
                                marker=dict(
                                    symbol=config['marker_symbol'],
                                    size=config['marker_size'],
                                    color=config['marker_color']
                                )
                            ),
                            row=1, col=1
                        )

            # Graphique du volume
            colors = ['red' if row.close < row.open else 'green' 
                     for idx, row in df.iterrows()]
            
            fig.add_trace(
                go.Bar(
                    x=df['openTime'],
                    y=df['volume'],
                    marker_color=colors,
                    name='Volume'
                ),
                row=2, col=1
            )

            fig.update_layout(
                height=800,
                title_text=f"Analyse Prix/Volume {symbol}",
                xaxis_rangeslider_visible=False
            )

            return fig
        
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique prix/volume: {e}")
            raise
