import requests

def get_data_market(market_data):
    """
    Cette fonction interroge l'API de Binance pour obtenir les prix actuels des données marchés de cryptomonnaies.
    La fonction, `get_data_market`,prend en entrée une liste de symboles de marché (par exemple, 'BTCUSDT'
    et 'ETHBTC') et récupère les données de prix pour chacune de ces paires.

    La fonction envoie une requête distincte pour chaque symbole et compile 
    les résultats dans une liste. En cas d'erreur (par exemple, une connexion échouée ou 
    un symbole invalide), le script capture l'exception et affiche un message d'erreur.

    Après avoir récupéré les données, le script extrait et affiche les informations de prix 
    pour chaque paire spécifique en filtrant la liste de résultats. Cela permet une récupération 
    de données flexible et rapide pour plusieurs paires de marché en une seule exécution.
    """

    url = "https://www.binance.com/api/v3/ticker"
    data_market = []
    try:
        for symbol in market_data:
            req = requests.get(url, params={'symbol':symbol})
            data = req.json()
            data_market.append(data) 
        return data_market

    except Exception as e:
        print(f"Impossible de récupérer les données {e}")
        return None

def historical_data(symbol, interval, starTime=None, endTime=None):
    """
    Récupération des données historiques du marché.

    Étapes principales :
    1. Construit l'URL de l'API Binance pour obtenir les données historiques de trading.
    2. Définit les paramètres de requête, y compris :
        - `symbol` : la paire de trading (ex. : 'BTCUSDT').
        - `interval` : l'intervalle de temps des bougies (ex. : '1m', '1h').
        - `starTime` : heure de début (en timestamp UNIX, facultatif).
        - `endTime` : heure de fin (en timestamp UNIX, facultatif).
        - `limit` : nombre maximum de points de données à récupérer (par défaut :500; max : 1000).
    3. Effectue une requête GET à l'API Binance pour récupérer les données au format JSON.
    4. Gère les erreurs en capturant les exceptions et en affichant un message d'erreur en cas d'échec.

    """
    url ="https://www.binance.com/api/v3/klines"
    param = {
        'symbol': symbol,
        'interval': interval,
        'starTime': starTime,
        'endTime': endTime,
        'timeZone': 0,
        'limit':1000
    }

    try:
        req = requests.get(url, params=param)
        req.raise_for_status
        return req.json()
    
    except Exception as e:
        print(f"Erreur de récupération des données historiques{e}")
        return None



donnee = ['BTCUSDT','ETHBTC']
market = get_data_market(donnee)
# print(market)

btc_usdt = [element for element in market if element['symbol'] == 'BTCUSDT']
print('Les données du BTC-USDT:',btc_usdt)
print("\n")

eth_btc = [element for element in market if element['symbol'] == 'ETHBTC']
print('Les données du ETH-BTC:',eth_btc)
print("\n")

symbol = "BTCUSDT"
interval = "1m"
data_historical = historical_data(symbol, interval)
print("Les Données historiques:\n")
print(data_historical)