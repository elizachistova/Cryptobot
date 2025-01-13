from binance.client import Client
import websockets
import asyncio
import json
import pandas as pd
from datetime import datetime
import sys
import os

# Ajouter le chemin racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import constants.defs as defs

class MarketData:
    def __init__(self):
        # Initialisation du client Binance
        self.client = Client(defs.API_KEY, defs.API_SECRET, testnet=True)
        self.ws_running = False
        
    def get_historical_data(self, symbol: str, interval='1h', limit=100):
        """Récupère les données historiques"""
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 
                'volume', 'close_time', 'quote_volume', 'trades',
                'taker_base_vol', 'taker_quote_vol', 'ignore'
            ])
            
            # Convertir les types de données
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
                
            print(f"\nHistorical data for {symbol}:")
            print(df.tail(1).to_string())
            return df
            
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return None

    async def start_live_data(self, symbols=['btcusdt', 'ethusdt', 'ethbtc']):
        """Démarre le flux de données en direct"""
        self.ws_running = True
        streams = [f"{symbol}@kline_1m" for symbol in symbols]
        ws_url = f"{defs.WS_URL}/{''.join(s for s in streams)}"
        
        while self.ws_running:
            try:
                async with websockets.connect(ws_url) as ws:
                    print(f"\nConnected to live data feed for {symbols}")
                    
                    while self.ws_running:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        
                        if data['e'] == 'kline' and data['k']['x']:  # Si la bougie est fermée
                            symbol = data['s']
                            k = data['k']
                            
                            print(f"\n=== {symbol} New Candle ===")
                            print(f"Time: {datetime.fromtimestamp(k['t']/1000)}")
                            print(f"Open: {float(k['o']):.2f}")
                            print(f"High: {float(k['h']):.2f}")
                            print(f"Low: {float(k['l']):.2f}")
                            print(f"Close: {float(k['c']):.2f}")
                            print(f"Volume: {float(k['v']):.8f}")
                            print("-" * 40)
                            
            except Exception as e:
                print(f"WebSocket error: {e}")
                await asyncio.sleep(5)  # Attendre 5 secondes avant de réessayer

    def stop_live_data(self):
        """Arrête le flux de données en direct"""
        self.ws_running = False

async def main():
    # Création de l'instance
    md = MarketData()
    
    # Récupérer les données historiques pour chaque symbole
    symbols = ['BTCUSDT', 'ETHUSDT', 'ETHBTC']
    for symbol in symbols:
        df = md.get_historical_data(symbol)
        if df is not None:
            # Optionnel: sauvegarder les données dans un fichier
            df.to_csv(f'data/{symbol}_historical.csv', index=False)
    
    # Démarrer le flux en direct
    try:
        print("\nStarting live data stream. Press Ctrl+C to stop.")
        await md.start_live_data([s.lower() for s in symbols])
    except KeyboardInterrupt:
        print("\nStopping live data stream...")
        md.stop_live_data()
    except Exception as e:
        print(f"\nError in main loop: {e}")
        md.stop_live_data()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"\nProgram error: {e}")