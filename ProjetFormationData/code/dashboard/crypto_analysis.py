import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from typing import Dict, List, Tuple, Any
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptoAnalyzer:
    def __init__(self, data_dir: str = '/app/ProjetFormationData/code/data/data_processed'):
        """
        Initialise l'analyseur de cryptomonnaies.
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers *_final.json
        """
        self.data_dir = data_dir
        self.available_symbols = self._get_available_symbols()
        
    def _get_available_symbols(self) -> List[str]:
        """Récupère la liste des symboles disponibles dans le répertoire de données."""
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith('_final.json')]
            return [f.replace('_final.json', '') for f in files]
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du répertoire: {e}")
            return []

    def load_data(self, symbol: str) -> pd.DataFrame:
        """
        Charge les données pour un symbole donné.
        
        Args:
            symbol: Le symbole de la cryptomonnaie (ex: 'BTCUSDT')
            
        Returns:
            DataFrame contenant les données
        """
        try:
            filepath = os.path.join(self.data_dir, f"{symbol}_final.json")
            with open(filepath, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data['data'])
            df['openTime'] = pd.to_datetime(df['openTime'])
            return df
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données pour {symbol}: {e}")
            return pd.DataFrame()

    def plot_price_volume(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Crée un graphique prix/volume.
        
        Args:
            df: DataFrame contenant les données
            symbol: Symbole de la cryptomonnaie
            
        Returns:
            Figure Plotly
        """
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

    def plot_technical_indicators(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Crée un graphique des indicateurs techniques.
        
        Args:
            df: DataFrame contenant les données
            symbol: Symbole de la cryptomonnaie
            
        Returns:
            Figure Plotly
        """
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} Prix et Bandes de Bollinger', 'RSI'),
            row_heights=[0.7, 0.3]
        )

        # Prix et Bandes de Bollinger
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

        for band, color in [('BB_MA', 'blue'), 
                          ('BB_UPPER', 'gray'), 
                          ('BB_LOWER', 'gray')]:
            fig.add_trace(
                go.Scatter(
                    x=df['openTime'],
                    y=df[band],
                    name=band,
                    line=dict(color=color, dash='dash' if band != 'BB_MA' else 'solid')
                ),
                row=1, col=1
            )

        # RSI
        fig.add_trace(
            go.Scatter(
                x=df['openTime'],
                y=df['RSI'],
                name='RSI',
                line=dict(color='purple')
            ),
            row=2, col=1
        )

        # Niveaux de surachat/survente
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        fig.update_layout(
            height=800,
            title_text=f"Analyse Technique {symbol}",
            xaxis_rangeslider_visible=False
        )

        return fig

 

    def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Effectue une analyse complète pour un symbole donné.
        
        Args:
            symbol: Symbole de la cryptomonnaie
            
        Returns:
            Dictionnaire contenant toutes les analyses
        """
        if symbol not in self.available_symbols:
            logger.error(f"Symbole {symbol} non disponible")
            return {}

        try:
            df = self.load_data(symbol)
            if df.empty:
                return {}

            results = {
                'symbol': symbol,
                'price_volume_chart': self.plot_price_volume(df, symbol),
                'technical_chart': self.plot_technical_indicators(df, symbol),
            }
            

            return results

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {symbol}: {e}")
            return {}

def main():
    # Exemple d'utilisation
    analyzer = CryptoAnalyzer()
    
    print("Symboles disponibles:", analyzer.available_symbols)
    
    # Analyse pour BTC
    btc_analysis = analyzer.analyze_symbol('ETHUSDT')
    
    if btc_analysis:
        # Afficher les graphiques
        btc_analysis['price_volume_chart'].show()
        btc_analysis['technical_chart'].show()

if __name__ == "__main__":
    main()