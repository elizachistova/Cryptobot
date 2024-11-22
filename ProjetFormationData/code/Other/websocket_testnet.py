import json
import asyncio
import websockets
from datetime import datetime
from typing import Optional, Dict, List, Callable
from websockets.exceptions import ConnectionClosed
import constants.defs as defs

class BinanceWebSocket:
    def __init__(self):
        self.ws_running = False
        self.ws_connection = None
        self.ws_callbacks = {}
        self.last_candle_was_closed = False

    async def _handle_websocket_message(self, message: str):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            if data.get('e') == 'kline':
                symbol = data['s']
                kline = data['k']
                timestamp = datetime.fromtimestamp(kline['t']/1000)
                
                # On affiche si c'est une bougie fermée ou la première mise à jour après une bougie fermée
                if kline['x'] or self.last_candle_was_closed:
                    if kline['x']:
                        print(f"\n=== CANDLE CLOSED ===")
                        self.last_candle_was_closed = True
                    else:
                        print(f"\n=== NEW CANDLE STARTED ===")
                        self.last_candle_was_closed = False
                        
                    print(f"Time: {timestamp.strftime('%d-%m-%Y %H:%M:%S')}")
                    print(f"Pair: {symbol}")
                    print(f"Open: {float(kline['o']):.2f}")
                    print(f"High: {float(kline['h']):.2f}")
                    print(f"Low: {float(kline['l']):.2f}")
                    print(f"Close: {float(kline['c']):.2f}")
                    print(f"Volume: {float(kline['v']):.8f}")
                    print(f"Trades: {kline['n']}")
                    print("-" * 50)
                    
                if kline['x']:  # Si c'est une bougie fermée
                    if self.ws_callbacks.get(f"{symbol.lower()}@kline_1m"):
                        await self.ws_callbacks[f"{symbol.lower()}@kline_1m"](data)
        except Exception as e:
            print(f"Error handling message: {e}")

    async def start_websocket(self, stream: str, callback: Callable):
        """Start WebSocket connection for a specific stream"""
        self.ws_running = True
        self.ws_callbacks[stream] = callback
        
        ws_url = f"{defs.WS_URL}/{stream}"
        
        while self.ws_running:
            try:
                async with websockets.connect(ws_url) as websocket:
                    self.ws_connection = websocket
                    print(f"WebSocket connected to {stream}")
                    
                    while self.ws_running:
                        message = await websocket.recv()
                        await self._handle_websocket_message(message)
                        
            except ConnectionClosed:
                print("WebSocket connection closed, reconnecting...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"WebSocket error: {e}")
                await asyncio.sleep(5)

    def stop_websocket(self):
        """Stop WebSocket connection"""
        self.ws_running = False
        self.ws_callbacks.clear()