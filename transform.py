import pandas as pd
from extract import *

def data_pre_processing():
    """
    Cette fonction effectue le pré-traitement des données du marché pour les rendre 
    prêtes à l'analyse ou à l'entraînement d'un modèle.
    
    Étapes principales :
    1. Crée un DataFrame à partir des données du marché (`market`) en spécifiant les colonnes clés liées aux changements de prix, volumes et autres paramètres de trading.
    2. Convertit les colonnes numériques (telles que `priceChange`, `weightedAvgPrice`, etc.) en type `float` pour garantir la cohérence des calculs.
    3. Arrondit les valeurs numériques à deux décimales pour uniformiser les données et réduire la complexité des calculs.
    4. Retourne un DataFrame propre, structuré, et prêt pour des analyses approfondies ou pour servir de jeu de données d'entraînement à un modèle.

    Retourne :
        Un DataFrame contenant les données pré-traitées.
    """
    data = market
    
     # Création du DataFrame
    df = pd.DataFrame(data, columns=['symbol','priceChange', 'priceChangePercent', 'weightedAvgPrice',
                                      'openPrice', 'highPrice', 'lowPrice', 'lastPrice', 'volume', 
                                      'quoteVolume', 'openTime', 'closeTime', 'firstId', 'lastId', 'count'])
    
    # Nettoyage des données
    df.dtypes
    df[['priceChange','priceChangePercent','weightedAvgPrice','openPrice',
        'highPrice','lowPrice','lastPrice','volume']] = df[['priceChange','priceChangePercent','weightedAvgPrice','openPrice',
                                                            'highPrice','lowPrice','lastPrice','volume']].astype(float)
    
    df[['priceChange','priceChangePercent','weightedAvgPrice','openPrice',
        'highPrice','lowPrice','lastPrice','volume']] = df[['priceChange','priceChangePercent','weightedAvgPrice','openPrice',
                                                            'highPrice','lowPrice','lastPrice','volume']].round(2)
    return df


def pre_processor_historical_data():
    """
    Récupération les données historiques, pré-processer pour pouvoir entraîner notre futur modèle.
    A l'aide de la fonction `pre_processor_historical_data`,nous récupérons 
    les données historiques pour les préparer à l'entraînement d'un modèle.
    
    Étapes principales :
    1. Crée un DataFrame à partir des données historiques en spécifiant les colonnes nécessaires.
    2. Convertit les colonnes de prix et de volume en type `float` pour assurer la cohérence des données numériques.
    3. Arrondit les valeurs des colonnes numériques à deux décimales pour uniformiser les données.
    4. Supprime les colonnes inutiles qui ne sont pas nécessaires pour le modèle, réduisant ainsi la taille des données et éliminant les informations redondantes.
    
    Retourne :
        Un DataFrame propre et prêt pour l'analyse ou l'entraînement du modèle.
    """
    data = data_historical

    df_historical_data = pd.DataFrame(data, columns=['OpenTime','OpenPrice','HighPrice', 'LowPrice','ClosePrice',
                                                     'Volume','CloseTime','AssetVolume','NumberOfTrades',
                                                     'BaseAssetVolume','QuoteAssetoVlume','field']) 
    
    # Nettoyage des données
    df_historical_data[['OpenPrice','HighPrice','LowPrice','ClosePrice','Volume']] = df_historical_data[['OpenPrice','HighPrice','LowPrice','ClosePrice','Volume']].astype(float)
    df_historical_data[['OpenPrice','HighPrice','LowPrice','ClosePrice','Volume']] = df_historical_data[['OpenPrice','HighPrice','LowPrice','ClosePrice','Volume']].round(2)
    
    # Suppression des colonnes non nécessaire à notre futur modèle de pré-traitement
    df_historical_data =  df_historical_data.drop(columns=['AssetVolume','NumberOfTrades',
                                                     'BaseAssetVolume','QuoteAssetoVlume','field'])
    
    return df_historical_data


collect = data_pre_processing()
print("\n")
print("\t\t\tDataFrame des données:\n")
print(collect,"\n")
print(collect.dtypes)
print(collect.isna())


historical = pre_processor_historical_data()
print("\n")
print("\t\t\tLes Données historiques:\n")
print(historical.head(10),"\n")
print(historical.dtypes)
print(historical.isna())